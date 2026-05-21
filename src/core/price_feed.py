"""
Cross-Chain Price Feed - Simulated DEX price data for multiple chains.
In production, this would connect to real DEX APIs (Uniswap, SushiSwap, etc.)
"""

import random
import logging
from typing import Dict, List
from dataclasses import dataclass, field

logger = logging.getLogger("mimo-arb.price_feed")

# Supported DEXes per chain
CHAIN_DEXES = {
    "ethereum": ["Uniswap V3", "SushiSwap", "Curve", "Balancer"],
    "arbitrum": ["Uniswap V3", "SushiSwap", "Camelot", "GMX"],
    "polygon": ["Uniswap V3", "QuickSwap", "SushiSwap", "Curve"],
    "base": ["Uniswap V3", "BaseSwap", "Aerodrome"],
    "optimism": ["Uniswap V3", "Velodrome", "SushiSwap"],
    "bsc": ["PancakeSwap", "BiSwap", "ApeSwap"],
    "avalanche": ["Trader Joe", "Pangolin", "Platypus"],
}

# Base prices (USD)
BASE_PRICES = {
    "USDC": 1.0001,
    "USDT": 0.9999,
    "DAI": 1.0002,
    "WETH": 3842.50,
    "WBTC": 107250.00,
    "ARB": 0.48,
    "MATIC": 0.22,
    "OP": 0.72,
    "LINK": 13.85,
    "UNI": 6.42,
}


@dataclass
class PriceQuote:
    token: str
    chain: str
    dex: str
    price: float
    liquidity_usd: float
    price_impact_pct: float


@dataclass
class ArbitrageOpportunity:
    token: str
    buy_chain: str
    buy_dex: str
    buy_price: float
    sell_chain: str
    sell_dex: str
    sell_price: float
    spread_bps: float
    estimated_profit_bps: float
    liquidity_usd: float
    bridge_cost_usd: float
    gas_cost_usd: float
    net_profit_bps: float
    timestamp: str


