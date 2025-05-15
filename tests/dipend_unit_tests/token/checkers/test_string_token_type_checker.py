import pytest
from dipend.token.checkers.string_token_type_checker import (
    StringTokenTypeChecker,
)


class TestStringTokenTypeChecker:
    @pytest.fixture
    def strategy(self):
        return StringTokenTypeChecker()

    def test_execute_returns_true_for_string(self, strategy):
        input_data = "This is a string"

        result = strategy.execute(input_data)

        assert result is True

    def test_execute_returns_false_for_non_string(self, strategy):
        input_data = 12345

        result = strategy.execute(input_data)

        assert result is False

    def test_execute_returns_false_for_none(self, strategy):
        input_data = None

        result = strategy.execute(input_data)

        assert result is False

    def test_execute_returns_true_for_empty_string(self, strategy):
        input_data = ""

        result = strategy.execute(input_data)

        assert result is True
