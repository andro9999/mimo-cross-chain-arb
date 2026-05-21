"""
Analyzer Agent - Deep analysis of arbitrage opportunities.
Calculates profitability, costs, and optimal trade sizing.
"""

import logging
import json
from src.agents.base import BaseAgent

logger = logging.getLogger("mimo-arb.analyzer")

ANALYSIS_PROMPT = """You are MiMo Analyzer Agent — a quantitative arbitrage analyst.

Perform deep analysis on the given arbitrage opportunity:
1. Break down all costs (gas, bridge fees, DEX fees, slippage)
2. Calculate net profit after all costs
3. Estimate execution time (bridge confirmation times)
4. Risk assessment (MEV risk, bridge risk, price movement risk)
5. Optimal trade size recommendation
6. Whether to execute or skip

Output JSON:
{
    "verdict": "execute/skip/monitor",
    "confidence": 0.0-1.0,
    "net_profit_usd": 0.00,
    "total_cost_usd": 0.00,
    "execution_time_seconds": 0,
    "risk_score": 0-100,
    "optimal_size_usd": 0,
    "reasoning": "..."
}
"""


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("AnalyzerAgent")
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "analyze")
        if action == "analyze":
            return await self._analyze(payload)
        return {"error": f"Unknown action: {action}"}
    
    async def _analyze(self, payload: dict) -> dict:
        opp = payload.get("opportunity", {})
        
        # Calculate detailed costs
        trade_size = opp.get("trade_size_usd", 10000)
        spread_bps = opp.get("spread_bps", 0)
        bridge_cost = opp.get("bridge_cost", 5.0)
        gas_cost = opp.get("gas_cost", 3.0)
        dex_fee_pct = 0.3  # 0.3% typical DEX fee
        
        gross_profit = trade_size * (spread_bps / 10000)
        dex_fees = trade_size * (dex_fee_pct / 100) * 2  # Both legs
        slippage = trade_size * 0.001  # 10 bps slippage estimate
        total_cost = bridge_cost + gas_cost + dex_fees + slippage
        net_profit = gross_profit - total_cost
        net_profit_bps = (net_profit / trade_size) * 10000 if trade_size > 0 else 0
        
        cost_breakdown = {
            "trade_size_usd": trade_size,
            "spread_bps": spread_bps,
            "gross_profit_usd": round(gross_profit, 2),
            "bridge_cost_usd": round(bridge_cost, 2),
            "gas_cost_usd": round(gas_cost, 2),
            "dex_fees_usd": round(dex_fees, 2),
            "slippage_usd": round(slippage, 2),
            "total_cost_usd": round(total_cost, 2),
            "net_profit_usd": round(net_profit, 2),
            "net_profit_bps": round(net_profit_bps, 2),
        }
        
        # Get LLM verdict
        analysis = await self.llm.generate(
            system_prompt=ANALYSIS_PROMPT,
            user_prompt=f"Analyze this arbitrage:\n{json.dumps(cost_breakdown, indent=2)}\n\nOpportunity details:\n{json.dumps(opp, indent=2)}",
            temperature=0.2,
            max_tokens=1000,
        )
        
        return {
            "agent": self.name,
            "cost_breakdown": cost_breakdown,
            "verdict": "execute" if net_profit > 0 else "skip",
            "analysis": analysis,
        }
