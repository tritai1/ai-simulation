from __future__ import annotations

from typing import Dict

from app.agents.ceo_agent import ceo_agent
from app.agents.chro_agent import chro_agent
from app.agents.regional_manager_agent import regional_manager_agent


def select_agent(user_message: str, state: Dict) -> object:
    """
    Lightweight routing:
    - Uses current module state first (so the learner stays on track).
    - Allows explicit overrides if user addresses a persona directly.
    """
    message = (user_message or "").lower()

    if any(k in message for k in ["ceo", "chief executive", "group ceo"]):
        return ceo_agent
    if any(k in message for k in ["chro", "hr", "human resources"]):
        return chro_agent
    if any(k in message for k in ["regional", "europe", "comms", "communications", "employer branding"]):
        return regional_manager_agent

    module = int(state.get("module", 1) or 1)
    if module == 1:
        # Module 1 often alternates CEO (DNA) and CHRO (competencies)
        if any(k in message for k in ["competency", "framework", "vision", "entrepreneurship", "passion", "trust"]):
            return chro_agent
        return ceo_agent
    if module == 2:
        return chro_agent
    if module == 3:
        return regional_manager_agent
    return chro_agent