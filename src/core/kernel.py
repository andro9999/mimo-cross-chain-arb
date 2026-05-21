"""
Agent Kernel - Lifecycle management for all agents.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger("mimo-arb.kernel")


class AgentState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class AgentHealth:
    state: AgentState = AgentState.IDLE
    last_heartbeat: Optional[datetime] = None
    error_count: int = 0
    total_tasks: int = 0
    avg_latency_ms: float = 0.0


class AgentKernel:
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.health: Dict[str, AgentHealth] = {}
    
    def register(self, name: str, agent: Any) -> None:
        self.agents[name] = agent
        self.health[name] = AgentHealth()
        logger.info(f"Registered agent: {name}")
    
    async def start_all(self) -> None:
        for name, agent in self.agents.items():
            try:
                if hasattr(agent, "start"):
                    await agent.start()
                self.health[name].state = AgentState.RUNNING
                self.health[name].last_heartbeat = datetime.utcnow()
            except Exception as e:
                self.health[name].state = AgentState.ERROR
                self.health[name].error_count += 1
                logger.error(f"Failed to start {name}: {e}")
    
    async def stop_all(self) -> None:
        for name, agent in self.agents.items():
            try:
                if hasattr(agent, "stop"):
                    await agent.stop()
                self.health[name].state = AgentState.STOPPED
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
    
    async def dispatch(self, agent_name: str, payload: dict) -> dict:
        if agent_name not in self.agents:
            return {"error": f"Agent \'{agent_name}\' not found"}
        
        agent = self.agents[agent_name]
        health = self.health[agent_name]
        start_time = asyncio.get_event_loop().time()
        
        try:
            result = await agent.execute(payload)
            elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
            health.total_tasks += 1
            health.avg_latency_ms = (
                (health.avg_latency_ms * (health.total_tasks - 1) + elapsed)
                / health.total_tasks
            )
            health.last_heartbeat = datetime.utcnow()
            return result
        except Exception as e:
            health.error_count += 1
            health.state = AgentState.ERROR
            logger.error(f"Agent {agent_name} error: {e}")
            return {"error": str(e)}
    
    def status(self) -> dict:
        return {
            name: {
                "state": h.state.value,
                "tasks": h.total_tasks,
                "errors": h.error_count,
                "avg_latency_ms": round(h.avg_latency_ms, 2),
                "last_heartbeat": h.last_heartbeat.isoformat() if h.last_heartbeat else None,
            }
            for name, h in self.health.items()
        }
