from app.agents.base_agent import BaseAgent
from app.prompts.gucci_personas import CEO_PROMPT


ceo_agent = BaseAgent(
    persona_id="gucci_ceo",
    system_prompt=CEO_PROMPT,
)