class PriceFeed:
    """
    Cross-chain price feed with realistic price variations.
    Simulates price differences across chains that create arbitrage opportunities.
    """
    
    def __init__(self):
        self._prices: Dict[str, Dict[str, Dict[str, float]]] = {}
        self._initialize_prices()
    
    def _initialize_prices(self):
        """Initialize prices with slight variations across chains."""
        for token, base_price in BASE_PRICES.items():
            self._prices[token] = {}
            for chain, dexes in CHAIN_DEXES.items():
                self._prices[token][chain] = {}
                for dex in dexes:
                    # Add realistic variation: 0-30 bps deviation
                    variation = random.uniform(-0.003, 0.003)
                    self._prices[token][chain][dex] = base_price * (1 + variation)
    
    def get_all_quotes(self) -> List[PriceQuote]:
        """Get current price quotes across all chains and DEXes."""
        quotes = []
        for token, chains in self._prices.items():
            for chain, dexes in chains.items():
                for dex, price in dexes.items():
                    liquidity = random.uniform(500_000, 50_000_000)
                    impact = random.uniform(0.01, 0.5)
                    quotes.append(PriceQuote(
                        token=token, chain=chain, dex=dex,
                        price=price, liquidity_usd=liquidity,
                        price_impact_pct=impact,
                    ))
        return quotes
    
    def update_prices(self):
        """Simulate price movement."""
        for token, chains in self._prices.items():
            base = BASE_PRICES.get(token, 1.0)
            for chain, dexes in chains.items():
                for dex in dexes:
                    # Random walk with mean reversion
                    current = self._prices[token][chain][dex]
                    drift = (base - current) / base * 0.1
                    noise = random.gauss(0, 0.001)
                    new_price = current * (1 + drift + noise)
                    self._prices[token][chain][dex] = new_price
    
    def find_arbitrage(
        self,
        tokens: List[str] = None,
        chains: List[str] = None,
        min_profit_bps: float = 30,
    ) -> List[ArbitrageOpportunity]:
        """Find arbitrage opportunities across chains."""
        self.update_prices()
        
        if tokens is None:
            tokens = list(BASE_PRICES.keys())
        if chains is None:
            chains = list(CHAIN_DEXES.keys())
        
        opportunities = []
        
        for token in tokens:
            if token not in self._prices:
                continue
            
            # Collect all prices for this token
            all_prices = []
            for chain in chains:
                if chain not in self._prices[token]:
                    continue
                for dex, price in self._prices[token][chain].items():
                    all_prices.append((chain, dex, price))
            
            # Find best buy (lowest) and best sell (highest) across different chains
            for buy_chain, buy_dex, buy_price in all_prices:
                for sell_chain, sell_dex, sell_price in all_prices:
                    if buy_chain == sell_chain:
                        continue  # Cross-chain only
                    
                    spread_bps = ((sell_price - buy_price) / buy_price) * 10000
                    
                    if spread_bps < min_profit_bps:
                        continue
                    
                    # Estimate costs
                    bridge_cost = self._estimate_bridge_cost(token, buy_chain, sell_chain)
                    gas_cost = self._estimate_gas_cost(buy_chain, sell_chain)
                    
                    trade_size = 10000  # $10K trade
                    gross_profit = trade_size * (spread_bps / 10000)
                    net_profit = gross_profit - bridge_cost - gas_cost
                    net_profit_bps = (net_profit / trade_size) * 10000
                    
                    if net_profit_bps > 0:
                        from datetime import datetime
                        opportunities.append(ArbitrageOpportunity(
                            token=token,
                            buy_chain=buy_chain, buy_dex=buy_dex, buy_price=buy_price,
                            sell_chain=sell_chain, sell_dex=sell_dex, sell_price=sell_price,
                            spread_bps=round(spread_bps, 2),
                            estimated_profit_bps=round(spread_bps, 2),
                            liquidity_usd=random.uniform(1_000_000, 50_000_000),
                            bridge_cost_usd=round(bridge_cost, 2),
                            gas_cost_usd=round(gas_cost, 2),
                            net_profit_bps=round(net_profit_bps, 2),
                            timestamp=datetime.utcnow().isoformat(),
                        ))
        
        opportunities.sort(key=lambda x: x.net_profit_bps, reverse=True)
        return opportunities[:20]
    
    def _estimate_bridge_cost(self, token: str, from_chain: str, to_chain: str) -> float:
        """Estimate bridge cost in USD."""
        base_costs = {
            ("ethereum", "arbitrum"): 2.5,
            ("ethereum", "polygon"): 3.0,
            ("ethereum", "base"): 2.0,
            ("ethereum", "optimism"): 2.5,
            ("arbitrum", "polygon"): 1.5,
            ("arbitrum", "base"): 1.0,
            ("polygon", "base"): 1.5,
            ("optimism", "base"): 1.0,
        }
        key = tuple(sorted([from_chain, to_chain]))
        return base_costs.get(key, 5.0) + random.uniform(0, 2.0)
    
    def _estimate_gas_cost(self, buy_chain: str, sell_chain: str) -> float:
        """Estimate gas cost for both legs."""
        gas_costs = {
            "ethereum": random.uniform(5, 25),
            "arbitrum": random.uniform(0.1, 0.5),
            "polygon": random.uniform(0.01, 0.05),
            "base": random.uniform(0.05, 0.3),
            "optimism": random.uniform(0.1, 0.5),
            "bsc": random.uniform(0.1, 0.3),
            "avalanche": random.uniform(0.1, 0.5),
        }
        return gas_costs.get(buy_chain, 1.0) + gas_costs.get(sell_chain, 1.0)
    
    def get_price_matrix(self) -> Dict:
        """Get price matrix for dashboard display."""
        matrix = {}
        for token, chains in self._prices.items():
            matrix[token] = {}
            for chain, dexes in chains.items():
                best_price = max(dexes.values())
                best_dex = max(dexes, key=dexes.get)
                matrix[token][chain] = {
                    "price": round(best_price, 6),
                    "dex": best_dex,
                    "spread_bps": round((max(dexes.values()) - min(dexes.values())) / min(dexes.values()) * 10000, 2),
                }
        return matrix
