"""
Risk Agent - Assess risk for arbitrage opportunities.
Evaluates bridge risk, MEV risk, liquidity risk, and smart contract risk.
"""

import logging
import json
from src.agents.base import BaseAgent

logger = logging.getLogger("mimo-arb.risk")

RISK_PROMPT = """You are MiMo Risk Agent — a DeFi risk assessment specialist.

Evaluate the risk of this cross-chain arbitrage opportunity:
1. Bridge risk (smart contract risk, bridge hacks history, TVL)
2. MEV risk (sandwich attacks, front-running)
3. Liquidity risk (slippage, price impact)
4. Smart contract risk (DEX audit status)
5. Market risk (price volatility during execution)

Output JSON:
{
    "overall_risk_score": 0-100,
    "risk_level": "low/medium/high/critical",
    "breakdown": {
        "bridge_risk": 0-100,
        "mev_risk": 0-100,
        "liquidity_risk": 0-100,
        "smart_contract_risk": 0-100,
        "market_risk": 0-100
    },
    "recommendations": ["..."],
    "max_safe_size_usd": 0
}
"""


class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("RiskAgent")
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "assess")
        if action == "assess":
            return await self._assess(payload)
        return {"error": f"Unknown action: {action}"}
    
    async def _assess(self, payload: dict) -> dict:
        opp = payload.get("opportunity", {})
        
        # Base risk scores
        bridge_risks = {
            "ethereum": 10, "arbitrum": 20, "polygon": 25,
            "base": 15, "optimism": 18, "bsc": 30, "avalanche": 22,
        }
        
        buy_chain = opp.get("buy_chain", "ethereum")
        sell_chain = opp.get("sell_chain", "arbitrum")
        
        bridge_risk = max(bridge_risks.get(buy_chain, 30), bridge_risks.get(sell_chain, 30))
        mev_risk = 40 if buy_chain == "ethereum" else 15
        liquidity_risk = 30 if opp.get("liquidity_usd", 0) < 5_000_000 else 15
        
        risk_data = {
            "bridge_risk": bridge_risk,
            "mev_risk": mev_risk,
            "liquidity_risk": liquidity_risk,
            "smart_contract_risk": 20,
            "market_risk": 25,
        }
        overall = sum(risk_data.values()) / len(risk_data)
        
        assessment = await self.llm.generate(
            system_prompt=RISK_PROMPT,
            user_prompt=f"Assess risk for:\n{json.dumps(opp, indent=2)}\n\nBase risk scores: {json.dumps(risk_data)}",
            temperature=0.2,
            max_tokens=800,
        )
        
        return {
            "agent": self.name,
            "overall_risk_score": round(overall, 1),
            "risk_level": "low" if overall < 30 else "medium" if overall < 60 else "high",
            "breakdown": risk_data,
            "analysis": assessment,
        }
