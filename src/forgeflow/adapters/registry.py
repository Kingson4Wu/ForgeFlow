from __future__ import annotations

from forgeflow.adapters.base import CLIAdapter

_registry: dict[str, type[CLIAdapter]] = {}


def register(name: str, adapter_cls: type[CLIAdapter]) -> None:
    """Register a CLI adapter class under the given name."""
    _registry[name.strip().lower()] = adapter_cls


def get_adapter(name: str) -> CLIAdapter:
    """Get an instance of the registered CLI adapter."""
    key = name.strip().lower()
    if not _registry:
        # Lazy-load built-in adapters (modules self-register on import)
        import forgeflow.adapters.claude_code  # noqa: F401
        import forgeflow.adapters.codex  # noqa: F401
        import forgeflow.adapters.gemini  # noqa: F401
    if key not in _registry:
        supported = ", ".join(sorted(_registry.keys()))
        raise ValueError(f"Unknown CLI type: {name}. Supported: {supported}")
    return _registry[key]()


def list_adapters() -> list[str]:
    """List all registered adapter names."""
    return list(_registry.keys())
