"""Checker which checkes whether random seed is set in pytorch"""
from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker
import astroid


class RandomnessControllingPytorchChecker(BaseChecker):
    """Checker which checks whether random seed is set in pytorch"""
    __implements__ = IAstroidChecker

    name = "randomness-control-pytorch"
    priority = -1
    msgs = {
        "W5573" : (
            "torch.manual_seed() is not set in pytorch program",
            "randomness-control-pytorch",
            "torch.manual_seed() should be set in pytorch program for reproducible result"
        )
    }
    options = ()

    _import_pytorch = False
    _has_manual_seed = False

    def visit_import(self, node: astroid.Import):
        """
        Check whether there is a pytorch import.
        :param node: import node
        """
        for name, _ in node.names:
            if name == "torch":
                self._import_pytorch = True

    def visit_call(self, node: astroid.Call):
        """
        Check whether there is a rule violation.
        :param node:
        """
        if(
            hasattr(node, "func")
            and hasattr(node.func, "attrname")
            and node.func.attrname == "manual_seed"
        ):
            self._has_manual_seed = True

        if(
            self._import_pytorch is True
            and self._has_manual_seed is False
        ):
            self.add_message("randomness-control-pytorch", node = node)

