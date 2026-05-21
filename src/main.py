"""
MiMo Cross-Chain Arbitrage Engine - Main Entry Point
Multi-agent system for cross-chain arbitrage detection and execution.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from src.core.kernel import AgentKernel
from src.core.monitor import MetricsCollector
from src.agents.scanner_agent import ScannerAgent
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.executor_agent import ExecutorAgent
from src.agents.risk_agent import RiskAgent
from src.agents.strategy_agent import StrategyAgent
from src.agents.monitor_agent import MonitorAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("mimo-arb")

kernel: AgentKernel = None
metrics: MetricsCollector = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global kernel, metrics
    logger.info("Starting MiMo Cross-Chain Arbitrage Engine...")
    
    kernel = AgentKernel()
    metrics = MetricsCollector()
    
    kernel.register("scanner", ScannerAgent())
    kernel.register("analyzer", AnalyzerAgent())
    kernel.register("executor", ExecutorAgent())
    kernel.register("risk", RiskAgent())
    kernel.register("strategy", StrategyAgent())
    kernel.register("monitor", MonitorAgent())
    
    await kernel.start_all()
    logger.info(f"Started {len(kernel.agents)} agents")
    
    yield
    
    await kernel.stop_all()
    logger.info("All agents stopped")


app = FastAPI(
    title="MiMo Cross-Chain Arbitrage Engine",
    description="AI-powered cross-chain arbitrage detection, analysis, and execution",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", "r") as f:
        return f.read()


@app.get("/health")
async def health():
    return {"status": "healthy", "agents": kernel.status() if kernel else {}}


@app.post("/api/scan")
async def scan_opportunities(request: dict):
    """Scan for cross-chain arbitrage opportunities."""
    chains = request.get("chains", ["ethereum", "arbitrum", "polygon", "base", "optimism"])
    tokens = request.get("tokens", ["USDC", "USDT", "DAI", "WETH", "WBTC"])
    min_profit = request.get("min_profit_bps", 50)
    
    result = await kernel.dispatch("scanner", {
        "action": "scan",
        "chains": chains,
        "tokens": tokens,
        "min_profit_bps": min_profit,
    })
    metrics.record("scan_completed")
    return JSONResponse(content=result)


@app.post("/api/analyze")
async def analyze_opportunity(request: dict):
    """Deep analysis of an arbitrage opportunity."""
    result = await kernel.dispatch("analyzer", {
        "action": "analyze",
        "opportunity": request,
    })
    metrics.record("analysis_completed")
    return JSONResponse(content=result)


@app.post("/api/execute")
async def execute_arbitrage(request: dict):
    """Execute an arbitrage trade (simulation or live)."""
    result = await kernel.dispatch("executor", {
        "action": "execute",
        "trade": request,
    })
    metrics.record("execution_attempted")
    return JSONResponse(content=result)


@app.post("/api/risk")
async def assess_risk(request: dict):
    """Assess risk for an arbitrage opportunity."""
    result = await kernel.dispatch("risk", {
        "action": "assess",
        "opportunity": request,
    })
    metrics.record("risk_assessed")
    return JSONResponse(content=result)


@app.post("/api/strategy")
async def generate_strategy(request: dict):
    """Generate AI-powered arbitrage strategy."""
    result = await kernel.dispatch("strategy", {
        "action": "generate",
        "params": request,
    })
    metrics.record("strategy_generated")
    return JSONResponse(content=result)


@app.get("/api/prices")
async def get_prices():
    """Get current cross-chain price matrix."""
    result = await kernel.dispatch("monitor", {
        "action": "prices",
    })
    return JSONResponse(content=result)


@app.get("/api/history")
async def get_history():
    """Get arbitrage execution history."""
    result = await kernel.dispatch("executor", {
        "action": "history",
    })
    return JSONResponse(content=result)


@app.get("/api/metrics")
async def get_metrics():
    return JSONResponse(content=metrics.summary())


@app.get("/api/agents")
async def list_agents():
    return JSONResponse(content=kernel.status())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
