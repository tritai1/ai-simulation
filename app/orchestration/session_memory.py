from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple

Role = Literal["user", "assistant"]


@dataclass
class Session:
    session_id: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    messages: List[Dict[str, str]] = field(default_factory=list)
    state: Dict[str, Any] = field(
        default_factory=lambda: {
            "module": 1,  # 1..3
            "annoyance": 0,  # grows if user is rude / loops
            "last_persona_id": None,
            "deliverables": {"module1": {}, "module2": {}, "module3": {}},
            "last_user_messages": [],
        }
    )


_SESSIONS: Dict[str, Session] = {}


def get_session(session_id: str) -> Session:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = Session(session_id=session_id)
    return _SESSIONS[session_id]


def save_message(session_id: str, role: Role, content: str) -> None:
    session = get_session(session_id)
    session.messages.append({"role": role, "content": content})
    if role == "user":
        last = session.state.get("last_user_messages", [])
        last.append(content)
        session.state["last_user_messages"] = last[-5:]


def update_state(session_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    session = get_session(session_id)
    session.state.update(patch)
    return session.state


def get_state(session_id: str) -> Dict[str, Any]:
    return get_session(session_id).state


def get_memory_context(session_id: str, max_turns: int = 10) -> str:
    session = get_session(session_id)
    recent = session.messages[-max_turns:]
    lines: List[str] = []
    lines.append(f"session_id: {session.session_id}")
    lines.append(f"module: {session.state.get('module')}")
    lines.append(f"annoyance: {session.state.get('annoyance')}")
    lines.append(f"last_persona_id: {session.state.get('last_persona_id')}")
    lines.append("")
    lines.append("recent_messages:")
    for m in recent:
        role = m["role"]
        content = m["content"]
        lines.append(f"- {role}: {content}")
    return "\n".join(lines).strip()


def detect_looping(session_id: str) -> bool:
    state = get_state(session_id)
    last = state.get("last_user_messages", [])
    if len(last) < 3:
        return False
    # naive loop signal: same message repeated or near-repeated
    a, b, c = (last[-1] or "").lower().strip(), (last[-2] or "").lower().strip(), (last[-3] or "").lower().strip()
    if a and (a == b or a == c):
        return True
    if len(a) > 40 and (a[:40] == b[:40] or a[:40] == c[:40]):
        return True
    return False