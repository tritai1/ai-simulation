from app.agents.base_agent import BaseAgent
from app.prompts.gucci_personas import CHRO_PROMPT


chro_agent = BaseAgent(persona_id="gucci_chro", system_prompt=CHRO_PROMPT)