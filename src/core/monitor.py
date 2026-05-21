"""
Metrics Collector.
"""

import time
import logging
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger("mimo-arb.monitor")


class MetricsCollector:
    def __init__(self):
        self._entries = []
        self._counters: Dict[str, int] = {}
        self._start_time = time.time()
    
    def record(self, name: str, value: float = 1.0):
        self._entries.append({"timestamp": time.time(), "name": name, "value": value})
        self._counters[name] = self._counters.get(name, 0) + value
    
    def summary(self) -> Dict:
        uptime = time.time() - self._start_time
        return {
            "uptime_seconds": round(uptime, 1),
            "total_events": len(self._entries),
            "counters": self._counters,
            "events_per_minute": round(len(self._entries) / max(uptime / 60, 1), 2),
        }
