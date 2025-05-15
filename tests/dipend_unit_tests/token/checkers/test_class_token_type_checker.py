import pytest
from dipend.token.checkers.class_token_type_checker import (
    ClassTokenTypeChecker,
)


class TestClassTokenTypeChecker:
    @pytest.fixture
    def strategy(self):
        return ClassTokenTypeChecker()

    def test_execute_returns_true_for_valid_class(self, strategy):
        class SampleClass:
            pass

        result = strategy.execute(SampleClass)

        assert result is True

    def test_execute_returns_false_for_instance(self, strategy):
        class SampleClass:
            pass

        instance = SampleClass()
        result = strategy.execute(instance)

        assert result is False

    def test_execute_returns_false_for_non_class_type(self, strategy):
        non_class_input = "NotAClass"

        result = strategy.execute(non_class_input)

        assert result is False

    def test_execute_returns_false_for_built_in_types(self, strategy):
        result = strategy.execute(int)

        assert result is False
