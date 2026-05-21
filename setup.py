from setuptools import setup, find_packages

setup(
    name="mimo-cross-chain-arb",
    version="1.0.0",
    description="AI-powered cross-chain arbitrage engine with multi-agent architecture",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "httpx>=0.25.0",
        "pyyaml>=6.0",
    ],
)
