"""
Strategy Agent - Generate AI-powered arbitrage strategies.
Uses MiMo LLM to create adaptive trading strategies.
"""

import logging
import json
from src.agents.base import BaseAgent

logger = logging.getLogger("mimo-arb.strategy")

STRATEGY_PROMPT = """You are MiMo Strategy Agent — a DeFi arbitrage strategist.

Given the market conditions and parameters, generate an optimal arbitrage strategy:

1. Which tokens to focus on and why
2. Which chain pairs have the most opportunity
3. Optimal trade size and frequency
4. Risk management rules
5. When to enter and exit positions
6. Capital allocation across chains

Output a clear, actionable strategy with specific parameters.
"""


class StrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__("StrategyAgent")
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "generate")
        if action == "generate":
            return await self._generate(payload)
        return {"error": f"Unknown action: {action}"}
    
    async def _generate(self, payload: dict) -> dict:
        params = payload.get("params", {})
        capital = params.get("capital_usd", 100000)
        risk_tolerance = params.get("risk_tolerance", "medium")
        chains = params.get("chains", ["ethereum", "arbitrum", "polygon", "base"])
        
        strategy = await self.llm.generate(
            system_prompt=STRATEGY_PROMPT,
            user_prompt=f"Generate strategy for:\n"
                       f"Capital: ${capital:,.0f}\n"
                       f"Risk tolerance: {risk_tolerance}\n"
                       f"Chains: {', '.join(chains)}\n"
                       f"Preferred tokens: USDC, USDT, WETH, WBTC",
            temperature=0.5,
            max_tokens=2000,
        )
        
        return {
            "agent": self.name,
            "strategy": strategy,
            "parameters": {
                "capital_usd": capital,
                "risk_tolerance": risk_tolerance,
                "chains": chains,
            },
        }
