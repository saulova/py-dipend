import pytest
from dipend.exceptions.decorator_exception import DecoratorException
from dipend.decorators.inject_mapped_dependency import (
    inject_mapped_dependency,
)


class TestInjectMappedDependency:
    def test_valid_class_decorator(self):
        class ValidClass:
            pass

        decorated_class = inject_mapped_dependency(0, ["token1", "token2"])(ValidClass)

        assert hasattr(decorated_class, "__di_mapped_dependency")
        assert getattr(decorated_class, "__di_mapped_dependency")[0] == [
            "token1",
            "token2",
        ]

    def test_invalid_decorator_on_non_class(self):
        with pytest.raises(DecoratorException, match="inject_mapped_dependency is a class decorator."):
            inject_mapped_dependency(0, ["token1"])(lambda x: x)

    def test_constructor_index_not_int(self):
        class ValidClass:
            pass

        with pytest.raises(DecoratorException, match="constructor_index must be an int."):
            inject_mapped_dependency("not-an-int", ["token1"])(ValidClass)

    def test_qualifier_tokens_not_list(self):
        class ValidClass:
            pass

        with pytest.raises(DecoratorException, match="qualifier_tokens must be a list."):
            inject_mapped_dependency(0, "not-a-list")(ValidClass)

    def test_applies_multiple_mapped_dependencies(self):
        class ValidClass:
            pass

        decorated_class = inject_mapped_dependency(0, ["token1"])(ValidClass)
        decorated_class = inject_mapped_dependency(1, ["token2"])(decorated_class)

        assert hasattr(decorated_class, "__di_mapped_dependency")
        assert getattr(decorated_class, "__di_mapped_dependency")[0] == ["token1"]
        assert getattr(decorated_class, "__di_mapped_dependency")[1] == ["token2"]

    def test_skip_builtin_classes(self):
        with pytest.raises(DecoratorException, match="inject_mapped_dependency is a class decorator."):
            inject_mapped_dependency(0, ["token"])(int)
