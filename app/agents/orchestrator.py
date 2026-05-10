"""
Backward-compat shim.

Older code referenced `app.agents.orchestrator.BaseAgent`.
The new implementation lives in `app.agents.base_agent.BaseAgent`.
"""

from app.agents.base_agent import AgentReply, BaseAgent  # noqa: F401