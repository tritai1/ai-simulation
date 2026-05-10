from __future__ import annotations

import time
import re
from typing import Dict, List

from app.agents.ceo_agent import ceo_agent
from app.agents.chro_agent import chro_agent
from app.agents.regional_manager_agent import regional_manager_agent
from app.core.llm import model
from app.orchestration.director import director
from app.orchestration.session_memory import (
    get_memory_context,
    save_message,
)
from app.services.report_service import export_module_pack


def _safe_retrieve_context(user_message: str) -> str:
    """
    Prototype-friendly: retrieval is optional.
    If FAISS index / artifacts are missing, return empty context.
    """
    try:
        from app.RAG.retriever import retrieve_context

        return retrieve_context(user_message)
    except Exception:
        return ""


class ChatService:
    def __init__(self) -> None:
        # When quota is exceeded, avoid hammering API for a short cooldown.
        self.quota_cooldown_until = 0.0

    def _quota_cooldown_active(self) -> bool:
        return time.time() < self.quota_cooldown_until

    def _activate_quota_cooldown(self, seconds: int = 90) -> None:
        self.quota_cooldown_until = time.time() + seconds

    def _remaining_quota_cooldown(self) -> int:
        return max(0, int(self.quota_cooldown_until - time.time()))

    def _fallback_response(self, module: int, user_message: str, reason: str) -> str:
        if "quota" in reason.lower():
            wait_s = self._remaining_quota_cooldown()
            wait_note = f"\n- Thu lai sau khoang `{wait_s}s`.\n" if wait_s > 0 else ""
            return f"""## Tiep tuc bai hoc (che do on dinh)

He thong dang gioi han muc goi AI trong it phut. De ban khong bi ngat, minh tra loi theo khung huan luyen.

## Huong dan cho Module {module}
- Viet lai yeu cau thanh 1-2 cau, co ket qua mong muon ro rang.
- Neu can quyet dinh: yeu cau output theo 4 phan: Roundtable / Decision / Next actions / Trade-offs.
- Uu tien prompt ngan, mot muc tieu moi lan gui.
{wait_note}

## Prompt goi y tiep theo
- `Module {module}. CEO: top 3 strategic constraints + 1 decision principle.`
- `Module {module}. CHRO: convert to practical framework with owners and milestones.`
- `Module {module}. Regional (Europe) Comms Manager: rollout risks and mitigations.`

## Câu hỏi của bạn
{user_message}
"""

        return f"""## He thong tam thoi gap loi mo hinh

Ly do: `{reason}`.

Ban co the gui lai voi prompt gon hon theo mau:
`Module {module}. CEO: Give 3 constraints, 1 principle, and one short decision.`
"""

    def _apply_safety_guardrails(self, text: str) -> str:
        """
        Enforce baseline in-sim safety:
        - Suggestions are drafts
        - Learner must confirm sources
        - Neutral phrasing / no wagering language
        """
        lowered = text.lower()
        blocked_terms = ["bet", "wager", "sure win", "guaranteed win", "all-in"]
        if any(t in lowered for t in blocked_terms):
            text = text + "\n\n> Note: Wagering-style language removed per simulation guardrails."

        safety_note = (
            "> Safety note: AI suggestions are drafts. Please confirm assumptions and sources "
            "before final submission."
        )
        if "safety note:" not in lowered:
            text = f"{text}\n\n{safety_note}"
        return text

    def _prompt_library(self) -> Dict[str, List[str]]:
        return {
            "headlines": [
                "Module 1: Define Group DNA without diluting brand identity",
                "Module 2: Design a 360 + coaching program that leaders will trust",
                "Module 3: Cascade adoption across regions with measurable impact",
            ],
            "disclaimers": [
                "This draft is for simulation learning and requires stakeholder validation.",
                "Use neutral language and verify data sources before implementation.",
                "Recommendations balance group standards with local brand autonomy.",
            ],
            "starter_prompts": [
                "Module 1. CEO: What are the 3 non-negotiables for Group DNA?",
                "Module 2. CHRO: Draft the 360 blueprint with privacy and anonymity rules.",
                "Module 3. Regional (Europe) Comms Manager: List rollout risks and mitigations.",
            ],
        }

    def _format_prompt_library(self) -> str:
        lib = self._prompt_library()
        return (
            "## Prompt Library\n\n"
            "### Headlines\n- " + "\n- ".join(lib["headlines"]) + "\n\n"
            "### Disclaimers\n- " + "\n- ".join(lib["disclaimers"]) + "\n\n"
            "### Starter prompts\n- " + "\n- ".join(lib["starter_prompts"])
        )

    def _kpi_calculator(self, payload: str) -> str:
        """
        Expected formats:
        /kpi completion=80 adoption=65 mobility=12 baseline_mobility=8
        """
        parts = payload.replace(",", " ").split()
        kv: Dict[str, float] = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                try:
                    kv[k.strip()] = float(v.strip())
                except ValueError:
                    pass

        completion = kv.get("completion", 0.0)
        adoption = kv.get("adoption", 0.0)
        mobility = kv.get("mobility", 0.0)
        baseline_mobility = kv.get("baseline_mobility", 0.0)

        leading_score = round((completion * 0.5 + adoption * 0.5), 2)
        lift = round(mobility - baseline_mobility, 2)
        lift_pct = round((lift / baseline_mobility * 100), 2) if baseline_mobility > 0 else 0.0

        return f"""## KPI Calculator

- Leading score: `{leading_score}`
- Mobility lift: `{lift}` points
- Mobility lift %: `{lift_pct}%`

### Interpretation
- If leading score < 70: strengthen enablement + manager sponsorship.
- If mobility lift <= 0: remove policy bottlenecks and improve cross-brand role visibility.
"""

    def _ab_simulator(self, payload: str) -> str:
        """
        Expected format:
        /ab a_rate=62 b_rate=71 sample_a=120 sample_b=115 metric=completion
        """
        parts = payload.replace(",", " ").split()
        kv: Dict[str, float] = {}
        metric = "primary_metric"
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                if k.strip() == "metric":
                    metric = v.strip()
                    continue
                try:
                    kv[k.strip()] = float(v.strip())
                except ValueError:
                    pass

        a_rate = kv.get("a_rate", 0.0)
        b_rate = kv.get("b_rate", 0.0)
        sample_a = kv.get("sample_a", 0.0)
        sample_b = kv.get("sample_b", 0.0)
        delta = round(b_rate - a_rate, 2)
        winner = "B" if delta > 0 else ("A" if delta < 0 else "Tie")

        confidence_hint = "Low confidence"
        if sample_a >= 100 and sample_b >= 100 and abs(delta) >= 5:
            confidence_hint = "Medium confidence"
        if sample_a >= 300 and sample_b >= 300 and abs(delta) >= 5:
            confidence_hint = "High confidence"

        return f"""## A/B Simulator

- Metric: `{metric}`
- Variant A: `{a_rate}%` (n={int(sample_a)})
- Variant B: `{b_rate}%` (n={int(sample_b)})
- Delta (B-A): `{delta}` points
- Suggested winner: `{winner}`
- Confidence hint: `{confidence_hint}`

### Recommendation
- Roll out winner gradually (pilot first), monitor lagging KPIs for 2-4 weeks.
"""

    def _reason_from_exception(self, exc: Exception) -> str:
        text = str(exc).lower()
        if "quota" in text or "429" in text or "resourceexhausted" in text:
            return "Gemini quota exceeded (429)"
        return "backend model error"

    def _extract_retry_seconds(self, exc: Exception) -> int:
        text = str(exc).lower()
        m = re.search(r"retry in\s+([0-9]+(?:\.[0-9]+)?)s", text)
        if m:
            return max(5, int(float(m.group(1))))
        m2 = re.search(r"retry_delay\s*\{\s*seconds:\s*([0-9]+)", text, flags=re.DOTALL)
        if m2:
            return max(5, int(m2.group(1)))
        return 15

    def _run_roundtable(self, session_id: str, user_message: str, memory_context: str, rag_context: str) -> str:
        """
        Module 1-2 collaborative mode with a single model call (cost-saving).
        """
        synthesis_prompt = f"""
You are simulating a roundtable with 3 AI co-workers in one response:
- CEO (strategy + brand DNA)
- CHRO (framework + people process)
- Regional Manager EU (rollout reality + change risks)

User ask:
{user_message}

Conversation memory:
{memory_context}

Knowledge:
{rag_context}

Return markdown with EXACT sections:
1) ## Co-worker Roundtable
- 2-4 bullets each for CEO / CHRO / Regional
2) ## Decision
- one clear decision and why
3) ## What learner should do next
- 3 concrete next actions aligned to current module
4) ## Trade-offs
- at least 2 trade-offs considered
""".strip()
        synthesis = model.generate_content(synthesis_prompt)
        return getattr(synthesis, "text", None) or str(synthesis)

    def process_message(self, session_id: str, user_message: str) -> str:
        msg = (user_message or "").strip()
        try:
            if msg.lower().startswith("/promptlib"):
                response = self._format_prompt_library()
                response = self._apply_safety_guardrails(response)
                save_message(session_id, "user", user_message)
                save_message(session_id, "assistant", response)
                return response

            if msg.lower().startswith("/kpi"):
                payload = msg[4:].strip()
                response = self._kpi_calculator(payload)
                response = self._apply_safety_guardrails(response)
                save_message(session_id, "user", user_message)
                save_message(session_id, "assistant", response)
                return response

            if msg.lower().startswith("/ab"):
                payload = msg[3:].strip()
                response = self._ab_simulator(payload)
                response = self._apply_safety_guardrails(response)
                save_message(session_id, "user", user_message)
                save_message(session_id, "assistant", response)
                return response

            if msg.lower().startswith("/export"):
                # Usage: /export 1  | /export module 2
                parts = msg.lower().replace("module", "").split()
                module = 1
                for p in parts[1:]:
                    if p.isdigit():
                        module = int(p)
                        break
                files = export_module_pack(session_id=session_id, module=module)
                return "Exported:\n" + "\n".join([f"- {k}: {v}" for k, v in files.items()])

            memory_context = get_memory_context(session_id)
            rag_context = _safe_retrieve_context(user_message)
            _agent_preview, hint, state = director.route(session_id=session_id, user_message=user_message)
            module = int(state.get("module", 1) or 1)

            if self._quota_cooldown_active():
                fallback = self._fallback_response(
                    module=module,
                    user_message=user_message,
                    reason="Gemini quota cooldown active",
                )
                save_message(session_id, "user", user_message)
                save_message(session_id, "assistant", fallback)
                return fallback

            # For Module 1-2, use collaborative "AI co-workers talk to each other" mode by default.
            # User can bypass with "/solo ..." if they want a single persona response.
            if module in (1, 2) and not msg.lower().startswith("/solo"):
                save_message(session_id, "user", user_message)
                response = self._run_roundtable(
                    session_id=session_id,
                    user_message=user_message,
                    memory_context=memory_context,
                    rag_context=rag_context,
                )
                guarded = self._apply_safety_guardrails(response)
                save_message(session_id, "assistant", guarded)
                return guarded

            agent = _agent_preview

            reply = agent.chat(
                user_message=user_message,
                memory_context=memory_context,
                rag_context=rag_context,
                director_hint=hint,
            )

            save_message(session_id, "user", user_message)
            guarded = self._apply_safety_guardrails(reply.message)
            save_message(session_id, "assistant", guarded)
            return guarded
        except Exception as exc:
            _agent_preview, _hint, state = director.route(session_id=session_id, user_message=user_message)
            module = int(state.get("module", 1) or 1)
            reason = self._reason_from_exception(exc)
            if "quota" in reason.lower():
                self._activate_quota_cooldown(seconds=self._extract_retry_seconds(exc))
            fallback = self._fallback_response(module=module, user_message=user_message, reason=reason)
            fallback = self._apply_safety_guardrails(fallback)
            save_message(session_id, "user", user_message)
            save_message(session_id, "assistant", fallback)
            return fallback


chat_service = ChatService()

