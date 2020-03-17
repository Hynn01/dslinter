"""Class which tests the DataFrameChecker."""
import astroid
import pylint.testutils

import dslinter


class TestDataFrameChecker(pylint.testutils.CheckerTestCase):
    """Class which tests the DataFrameChecker."""

    CHECKER_CLASS = dslinter.plugin.DataFrameChecker

    DF_INIT = """
    import pandas as pd
    df = pd.DataFrame()
    """

    def test_dataframe_call_assigned(self):
        """Test whether no message is added when a DataFrame operation is assigned."""
        module_tree = astroid.parse(self.DF_INIT + "a = df.abs()")
        assigned_call = module_tree.body[-1].value
        with self.assertNoMessages():
            self.checker.visit_module(module_tree)
            self.checker.visit_call(assigned_call)

    def test_other_call_not_assigned(self):
        """Test whether no message is added when an operation on another type is not assigned."""
        module_tree = astroid.parse(self.DF_INIT + "''.join([])")
        other_call = module_tree.body[-1].value
        with self.assertNoMessages():
            self.checker.visit_module(module_tree)
            self.checker.visit_call(other_call)

    def test_dataframe_call_not_assigned(self):
        """Test whether a message is added when a DataFrame operation is not assigned."""
        module_tree = astroid.parse(self.DF_INIT + "df.abs()")
        unassigned_call = module_tree.body[-1].value
        with self.assertAddsMessages(
            pylint.testutils.Message(msg_id="dataframe-lost", node=unassigned_call),
        ):
            self.checker.visit_module(module_tree)
            self.checker.visit_call(unassigned_call)

    def test_dataframe_call_assigned_double(self):
        """Test whether no message is added when two DataFrame operations are assigned."""
        module_tree = astroid.parse(self.DF_INIT + "a = df.abs().abs()")
        assigned_call = module_tree.body[-1].value
        second_call = assigned_call.func.expr
        with self.assertNoMessages():
            self.checker.visit_module(module_tree)
            self.checker.visit_call(assigned_call)
            self.checker.visit_call(second_call)

    def test_dataframe_call_not_assigned_double(self):
        """
        Test whether no message is added when two DataFrame operations are not assigned.

        This is the known false negative.
        """
        module_tree = astroid.parse(self.DF_INIT + "df.abs().abs()")
        unassigned_call = module_tree.body[-1].value
        second_call = unassigned_call.func.expr
        with self.assertNoMessages():
            self.checker.visit_module(module_tree)
            self.checker.visit_call(unassigned_call)
            self.checker.visit_call(second_call)

    def test_dataframe_two_calls_assigned_single_line(self):
        """No message should be added when two DataFrame operations are assigned on one line."""
        module_tree = astroid.parse(self.DF_INIT + "a = df.abs(); b = df.abs()")
        assigned_call_1 = module_tree.body[-2].value
        assigned_call_2 = module_tree.body[-1].value
        with self.assertNoMessages():
            self.checker.visit_module(module_tree)
            self.checker.visit_call(assigned_call_1)
            self.checker.visit_call(assigned_call_2)

    def test_dataframe_two_calls_not_assigned_single_line(self):
        """Two messages should be added when two DataFrame operations aren't assigned (one line)."""
        module_tree = astroid.parse(self.DF_INIT + "df.abs(); df.abs()")
        assigned_call_1 = module_tree.body[-2].value
        assigned_call_2 = module_tree.body[-1].value
        with self.assertAddsMessages(
            pylint.testutils.Message(msg_id="dataframe-lost", node=assigned_call_1),
            pylint.testutils.Message(msg_id="dataframe-lost", node=assigned_call_2),
        ):
            self.checker.visit_module(module_tree)
            self.checker.visit_call(assigned_call_1)
            self.checker.visit_call(assigned_call_2)

    def test_other_and_dataframe_not_assigned_single_line(self):  # noqa: D205, D400
        """
        Test whether a message is added when a DataFrame operation is not assigned on the same line
        as an operation on another type of object.
        """
        module_tree = astroid.parse(self.DF_INIT + "''.join([]); df.abs()")
        assigned_call_1 = module_tree.body[-2].value
        assigned_call_2 = module_tree.body[-1].value
        with self.assertAddsMessages(
            pylint.testutils.Message(msg_id="dataframe-lost", node=assigned_call_2),
        ):
            self.checker.visit_module(module_tree)
            self.checker.visit_call(assigned_call_1)
            self.checker.visit_call(assigned_call_2)

    def test_dataframe_not_assigned_and_other_single_line(self):  # noqa: D205, D400
        """
        Test whether a message is added when an operation on another type of object is done on the
        same line as an unassigned DataFrame operation.
        """
        module_tree = astroid.parse(self.DF_INIT + "df.abs(); ''.join([])")
        assigned_call_1 = module_tree.body[-2].value
        assigned_call_2 = module_tree.body[-1].value
        with self.assertAddsMessages(
            pylint.testutils.Message(msg_id="dataframe-lost", node=assigned_call_1),
        ):
            self.checker.visit_module(module_tree)
            self.checker.visit_call(assigned_call_1)
            self.checker.visit_call(assigned_call_2)
