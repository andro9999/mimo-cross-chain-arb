# MiMo Cross-Chain Arbitrage Engine

> AI-powered multi-agent system for cross-chain arbitrage detection, analysis, risk assessment, and execution across 7 chains and 10 tokens. Built with MiMo LLM.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

---

## Demo

**Live:** http://43.153.206.68

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                  MiMo Cross-Chain Arbitrage Engine                    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │
│  │  Scanner  │  │ Analyzer  │  │ Executor  │  │   Risk    │        │
│  │   Agent   │  │   Agent   │  │   Agent   │  │   Agent   │        │
│  │           │  │           │  │           │  │           │        │
│  │ Cross-    │  │ Deep cost │  │ Trade     │  │ Bridge    │        │
│  │ chain     │  │ analysis, │  │ routing,  │  │ risk,     │        │
│  │ price     │  │ profit    │  │ simulate  │  │ MEV risk, │        │
│  │ scanning  │  │ calc,     │  │ execute   │  │ liquidity │        │
│  │           │  │ verdict   │  │           │  │           │        │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘        │
│        │              │              │              │                │
│  ┌─────┴─────┐  ┌─────┴─────┐                                              │
│  │ Strategy  │  │  Monitor  │                                              │
│  │   Agent   │  │   Agent   │                                              │
│  │           │  │           │                                              │
│  │ AI-       │  │ Real-time │                                              │
│  │ powered   │  │ price     │                                              │
│  │ trading   │  │ matrix,   │                                              │
│  │ strategy  │  │ alerts    │                                              │
│  └─────┬─────┘  └─────┬─────┘                                              │
│        │              │                                                    │
│  ┌─────┴──────────────┴─────────────────────────────────────┐            │
│  │                    Agent Kernel                            │            │
│  │         Lifecycle · Dispatch · Health Monitor              │            │
│  └─────┬──────────────┬──────────────┬──────────────┬───────┘            │
│        │              │              │              │                    │
│  ┌─────┴─────┐  ┌─────┴────┐  ┌─────┴────┐  ┌─────┴────┐              │
│  │   Price   │  │  MiMo    │  │  Bridge   │  │  DEX     │              │
│  │   Feed    │  │   LLM    │  │  Costs    │  │  Fees    │              │
│  │ 7 chains  │  │ Analyze  │  │ Estimate  │  │ 0.3%     │              │
│  │ 10 tokens │  │ Strategy │  │ Calculate │  │ Typical  │              │
│  └───────────┘  └──────────┘  └──────────┘  └──────────┘              │
│                                                                       │
├──────────────────────────────────────────────────────────────────────┤
│  FastAPI Server  ·  REST API  ·  Web Dashboard  ·  Docker            │
└──────────────────────────────────────────────────────────────────────┘
```

## Agents

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **ScannerAgent** | Cross-chain price scanning | Chains, tokens, min profit | Top 20 arbitrage opportunities |
| **AnalyzerAgent** | Deep profitability analysis | Opportunity details | Cost breakdown, verdict (execute/skip) |
| **ExecutorAgent** | Trade execution planning | Trade parameters | Step-by-step execution plan |
| **RiskAgent** | Risk assessment | Opportunity + chain data | Risk score (0-100), breakdown by category |
| **StrategyAgent** | AI strategy generation | Capital, risk tolerance | Adaptive trading strategy |
| **MonitorAgent** | Real-time price monitoring | Price feeds | Cross-chain price matrix |

## Features

### Cross-Chain Price Matrix
- Real-time prices across **7 chains** (Ethereum, Arbitrum, Polygon, Base, Optimism, BSC, Avalanche)
- **10 tokens** tracked (USDC, USDT, DAI, WETH, WBTC, ARB, MATIC, OP, LINK, UNI)
- Best price per chain with DEX source
- Spread calculation in basis points

### Opportunity Scanner
- Detects price differences across chains
- Filters by minimum profit threshold (20-100+ bps)
- Accounts for bridge costs, gas fees, DEX fees
- LLM-powered analysis of top opportunities

### Deep Analyzer
- Full cost breakdown (gas, bridge, DEX fees, slippage)
- Net profit calculation per trade
- Execution time estimation
- AI verdict: execute, skip, or monitor

### Risk Assessment
- **5 risk categories:** Bridge, MEV, Liquidity, Smart Contract, Market
- Visual risk bars with color coding
- Overall risk score (0-100)
- Risk level classification (low/medium/high)

### AI Strategy Generator
- MiMo LLM-powered strategy creation
- Capital allocation recommendations
- Chain pair optimization
- Risk-adjusted parameters

### Trade Executor
- Simulation mode (safe testing)
- Step-by-step execution plans
- Execution history tracking
- Contingency planning

## Supported Chains & DEXes

| Chain | DEXes |
|-------|-------|
| Ethereum | Uniswap V3, SushiSwap, Curve, Balancer |
| Arbitrum | Uniswap V3, SushiSwap, Camelot, GMX |
| Polygon | Uniswap V3, QuickSwap, SushiSwap, Curve |
| Base | Uniswap V3, BaseSwap, Aerodrome |
| Optimism | Uniswap V3, Velodrome, SushiSwap |
| BSC | PancakeSwap, BiSwap, ApeSwap |
| Avalanche | Trader Joe, Pangolin, Platypus |

## Quick Start

```bash
git clone https://github.com/mh1301/mimo-cross-chain-arb.git
cd mimo-cross-chain-arb

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env

