"""
Scanner Agent - Scan cross-chain prices and detect arbitrage opportunities.
"""

import logging
import json
from src.agents.base import BaseAgent
from src.core.price_feed import PriceFeed

logger = logging.getLogger("mimo-arb.scanner")

SCAN_PROMPT = """You are MiMo Scanner Agent — an expert at analyzing cross-chain arbitrage opportunities.

Given the following price data across chains and DEXes, identify the top arbitrage opportunities.

For each opportunity, explain:
1. The trade route (buy chain/DEX -> sell chain/DEX)
2. Why this spread exists (liquidity imbalance, chain congestion, etc.)
3. Risk factors (bridge time, slippage, MEV)
4. Recommended trade size

Output JSON:
{
    "opportunities": [
        {
            "route": "buy on X -> sell on Y",
            "token": "USDC",
            "spread_bps": 45,
            "explanation": "...",
            "risk_level": "low/medium/high",
            "recommended_action": "execute/monitor/skip"
        }
    ],
    "market_summary": "..."
}
"""


class ScannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("ScannerAgent")
        self.price_feed = PriceFeed()
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "scan")
        if action == "scan":
            return await self._scan(payload)
        elif action == "quotes":
            return self._get_quotes()
        return {"error": f"Unknown action: {action}"}
    
    async def _scan(self, payload: dict) -> dict:
        chains = payload.get("chains", ["ethereum", "arbitrum", "polygon", "base", "optimism"])
        tokens = payload.get("tokens", ["USDC", "USDT", "DAI", "WETH", "WBTC"])
        min_profit = payload.get("min_profit_bps", 30)
        
        opportunities = self.price_feed.find_arbitrage(tokens, chains, min_profit)
        
        opp_dicts = []
        for opp in opportunities:
            opp_dicts.append({
                "token": opp.token,
                "buy": f"{opp.buy_chain}/{opp.buy_dex} @ ${opp.buy_price:.6f}",
                "sell": f"{opp.sell_chain}/{opp.sell_dex} @ ${opp.sell_price:.6f}",
                "spread_bps": opp.spread_bps,
                "bridge_cost": opp.bridge_cost_usd,
                "gas_cost": opp.gas_cost_usd,
                "net_profit_bps": opp.net_profit_bps,
                "liquidity_usd": round(opp.liquidity_usd, 0),
            })
        
        # Get LLM analysis of top opportunities
        if opp_dicts:
            analysis = await self.llm.generate(
                system_prompt=SCAN_PROMPT,
                user_prompt=f"Analyze these arbitrage opportunities (trade size $10,000):\n{json.dumps(opp_dicts[:5], indent=2)}",
                temperature=0.3,
                max_tokens=1500,
            )
        else:
            analysis = "No profitable cross-chain arbitrage opportunities found at current prices."
        
        return {
            "agent": self.name,
            "opportunities": opp_dicts,
            "count": len(opp_dicts),
            "analysis": analysis,
            "chains_scanned": chains,
            "tokens_scanned": tokens,
        }
    
    def _get_quotes(self) -> dict:
        quotes = self.price_feed.get_all_quotes()
        return {
            "agent": self.name,
            "quotes": [
                {"token": q.token, "chain": q.chain, "dex": q.dex, "price": q.price}
                for q in quotes[:50]
            ],
        }
