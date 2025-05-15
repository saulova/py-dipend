import pytest
from dipend.context.context_store import ContextStore


class TestContextStore:
    @pytest.fixture
    def context_wrapper(self):
        return ContextStore()

    def test_set_and_get_var(self, context_wrapper):
        context_wrapper.set("test_var", "test_value")
        assert context_wrapper.get("test_var") == "test_value"

    def test_get_nonexistent_var(self, context_wrapper):
        assert context_wrapper.get("nonexistent_var") is None

    def test_set_updates_value(self, context_wrapper):
        context_wrapper.set("test_var", "initial_value")
        context_wrapper.set("test_var", "updated_value")
        assert context_wrapper.get("test_var") == "updated_value"

    def test_reset_var(self, context_wrapper):
        context_token = context_wrapper.set("test_var", "test_value")
        assert context_wrapper.get("test_var") == "test_value"

        context_wrapper.reset("test_var", context_token)
        assert context_wrapper.get("test_var") is None

    def test_reset_var_if_context_var_is_none(self, context_wrapper):
        context_token = context_wrapper.set("test_var", "test_value")
        context_wrapper._context_vars.set("test_var", None)
        context_wrapper.reset("test_var", context_token)
        assert context_wrapper.get("test_var") is None
