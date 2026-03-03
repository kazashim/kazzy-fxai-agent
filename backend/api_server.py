"""
Kazzy Agent Trading API Server
FastAPI backend for the automated trading system
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KazzyAPI")

# Import trading components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Global trading engine
trading_engine = None


class ConnectionManager:
    """WebSocket connection manager for real-time updates"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")


manager = ConnectionManager()


# Initialize trading engine
async def initialize_engine():
    global trading_engine
    from kazzy_trading import KazzyTradingEngine
    trading_engine = KazzyTradingEngine()
    await trading_engine.initialize()
    await trading_engine.start()
    logger.info("Trading engine initialized")


# Pydantic models
class ConnectExchangeRequest(BaseModel):
    exchange: str
    api_key: str
    api_secret: str
    testnet: bool = False


class TradeRequest(BaseModel):
    exchange: str
    symbol: str
    side: str
    quantity: float
    order_type: str = 'market'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


class StrategyRequest(BaseModel):
    exchange: str
    symbol: str
    strategy: str
    params: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_engine()
    yield
    # Shutdown
    if trading_engine:
        await trading_engine.stop()


# Create FastAPI app
app = FastAPI(
    title="Kazzy Agent Trading API",
    description="Automated Trading System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "engine": "running" if trading_engine and trading_engine.is_running else "stopped"
    }


# Get system status
@app.get("/api/status")
async def get_status():
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    status = trading_engine.get_status()

    # Get balances for connected exchanges
    balances = {}
    for name, connector in trading_engine.exchanges.items():
        if connector and hasattr(connector, 'is_connected') and connector.is_connected:
            balance = await connector.get_balance()
            if balance:
                balances[name] = balance

    # Get positions
    all_positions = []
    for name, connector in trading_engine.exchanges.items():
        if connector and hasattr(connector, 'is_connected') and connector.is_connected:
            positions = await connector.get_positions()
            for pos in positions:
                pos['exchange'] = name
                all_positions.append(pos)

    return {
        **status,
        "balances": balances,
        "positions": all_positions,
        "total_balance": sum(b.get('total', 0) for b in balances.values())
    }


# Connect to exchange
@app.post("/api/connect")
async def connect_exchange(request: ConnectExchangeRequest):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    success = await trading_engine.connect_exchange(
        exchange_name=request.exchange,
        api_key=request.api_key,
        api_secret=request.api_secret,
        testnet=request.testnet
    )

    if success:
        await manager.broadcast({
            "type": "exchange_connected",
            "exchange": request.exchange
        })

    return {
        "success": success,
        "exchange": request.exchange,
        "message": f"Connected to {request.exchange}" if success else "Connection failed"
    }


# Disconnect from exchange
@app.post("/api/disconnect")
async def disconnect_exchange(exchange: str):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    await trading_engine.disconnect_exchange(exchange)

    await manager.broadcast({
        "type": "exchange_disconnected",
        "exchange": exchange
    })

    return {"success": True, "exchange": exchange}


# Get balance
@app.get("/api/balance/{exchange}")
async def get_balance(exchange: str):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    balance = await trading_engine.get_balance(exchange)

    if not balance:
        raise HTTPException(status_code=404, detail="Exchange not connected or no balance")

    return balance


# Get positions
@app.get("/api/positions/{exchange}")
async def get_positions(exchange: str):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    positions = await trading_engine.get_positions(exchange)

    return {"positions": positions, "count": len(positions)}


# Execute trade
@app.post("/api/trade")
async def execute_trade(request: TradeRequest):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    result = await trading_engine.execute_trade(
        exchange_name=request.exchange,
        symbol=request.symbol,
        side=request.side,
        quantity=request.quantity,
        order_type=request.order_type,
        stop_loss=request.stop_loss,
        take_profit=request.take_profit
    )

    if result:
        await manager.broadcast({
            "type": "trade_executed",
            "trade": result
        })

    return {
        "success": result is not None,
        "trade": result
    }


# Close position
@app.post("/api/close/{exchange}/{position_id}")
async def close_position(exchange: str, position_id: str):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    success = await trading_engine.close_position(exchange, position_id)

    if success:
        await manager.broadcast({
            "type": "position_closed",
            "position_id": position_id,
            "exchange": exchange
        })

    return {"success": success, "position_id": position_id}


# Close all positions
@app.post("/api/close-all/{exchange}")
async def close_all_positions(exchange: str):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    success = await trading_engine.close_all_positions(exchange)

    await manager.broadcast({
        "type": "all_positions_closed",
        "exchange": exchange
    })

    return {"success": success, "exchange": exchange}


# Run strategy
@app.post("/api/strategy/run")
async def run_strategy(request: StrategyRequest):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    result = await trading_engine.run_strategy(
        strategy_name=request.strategy,
        exchange_name=request.exchange,
        symbol=request.symbol,
        params=request.params
    )

    await manager.broadcast({
        "type": "strategy_run",
        "strategy": request.strategy,
        "symbol": request.symbol,
        "result": result
    })

    return {
        "success": result,
        "strategy": request.strategy,
        "symbol": request.symbol
    }


# Get available symbols
@app.get("/api/symbols/{exchange}")
async def get_symbols(exchange: str):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    connector = trading_engine.exchanges.get(exchange)
    if not connector or not connector.is_connected:
        raise HTTPException(status_code=404, detail="Exchange not connected")

    symbols = await connector.get_symbols() if hasattr(connector, 'get_symbols') else []

    return {"symbols": symbols[:100]}  # Limit to 100


