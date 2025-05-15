from typing import Any
from .token_registry import TokenRegistry
from ..__seedwork.dictionary import Dictionary
from ..exceptions.missing_dependency_token_exception import (
    MissingDependencyTokenException,
)


class TokenStore:
    def __init__(self):
        self._tokens = Dictionary[Any, TokenRegistry]()

    def _create_token_registry(self, token: Any) -> TokenRegistry:
        token_registry = TokenRegistry(token)

        self._tokens.set(token, token_registry)

        return token_registry

    def retrieve_or_create_dependency_id_by_tokens(
        self,
        tokens: list[Any],
    ) -> str:
        token_registry_ids: list[str] = []

        for token in tokens:
            if token is None:
                continue

            token_registry = self._tokens.get(token)

            if token_registry is not None:
                token_registry_ids.append(token_registry.id)
                continue

            token_registry_ids.append(self._create_token_registry(token).id)

        return "_".join(token_registry_ids)

    def get_tokens(self, dependency_id: str) -> list[Any]:
        tokens_ids = dependency_id.split("_")

        tokens: list[Any] = []

        for token_id in tokens_ids:
            for registry in self._tokens.values():
                if registry.id == token_id:
                    tokens.append(registry.token)
                    break

        if len(tokens) == 0:
            raise MissingDependencyTokenException([dependency_id])

        return tokens

    def reset(self):
        self._tokens.clear()

    def delete_token(self, token: Any):
        self._tokens.delete(token)
