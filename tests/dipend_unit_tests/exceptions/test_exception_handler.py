from unittest.mock import MagicMock
import pytest
from dipend.exceptions.exception_handler import ExceptionHandler
from dipend.exceptions.base_dependency_container_exception import (
    BaseDependencyContainerException,
)
from dipend.token.token_store import (
    TokenStore,
)
from dipend.token.token_type_resolver import (
    TokenTypeResolver,
)
from dipend.token.token_name_resolver import (
    TokenNameResolver,
)


class TestExceptionHandler:
    @pytest.fixture
    def mock_dependencies(self):
        return {
            "token_store": MagicMock(spec=TokenStore),
            "token_type": MagicMock(spec=TokenTypeResolver),
            "token_name": MagicMock(spec=TokenNameResolver),
        }

    @pytest.fixture
    def handler(self, mock_dependencies):
        """Returns an instance of ExceptionHandler with mocked dependencies."""
        return ExceptionHandler(
            token_store=mock_dependencies["token_store"],
            token_type=mock_dependencies["token_type"],
            dependency_token_name=mock_dependencies["token_name"],
        )

    def test_create_error_message(self, handler):
        message = handler._create_error_message("token_1", "An error occurred")
        assert message == "error: An error occurred - caused by: [token_1]"

    def test_get_token_names_success(self, handler, mock_dependencies):
        mock_dependencies["token_store"].get_tokens.side_effect = lambda dep_id: [
            f"token_{dep_id}_1",
            f"token_{dep_id}_2",
        ]
        mock_dependencies["token_type"].get_token_type.side_effect = lambda token: f"type_{token}"
        mock_dependencies["token_name"].get_token_name.side_effect = lambda token, token_type: f"name_{token}"

        result = handler._get_token_names(["dep_1", "dep_2"])

        expected = [
            "(name_token_dep_1_1 - name_token_dep_1_2)",
            "(name_token_dep_2_1 - name_token_dep_2_2)",
        ]

        assert result == expected

    def test_get_token_names_unknown_dependency(self, handler, mock_dependencies):
        mock_dependencies["token_store"].get_tokens.side_effect = BaseDependencyContainerException([], "")

        result = handler._get_token_names(["unknown_dep"])
        assert result == ["(unknown dependency id: unknown_dep)"]

    def test_handle_creates_and_raises_error(self, handler, mock_dependencies):
        """Test `handle` generates and raises an appropriate exception."""
        mock_dependencies["token_store"].get_tokens.side_effect = lambda dep_id: [f"token_{dep_id}_1"]
        mock_dependencies["token_type"].get_token_type.side_effect = lambda token: f"type_{token}"
        mock_dependencies["token_name"].get_token_name.side_effect = lambda token, token_type: f"name_{token}"

        input_exception = MagicMock(spec=BaseDependencyContainerException)
        input_exception.dependency_ids = ["dep_1"]
        input_exception.message = "Test exception message"

        with pytest.raises(
            Exception,
            match="error: Test exception message - caused by: \\[\\(name_token_dep_1_1\\)\\]",
        ):
            handler.handle(input_exception)
