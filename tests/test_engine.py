"""Tests for MiMo Cross-Chain Arbitrage Engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.scanner_agent import ScannerAgent
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.risk_agent import RiskAgent
from src.core.kernel import AgentKernel
from src.core.price_feed import PriceFeed


def test_price_feed_quotes():
    feed = PriceFeed()
    quotes = feed.get_all_quotes()
    assert len(quotes) > 0
    assert all(q.price > 0 for q in quotes)


def test_price_feed_arbitrage():
    feed = PriceFeed()
    opps = feed.find_arbitrage(min_profit_bps=0)  # Accept any profit
    assert isinstance(opps, list)


def test_price_matrix():
    feed = PriceFeed()
    matrix = feed.get_price_matrix()
    assert "USDC" in matrix
    assert "ethereum" in matrix["USDC"]


@pytest.mark.asyncio
async def test_kernel_dispatch():
    kernel = AgentKernel()
    mock_agent = AsyncMock()
    mock_agent.execute = AsyncMock(return_value={"result": "ok"})
    mock_agent.start = AsyncMock()
    mock_agent.stop = AsyncMock()
    
    kernel.register("test", mock_agent)
    await kernel.start_all()
    result = await kernel.dispatch("test", {"action": "test"})
    assert result == {"result": "ok"}


@pytest.mark.asyncio
async def test_scanner_agent():
    agent = ScannerAgent()
    agent.llm = AsyncMock()
    agent.llm.generate = AsyncMock(return_value="Analysis complete")
    agent.llm.close = AsyncMock()
    
    result = await agent.execute({"action": "scan", "min_profit_bps": 0})
    assert "opportunities" in result
    assert "count" in result
