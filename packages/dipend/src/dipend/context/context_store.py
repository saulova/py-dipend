from typing import Any
from contextvars import ContextVar, Token
from ..__seedwork.dictionary import Dictionary


class ContextStore:
    def __init__(self):
        self._context_vars = Dictionary[str, ContextVar]()

    def set(self, var_name: str, value: Any):
        context_var = self._context_vars.get(var_name)

        if context_var is None:
            self._context_vars.set(var_name, ContextVar(var_name, default=None))

            context_var = self._context_vars.get(var_name)

        return context_var.set(value)

    def reset(self, var_name: str, context_token: Token):
        context_var = self._context_vars.get(var_name)

        if context_var is None:
            return

        context_var.reset(context_token)

    def get(self, var_name: str):
        context_var = self._context_vars.get(var_name)

        if context_var is None:
            return None

        return context_var.get()
