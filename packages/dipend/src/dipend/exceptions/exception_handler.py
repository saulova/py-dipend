from ..__seedwork.handler_interface import HandlerInterface
from .base_dependency_container_exception import BaseDependencyContainerException
from ..token.token_store import TokenStore
from ..token.token_type_resolver import TokenTypeResolver
from ..token.token_name_resolver import TokenNameResolver


class ExceptionHandler(HandlerInterface[BaseDependencyContainerException, None]):
    def __init__(
        self,
        token_store: TokenStore,
        token_type: TokenTypeResolver,
        dependency_token_name: TokenNameResolver,
    ):
        self._token_store = token_store
        self._token_type = token_type
        self._token_name_resolver = dependency_token_name

    def _create_error_message(self, token_name: str, description: str):
        return f"error: {description} - caused by: [{token_name}]"

    def _get_token_names(self, dependency_ids: list[str]) -> list[str]:
        token_names: list[str] = []

        for dependency_id in dependency_ids:
            try:
                tokens = self._token_store.get_tokens(dependency_id)

                names: list[str] = []

                for token in tokens:
                    token_type = self._token_type.get_token_type(token)

                    dependency_token_name = self._token_name_resolver.get_token_name(
                        token,
                        token_type,
                    )

                    names.append(dependency_token_name)

                token_names.append(f"({" - ".join(names)})")
            except BaseDependencyContainerException:
                token_names.append(f"(unknown dependency id: {dependency_id})")

        return token_names

    def handle(self, input_data: BaseDependencyContainerException):
        token_names = self._get_token_names(input_data.dependency_ids)

        error = Exception(
            self._create_error_message(
                ", ".join(token_names), getattr(input_data, "message", str(input_data))
            ),
        )

        raise error
