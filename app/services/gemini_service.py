"""
Backward-compat shim.

Earlier iterations used `gemini_service.py` to hold the chat orchestration.
The current implementation lives in `app.services.chat_service`.
"""

from app.services.chat_service import chat_service  # noqa: F401