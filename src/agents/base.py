"""
Base Agent - Abstract base class for all arbitrage agents.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from src.core.llm import LLMClient

logger = logging.getLogger("mimo-arb.agents")


class BaseAgent(ABC):
    def __init__(self, name: str, llm: Optional[LLMClient] = None):
        self.name = name
        self.llm = llm or LLMClient()
        self._running = False
    
    async def start(self):
        self._running = True
        logger.info(f"Agent \'{self.name}\' started")
    
    async def stop(self):
        self._running = False
        await self.llm.close()
        logger.info(f"Agent \'{self.name}\' stopped")
    
    @abstractmethod
    async def execute(self, payload: dict) -> dict:
        ...
