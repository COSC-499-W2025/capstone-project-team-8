"""app.views package

Keep this __init__ minimal to avoid import-time side effects and circular
imports when Django imports URL modules. Import submodules explicitly where
needed (for example, in app/urls.py import from app.views.uploadFolderView).
"""

__all__ = []
