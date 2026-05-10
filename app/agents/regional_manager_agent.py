from app.agents.base_agent import BaseAgent
from app.prompts.gucci_personas import REGIONAL_MANAGER_PROMPT


regional_manager_agent = BaseAgent(
    persona_id="gucci_regional_manager_eu",
    system_prompt=REGIONAL_MANAGER_PROMPT,
)