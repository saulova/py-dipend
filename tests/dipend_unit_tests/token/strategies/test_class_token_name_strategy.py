import pytest
from dipend.token.strategies.class_token_name_strategy import (
    ClassTokenNameStrategy,
)


class TestClassTokenNameStrategy:
    @pytest.fixture
    def strategy(self):
        return ClassTokenNameStrategy()

    def test_execute_returns_function_name(self, strategy):
        def sample_function():
            pass

        result = strategy.execute(sample_function)

        assert result == "sample_function"

    def test_execute_returns_class_name(self, strategy):
        class SampleClass:
            pass

        result = strategy.execute(SampleClass)

        assert result == "SampleClass"
