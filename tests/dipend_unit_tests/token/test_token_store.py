import pytest
from dipend.exceptions.missing_dependency_token_exception import (
    MissingDependencyTokenException,
)
from dipend.token.token_store import (
    TokenStore,
)


class TestTokenStore:
    @pytest.fixture
    def store(self):
        return TokenStore()

    def test_retrieve_or_create_dependency_id_by_tokens_creates_new_registry(
        self, store
    ):
        token1 = "token1"
        token2 = "token2"

        result = store.retrieve_or_create_dependency_id_by_tokens([token1, token2])

        assert result is not None
        assert len(result.split("_")) == 2

    def test_retrieve_or_create_dependency_id_by_tokens_reuses_existing_registry(
        self, store
    ):
        token = "shared_token"
        id1 = store.retrieve_or_create_dependency_id_by_tokens([token])
        id2 = store.retrieve_or_create_dependency_id_by_tokens([token])

        assert id1 == id2

    def test_retrieve_or_create_dependency_id_by_tokens_handles_none_tokens(
        self, store
    ):
        token = "valid_token"
        result = store.retrieve_or_create_dependency_id_by_tokens([token, None])

        assert result is not None
        assert len(result.split("_")) == 1

    def test_get_tokens_returns_tokens_for_valid_dependency_id(self, store):
        token = "test_token"
        dependency_id = store.retrieve_or_create_dependency_id_by_tokens([token])

        tokens = store.get_tokens(dependency_id)

        assert tokens == [token]

    def test_get_tokens_raises_exception_for_invalid_dependency_id(self, store):
        with pytest.raises(MissingDependencyTokenException):
            store.get_tokens("invalid_id")

    def test_delete_token_removes_token_registry(self, store):
        token = "token_to_delete"
        dependency_id = store.retrieve_or_create_dependency_id_by_tokens([token])

        store.delete_token(token)

        with pytest.raises(MissingDependencyTokenException):
            store.get_tokens(dependency_id)

    def test_delete_token_with_non_existent_token(self, store):
        token = "non_existent_token"

        store.delete_token(token)

    def test_delete_token_with_none_type_token(self, store):
        token = None

        store.delete_token(token)

    def test_reset_clears_all_tokens(self, store):
        token1 = "token1"
        token2 = "token2"

        dependency_id = store.retrieve_or_create_dependency_id_by_tokens(
            [token1, token2]
        )

        store.reset()

        with pytest.raises(MissingDependencyTokenException):
            store.get_tokens(dependency_id)
