from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from app.orchestration.router import select_agent
from app.orchestration.session_memory import detect_looping, get_state, update_state
from app.prompts.gucci_personas import DIRECTOR_SUPERVISOR_PROMPT


def _maybe_set_module_from_user_text(user_message: str, state: Dict[str, Any]) -> Dict[str, Any]:
    msg = (user_message or "").lower()
    if "module 1" in msg or "mod 1" in msg or "m1" in msg:
        state["module"] = 1
    elif "module 2" in msg or "mod 2" in msg or "m2" in msg:
        state["module"] = 2
    elif "module 3" in msg or "mod 3" in msg or "m3" in msg:
        state["module"] = 3
    return state


def _hint_for_module(module: int) -> str:
    if module == 1:
        return (
            "- What is the core tension (brand autonomy vs group mobility/pipeline) in 1–2 sentences?\n"
            "- Draft the 4-theme matrix (Vision/Entrepreneurship/Passion/Trust) across 3 levels with 2–3 behaviors each.\n"
            "- Map 3–4 use cases: recruitment, appraisal, development, mobility."
        )
    if module == 2:
        return (
            "- Lock instrument blueprint: rater groups, scale, anonymity rules, languages.\n"
            "- Define participant + rater journey: comms, deadlines, consent, privacy.\n"
            "- Coaching: coach profile + cadence + goals-to-habits plan; decide build vs buy."
        )
    if module == 3:
        return (
            "- Identify regional trainer profile and constraints (time, languages, brand tone).\n"
            "- Train-the-trainer rollout: workshops + RACI + checklist.\n"
            "- KPIs: leading (completion, NPS) and lagging (mobility, bench strength) + reporting cadence."
        )
    return "- Clarify which module you are working on (Module 1/2/3)."


class Director:
    """
    Supervisor layer:
    - Tracks module state per session.
    - Routes to the best persona.
    - When user loops, injects a subtle hint (questions-first) into the next agent reply.
    """

    supervisor_prompt = DIRECTOR_SUPERVISOR_PROMPT

    def route(self, session_id: str, user_message: str) -> Tuple[object, Optional[str], Dict[str, Any]]:
        state = get_state(session_id)
        state = _maybe_set_module_from_user_text(user_message, state)
        update_state(session_id, state)

        agent = select_agent(user_message, state)

        hint: Optional[str] = None
        if detect_looping(session_id):
            hint = _hint_for_module(int(state.get("module", 1)))
            annoyance = int(state.get("annoyance", 0) or 0)
            update_state(session_id, {"annoyance": min(annoyance + 1, 5)})

        return agent, hint, get_state(session_id)


director = Director()