from unittest.mock import MagicMock
import pytest
from dipend.enums.token_type_enum import TokenTypeEnum
from dipend.token.checkers.class_token_type_checker import (
    ClassTokenTypeChecker,
)
from dipend.token.checkers.string_token_type_checker import (
    StringTokenTypeChecker,
)
from dipend.token.token_type_resolver import (
    TokenTypeResolver,
)


class TestTokenType:
    @pytest.fixture(scope="function")
    def token_type(self):
        token_type = TokenTypeResolver()
        token_type.set_default_token_type_checkers()
        return token_type

    def test_set_default_token_type_checkers(self, token_type):
        assert isinstance(
            token_type._checkers.get(TokenTypeEnum.CLASS_CONSTRUCTOR),
            ClassTokenTypeChecker,
        )
        assert isinstance(
            token_type._checkers.get(TokenTypeEnum.STRING),
            StringTokenTypeChecker,
        )

    def test_set_token_type_checker(self, token_type):
        mock_checker = MagicMock()
        token_type.set_token_type_checker("CUSTOM", mock_checker)

        assert token_type._checkers.get("CUSTOM") == mock_checker

    def test_get_token_type_for_class_constructor(self, token_type):
        class SampleClass:
            pass

        result = token_type.get_token_type(SampleClass)

        assert result == TokenTypeEnum.CLASS_CONSTRUCTOR

    def test_get_token_type_for_string(self, token_type):
        result = token_type.get_token_type("SampleString")

        assert result == TokenTypeEnum.STRING

    def test_get_token_type_for_unknown_type(self, token_type):
        result = token_type.get_token_type(12345)

        assert result == "UNKNOWN"