# Run
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

Open http://localhost:8080 for the dashboard.

### Docker

```bash
docker-compose up -d
```

## API Reference

```bash
# Scan for opportunities
curl -X POST http://localhost:8080/api/scan \
  -H "Content-Type: application/json" \
  -d '{"min_profit_bps": 30}'

# Analyze an opportunity
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"token": "USDC", "buy_chain": "ethereum", "sell_chain": "arbitrum"}'

# Assess risk
curl -X POST http://localhost:8080/api/risk \
  -H "Content-Type: application/json" \
  -d '{"buy_chain": "ethereum", "sell_chain": "polygon"}'

# Generate strategy
curl -X POST http://localhost:8080/api/strategy \
  -H "Content-Type: application/json" \
  -d '{"capital_usd": 100000, "risk_tolerance": "medium"}'

# Get price matrix
curl http://localhost:8080/api/prices

# Health check
curl http://localhost:8080/health
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | MiMo v2.5 Pro | Analysis, strategy, risk assessment |
| **Framework** | FastAPI | REST API server |
| **Price Feed** | Simulated multi-chain DEX | Cross-chain price data |
| **Container** | Docker | Deployment |
| **Language** | Python 3.11+ | Core runtime |

## Project Structure

```
mimo-cross-chain-arb/
├── README.md
├── LICENSE
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── setup.py
├── .env.example
├── config/default.yaml
├── src/
│   ├── main.py                  # FastAPI server
│   ├── core/
│   │   ├── kernel.py            # Agent lifecycle
│   │   ├── llm.py               # MiMo LLM client
│   │   ├── monitor.py           # Metrics
│   │   └── price_feed.py        # Cross-chain price simulation
│   ├── agents/
│   │   ├── base.py              # Abstract base agent
│   │   ├── scanner_agent.py     # Opportunity detection
│   │   ├── analyzer_agent.py    # Profitability analysis
│   │   ├── executor_agent.py    # Trade execution
│   │   ├── risk_agent.py        # Risk assessment
│   │   ├── strategy_agent.py    # AI strategy
│   │   └── monitor_agent.py     # Price monitoring
│   └── utils/
├── templates/
│   └── index.html               # Dashboard
├── tests/
│   └── test_engine.py
└── data/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with MiMo LLM** — powering intelligent cross-chain arbitrage.