# Get market data
@app.get("/api/market/{exchange}/{symbol}")
async def get_market_data(exchange: str, symbol: str, timeframe: str = '1h', limit: int = 100):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    connector = trading_engine.exchanges.get(exchange)
    if not connector or not connector.is_connected:
        raise HTTPException(status_code=404, detail="Exchange not connected")

    data = await connector.get_market_data(symbol, timeframe, limit)

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "data": data
    }


# Get current price
@app.get("/api/price/{exchange}/{symbol}")
async def get_price(exchange: str, symbol: str):
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    connector = trading_engine.exchanges.get(exchange)
    if not connector or not connector.is_connected:
        raise HTTPException(status_code=404, detail="Exchange not connected")

    price = await connector.get_current_price(symbol)

    return {
        "symbol": symbol,
        "price": price,
        "timestamp": datetime.now().isoformat()
    }


# Risk metrics
@app.get("/api/risk/metrics")
async def get_risk_metrics():
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    if not trading_engine.risk_manager:
        return {"error": "Risk manager not initialized"}

    # Get total balance
    total_balance = 0
    for name, connector in trading_engine.exchanges.items():
        if connector and hasattr(connector, 'is_connected') and connector.is_connected:
            balance = await connector.get_balance()
            total_balance += balance.get('total', 0)

    metrics = trading_engine.risk_manager.get_risk_metrics(total_balance)

    return metrics


# Emergency stop
@app.post("/api/emergency/stop")
async def emergency_stop():
    """Emergency stop - close all positions"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    logger.warning("🛑 EMERGENCY STOP TRIGGERED")

    results = {}

    # Close all positions on all exchanges
    for name, connector in trading_engine.exchanges.items():
        if connector and hasattr(connector, 'is_connected') and connector.is_connected:
            count = await trading_engine.close_all_positions(name)
            results[name] = f"Closed {count} positions"

    await manager.broadcast({
        "type": "emergency_stop",
        "results": results,
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "message": "Emergency stop executed",
        "results": results
    }


# AI Endpoints

# Enable AI autonomous trading
@app.post("/api/ai/enable")
async def enable_ai():
    """Enable AI autonomous trading"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    trading_engine.enable_ai()

    await manager.broadcast({
        "type": "ai_enabled",
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "message": "AI Autonomous Trading Enabled"
    }


# Disable AI autonomous trading
@app.post("/api/ai/disable")
async def disable_ai():
    """Disable AI autonomous trading"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    trading_engine.disable_ai()

    await manager.broadcast({
        "type": "ai_disabled",
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "message": "AI Autonomous Trading Disabled"
    }


# AI Analysis
@app.get("/api/ai/analyze/{exchange}/{symbol}")
async def ai_analyze(exchange: str, symbol: str):
    """Get AI analysis for a symbol"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    analysis = await trading_engine.analyze_with_ai(exchange, symbol)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis failed - check exchange connection")

    return {
        "symbol": symbol,
        "exchange": exchange,
        "analysis": analysis
    }


# AI Signal Generation
@app.get("/api/ai/signals/{exchange}")
async def ai_signals(exchange: str, symbols: str = "BTC/USDT,ETH/USDT"):
    """Generate AI signals for multiple symbols"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    symbol_list = [s.strip() for s in symbols.split(',')]
    signals = await trading_engine.generate_ai_signals(exchange, symbol_list)

    return {
        "exchange": exchange,
        "signals": signals,
        "count": len(signals)
    }


# AI NLP Command
@app.post("/api/ai/command")
async def ai_command(command: Dict[str, str]):
    """Process NLP command through AI"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    result = await trading_engine.process_ai_command(command.get('command', ''))

    await manager.broadcast({
        "type": "ai_command",
        "command": command.get('command'),
        "result": result
    })

    return result


# Run AI Automation
@app.post("/api/ai/automate/{exchange}")
async def run_ai_automation(exchange: str, symbols: str = "BTC/USDT,ETH/USDT"):
    """Run AI automation for autonomous trading"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    if not trading_engine.ai_enabled:
        return {
            "success": False,
            "message": "AI is not enabled. Enable AI first."
        }

    symbol_list = [s.strip() for s in symbols.split(',')]
    trades = await trading_engine.run_ai_automation(exchange, symbol_list)

    await manager.broadcast({
        "type": "ai_automation",
        "executed_trades": len(trades),
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "executed_trades": len(trades),
        "trades": trades
    }


# AI Learning Recommendations
@app.get("/api/ai/recommendations")
async def ai_recommendations():
    """Get AI recommendations based on learning"""
    if not trading_engine or not trading_engine.ai_learning_system:
        raise HTTPException(status_code=500, detail="AI learning system not initialized")

    recommendations = trading_engine.ai_learning_system.get_recommendations()

    return recommendations


# AI Should Continue Trading
@app.get("/api/ai/should_continue")
async def ai_should_continue():
    """Check if AI should continue trading"""
    if not trading_engine or not trading_engine.ai_learning_system:
        return {"should_continue": True, "reason": "AI not initialized"}

    should_continue = trading_engine.ai_learning_system.should_continue_trading()

    return {
        "should_continue": should_continue,
        "reason": "Trading allowed" if should_continue else "AI recommends pause"
    }


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle client messages
            msg_type = message.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "get_status":
                if trading_engine:
                    status = trading_engine.get_status()
                    await websocket.send_json({"type": "status", "data": status})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
