from unittest.mock import MagicMock
import pytest
from dipend.enums.token_type_enum import TokenTypeEnum
from dipend.token.strategies.class_token_name_strategy import (
    ClassTokenNameStrategy,
)
from dipend.token.strategies.string_token_name_strategy import (
    StringTokenNameStrategy,
)
from dipend.token.token_name_resolver import (
    TokenNameResolver,
)


class TestTokenNameResolver:
    @pytest.fixture
    def dependency_token_name(self):
        dependency_token_name = TokenNameResolver()
        dependency_token_name.set_default_token_name_strategies()
        return dependency_token_name

    def test_set_default_token_name_strategies(self, dependency_token_name):
        assert isinstance(
            dependency_token_name._strategies.get(TokenTypeEnum.CLASS_CONSTRUCTOR),
            ClassTokenNameStrategy,
        )
        assert isinstance(
            dependency_token_name._strategies.get(TokenTypeEnum.STRING),
            StringTokenNameStrategy,
        )

    def test_set_token_name_strategy(self, dependency_token_name):
        mock_strategy = MagicMock()
        dependency_token_name.set_token_name_strategy("CUSTOM", mock_strategy)

        assert dependency_token_name._strategies.get("CUSTOM") == mock_strategy

    def test_get_token_name_with_class_constructor_strategy(self, dependency_token_name):
        class SampleClass:
            pass

        result = dependency_token_name.get_token_name(SampleClass, TokenTypeEnum.CLASS_CONSTRUCTOR)

        assert result == "SampleClass"

    def test_get_token_name_with_string_strategy(self, dependency_token_name):
        result = dependency_token_name.get_token_name("SampleString", TokenTypeEnum.STRING)

        assert result == "SampleString"

    def test_get_token_name_with_unknown_token_type(self, dependency_token_name):
        result = dependency_token_name.get_token_name("SampleToken", "UNKNOWN_TYPE")

        assert result == "UNKNOWN"
