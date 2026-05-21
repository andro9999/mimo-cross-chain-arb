"""
Monitor Agent - Real-time price monitoring and alerts.
Tracks price movements and triggers alerts for opportunities.
"""

import logging
from src.agents.base import BaseAgent
from src.core.price_feed import PriceFeed

logger = logging.getLogger("mimo-arb.monitor")


class MonitorAgent(BaseAgent):
    def __init__(self):
        super().__init__("MonitorAgent")
        self.price_feed = PriceFeed()
    
    async def execute(self, payload: dict) -> dict:
        action = payload.get("action", "prices")
        if action == "prices":
            return self._get_prices()
        elif action == "alerts":
            return self._check_alerts()
        return {"error": f"Unknown action: {action}"}
    
    def _get_prices(self) -> dict:
        matrix = self.price_feed.get_price_matrix()
        return {
            "agent": self.name,
            "price_matrix": matrix,
            "chains": list(matrix.get("USDC", {}).keys()),
            "tokens": list(matrix.keys()),
        }
    
    def _check_alerts(self) -> dict:
        opportunities = self.price_feed.find_arbitrage(min_profit_bps=50)
        return {
            "agent": self.name,
            "alerts": [
                {
                    "token": opp.token,
                    "route": f"{opp.buy_chain} -> {opp.sell_chain}",
                    "spread_bps": opp.spread_bps,
                    "net_profit_bps": opp.net_profit_bps,
                }
                for opp in opportunities[:5]
            ],
            "count": len(opportunities),
        }
