"""Service package for app.analyzers and related helpers.

Keep this module minimal to avoid import-time side effects and circular
imports. Import submodules explicitly where needed (for example,
`from app.services import analyzers` will import the analyzers submodule
without requiring this file to import it at package initialization).
"""

__all__ = []
