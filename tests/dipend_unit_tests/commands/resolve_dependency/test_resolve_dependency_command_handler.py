from unittest.mock import MagicMock
import pytest
from dipend.token.token_store import (
    TokenStore,
)
from dipend.dependency.dependency_resolver import (
    DependencyResolver,
)
from dipend.commands.resolve_dependency_command import (
    ResolveDependencyCommand,
)
from dipend.commands.resolve_dependency_command_handler import (
    ResolveDependencyCommandHandler,
)


class TestResolveDependencyCommandHandler:
    @pytest.fixture
    def setup_handler(self):
        token_store = MagicMock(TokenStore)
        dependency_resolver = MagicMock(DependencyResolver)

        handler = ResolveDependencyCommandHandler(
            token_store,
            dependency_resolver,
        )

        return handler, token_store, dependency_resolver

    def test_handle_resolves_dependency(self, setup_handler):
        handler, token_store, dependency_resolver = setup_handler

        command = ResolveDependencyCommand(tokens=["token1"])

        token_store.retrieve_or_create_dependency_id_by_tokens.return_value = "dependency_id"
        dependency_resolver.resolve.return_value = "resolved_instance"

        result = handler.handle(command)

        token_store.retrieve_or_create_dependency_id_by_tokens.assert_called_once_with(command.tokens)
        dependency_resolver.resolve.assert_called_once()

        assert result == "resolved_instance"
