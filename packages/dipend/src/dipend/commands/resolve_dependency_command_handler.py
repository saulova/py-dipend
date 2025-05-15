from typing import Any
from ..__seedwork.handler_interface import HandlerInterface
from ..token.token_store import TokenStore
from ..dependency.dependency_resolver import DependencyResolver
from .resolve_dependency_command import (
    ResolveDependencyCommand,
)


class ResolveDependencyCommandHandler(HandlerInterface[ResolveDependencyCommand, Any]):
    def __init__(
        self,
        token_store: TokenStore,
        dependency_resolver: DependencyResolver,
    ):
        self._token_store = token_store
        self._dependency_resolver = dependency_resolver

    def handle(
        self,
        input_data: ResolveDependencyCommand,
    ) -> Any:
        dependency_id = self._token_store.retrieve_or_create_dependency_id_by_tokens(input_data.tokens)

        dependency_instance = self._dependency_resolver.resolve(dependency_id)

        return dependency_instance
