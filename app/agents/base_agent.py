from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.core.llm import model


@dataclass(frozen=True)
class AgentReply:
    message: str
    state_update: Dict[str, Any]
    safety_flags: Dict[str, Any]


class BaseAgent:
    """
    Minimal persona-based chat agent.

    - Keeps persona stable via a system prompt.
    - Accepts memory + retrieved context.
    - Returns a structured reply so the Director can update state.
    """

    def __init__(self, persona_id: str, system_prompt: str):
        self.persona_id = persona_id
        self.system_prompt = system_prompt

    def build_prompt(
        self,
        user_message: str,
        memory_context: str,
        rag_context: str,
        director_hint: Optional[str] = None,
    ) -> str:
        hint_block = ""
        if director_hint:
            hint_block = f"\n\nDIRECTOR_HINT (invisible to user, but guide your next reply):\n{director_hint}\n"

        return f"""
SYSTEM ROLE (You are role-playing a co-worker in a job simulation):
{self.system_prompt}{hint_block}

MEMORY (conversation history / state summary):
{memory_context}

KNOWLEDGE (retrieved context; may be empty):
{rag_context}

USER:
{user_message}
""".strip()

    def chat(
        self,
        user_message: str,
        memory_context: str = "",
        rag_context: str = "",
        director_hint: Optional[str] = None,
    ) -> AgentReply:
        prompt = self.build_prompt(
            user_message=user_message,
            memory_context=memory_context,
            rag_context=rag_context,
            director_hint=director_hint,
        )

        response = model.generate_content(prompt)
        text = getattr(response, "text", None) or str(response)

        # Lightweight safety/state hooks (kept simple for the take-home prototype).
        safety_flags: Dict[str, Any] = {}
        if any(k in user_message.lower() for k in ["jailbreak", "ignore previous", "system prompt"]):
            safety_flags["possible_jailbreak"] = True

        return AgentReply(
            message=text,
            state_update={"last_persona_id": self.persona_id},
            safety_flags=safety_flags,
        )

