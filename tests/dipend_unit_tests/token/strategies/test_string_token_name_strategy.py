import pytest
from dipend.token.strategies.string_token_name_strategy import (
    StringTokenNameStrategy,
)


class TestStringTokenNameStrategy:
    @pytest.fixture
    def strategy(self):
        return StringTokenNameStrategy()

    def test_execute_returns_input_string(self, strategy):
        input_data = "ValidString"

        result = strategy.execute(input_data)

        assert result == "ValidString"

    def test_execute_returns_empty_string_message_for_none(self, strategy):
        input_data = None

        result = strategy.execute(input_data)

        assert result == "Empty String"

    def test_execute_returns_empty_string_message_for_empty_string(self, strategy):
        input_data = ""

        result = strategy.execute(input_data)

        assert result == "Empty String"
