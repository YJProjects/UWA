"""Firebase Authentication package exports."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .fireauth import FireAuth

__all__ = ["FireAuth"]


def __getattr__(name: str) -> Any:
    if name == "FireAuth":
        from .fireauth import FireAuth

        return FireAuth

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
