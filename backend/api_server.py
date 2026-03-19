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


# Poe AI Integration Endpoints
@app.get("/api/poe/models")
async def get_poe_models():
    """Get available Poe AI models"""
    from poe_integration import poe_integrator, POE_MODELS
    return {
        "enabled": poe_integrator.enabled,
        "current_model": poe_integrator.current_model,
        "models": POE_MODELS
    }


@app.post("/api/poe/set_model")
async def set_poe_model(model_id: str):
    """Set the active Poe AI model"""
    from poe_integration import poe_integrator
    poe_integrator.set_model(model_id)
    return {
        "success": True,
        "model": poe_integrator.current_model
    }


@app.post("/api/poe/chat")
async def poe_chat(message: str, context: Dict[str, Any] = {}):
    """Chat with Poe AI"""
    from poe_integration import poe_integrator

    result = await poe_integrator.chat_with_kazzy(message, context)
    return result


@app.post("/api/poe/analyze")
async def poe_analyze(symbol: str, market_data: Dict[str, Any]):
    """Analyze market with Poe AI"""
    from poe_integration import poe_integrator

    result = await poe_integrator.analyze_with_poe(market_data, symbol)
    return result


@app.get("/api/poe/status")
async def poe_status():
    """Get Poe AI status"""
    from poe_integration import poe_integrator
    return {
        "enabled": poe_integrator.enabled,
        "model": poe_integrator.current_model,
        "api_configured": bool(poe_integrator.api_key)
    }


# AI Learning & Data Aggregation Endpoints
@app.get("/api/learning/status")
async def get_learning_status():
    """Get AI learning system status"""
    from data_learning import ai_learning_system
    summary = ai_learning_system.get_learning_summary()
    return {
        "status": "active",
        "total_trades_analyzed": summary.get("total_trades", 0),
        "patterns_found": summary.get("patterns_found", 0),
        "improvements_available": summary.get("improvements_available", 0),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/learning/insights")
async def get_learning_insights():
    """Get AI learning insights and improvements"""
    from data_learning import ai_learning_system, data_aggregator

    # Get aggregated data from all exchanges
    if trading_engine and hasattr(trading_engine, 'exchanges'):
        aggregated_data = await data_aggregator.aggregate_all_data(trading_engine.exchanges)
        insights = await ai_learning_system.learn_from_data(aggregated_data)
        return insights
    else:
        # Demo data
        demo_data = {
            "trades": [],
            "accounts": [],
            "positions": []
        }
        insights = await ai_learning_system.learn_from_data(demo_data)
        return insights


@app.get("/api/learning/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    from data_learning import ai_learning_system

    metrics = ai_learning_system.performance_metrics
    if not metrics:
        # Demo metrics
        metrics = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "total_fees": 0,
            "net_pnl": 0,
            "profit_factor": 0,
            "max_drawdown": 0,
            "note": "Connect exchanges to see real performance data"
        }

    return metrics


@app.get("/api/learning/patterns")
async def get_detected_patterns():
    """Get AI-detected trading patterns"""
    from data_learning import ai_learning_system

    patterns = ai_learning_system.patterns_detected
    if not patterns:
        patterns = [
            {
                "type": "demo",
                "description": "Connect your trading accounts to detect real patterns",
                "recommendation": "Start trading to build pattern history"
            }
        ]

    return {"patterns": patterns}


@app.get("/api/learning/improvements")
async def get_improvements():
    """Get AI-suggested improvements"""
    from data_learning import ai_learning_system

    improvements = ai_learning_system.improvements_suggested
    if not improvements:
        improvements = [
            {
                "priority": "info",
                "category": "data_needed",
                "issue": "No trading data available",
                "suggestion": "Connect exchanges and start trading to receive AI-powered improvement suggestions",
                "expected_impact": "Personalized trading improvements"
            }
        ]

    return {"improvements": improvements}


@app.post("/api/learning/sync")
async def sync_all_data():
    """Force sync all data from connected exchanges"""
    from data_learning import data_aggregator, ai_learning_system

    if not trading_engine or not hasattr(trading_engine, 'exchanges'):
        return {
            "success": False,
            "message": "Trading engine not initialized. Connect exchanges first."
        }

    # Aggregate all data
    aggregated = await data_aggregator.aggregate_all_data(trading_engine.exchanges)

    # Learn from data
    insights = await ai_learning_system.learn_from_data(aggregated)

    return {
        "success": True,
        "message": "Data synced and learning updated",
        "data_summary": {
            "accounts": len(aggregated.get("accounts", [])),
            "positions": len(aggregated.get("positions", [])),
            "trades": len(aggregated.get("trades", [])),
            "markets": len(aggregated.get("markets", {}))
        },
        "insights": insights
    }


# ============================================
# UNIVERSAL EXCHANGE CONNECTOR ENDPOINTS
# ============================================

@app.get("/api/exchanges/available")
async def get_available_exchanges():
    """Get list of all available exchange connectors"""
    from exchange_connectors import ExchangeType
    return {
        "exchanges": [
            {"id": e.value, "name": e.name.replace("_", " ").title()}
            for e in ExchangeType
        ]
    }


@app.post("/api/exchanges/connect")
async def connect_universal_exchange(request: ConnectExchangeRequest):
    """Connect to any exchange using universal connector"""
    from exchange_connectors import exchange_manager

    success = await exchange_manager.connect_exchange(
        exchange_type=request.exchange,
        api_key=request.api_key,
        api_secret=request.api_secret,
        testnet=request.testnet
    )

    if success:
        await manager.broadcast({
            "type": "exchange_connected",
            "exchange": request.exchange,
            "timestamp": datetime.now().isoformat()
        })

    return {
        "success": success,
        "exchange": request.exchange,
        "message": f"Connected to {request.exchange}" if success else "Connection failed"
    }


@app.post("/api/exchanges/disconnect")
async def disconnect_universal_exchange(exchange: str):
    """Disconnect from an exchange"""
    from exchange_connectors import exchange_manager

    await exchange_manager.disconnect_exchange(exchange)

    await manager.broadcast({
        "type": "exchange_disconnected",
        "exchange": exchange,
        "timestamp": datetime.now().isoformat()
    })

    return {"success": True, "exchange": exchange}


@app.get("/api/exchanges/connected")
async def get_connected_exchanges():
    """Get list of connected exchanges"""
    from exchange_connectors import exchange_manager
    return {
        "exchanges": exchange_manager.get_connected_exchanges(),
        "count": len(exchange_manager.exchanges)
    }


@app.get("/api/exchanges/balance")
async def get_total_balance():
    """Get total balance across all exchanges"""
    from exchange_connectors import exchange_manager
    total = await exchange_manager.get_total_balance()
    return {
        "total_balance": total,
        "currency": "USD"
    }


@app.get("/api/exchanges/positions")
async def get_all_positions():
    """Get all positions across all exchanges"""
    from exchange_connectors import exchange_manager
    positions = await exchange_manager.get_all_positions()
    return {
        "positions": positions,
        "count": len(positions)
    }


@app.get("/api/exchanges/tickers")
async def get_all_tickers():
    """Get tickers from all exchanges"""
    from exchange_connectors import exchange_manager
    tickers = await exchange_manager.get_all_tickers()
    return {
        "tickers": {symbol: vars(ticker) for symbol, ticker in tickers.items()},
        "count": len(tickers)
    }


@app.post("/api/exchanges/trade")
async def execute_universal_trade(request: TradeRequest):
    """Execute trade on any exchange"""
    from exchange_connectors import exchange_manager

    result = await exchange_manager.execute_trade(
        exchange_type=request.exchange,
        symbol=request.symbol,
        side=request.side,
        quantity=request.quantity,
        order_type=request.order_type,
        price=request.stop_loss or 0,
        stop_loss=request.stop_loss,
        take_profit=request.take_profit
    )

    if result.get("success"):
        await manager.broadcast({
            "type": "trade_executed",
            "trade": result,
            "timestamp": datetime.now().isoformat()
        })

    return result


# ============================================
# LIVE TRADING FEEDS ENDPOINTS
# ============================================

@app.post("/api/feeds/start")
async def start_live_feeds():
    """Start live trading feeds streaming"""
    from live_feeds import live_feed_manager

    if live_feed_manager.is_streaming:
        return {
            "success": True,
            "message": "Feeds already streaming"
        }

    await live_feed_manager.start_streaming()

    await manager.broadcast({
        "type": "feeds_started",
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "message": "Live feeds started"
    }


@app.post("/api/feeds/stop")
async def stop_live_feeds():
    """Stop live trading feeds"""
    from live_feeds import live_feed_manager

    await live_feed_manager.stop_streaming()

    await manager.broadcast({
        "type": "feeds_stopped",
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "message": "Live feeds stopped"
    }


@app.get("/api/feeds/status")
async def get_feeds_status():
    """Get live feeds status"""
    from live_feeds import live_feed_manager, FeedType

    return {
        "streaming": live_feed_manager.is_streaming,
        "feed_types": [f.value for f in FeedType],
        "subscribers": {k: len(v) for k, v in live_feed_manager.subscribers.items()},
        "history_length": {
            k: len(v) for k, v in live_feed_manager.feed_history.items()
        }
    }


@app.get("/api/feeds/prices")
async def get_current_prices():
    """Get current prices from live feeds"""
    from live_feeds import live_feed_manager
    return {
        "prices": live_feed_manager.get_latest_prices(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/feeds/price/{symbol}")
async def get_symbol_price(symbol: str):
    """Get price history for a symbol"""
    from live_feeds import live_feed_manager
    history = live_feed_manager.get_price_history(symbol)
    return {
        "symbol": symbol,
        "history": history,
        "count": len(history)
    }


# ============================================
# AUTO-TRADING ENGINE ENDPOINTS
# ============================================

class AutoTradeRequest(BaseModel):
    symbols: list[str]
    risk_level: str = "medium"
    max_positions: int = 5


@app.post("/api/auto/start")
async def start_auto_trading(request: AutoTradeRequest):
    """Start autonomous AI trading"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    # Enable AI and start trading
    trading_engine.enable_ai()

    # Get available exchanges
    exchange_name = "binance"
    if trading_engine.exchanges:
        exchange_name = list(trading_engine.exchanges.keys())[0]

    results = []
    for symbol in request.symbols[:request.max_positions]:
        try:
            # Generate AI signal
            signal = await trading_engine.generate_ai_signals(exchange_name, [symbol])
            if signal and signal.get("signals"):
                trade_signal = signal["signals"][0]
                if trade_signal.get("action") in ["buy", "sell"]:
                    # Execute trade
                    result = await trading_engine.execute_trade(
                        exchange_name=exchange_name,
                        symbol=symbol,
                        side=trade_signal["action"],
                        quantity=0.01,  # Default quantity
                        order_type="market"
                    )
                    results.append({
                        "symbol": symbol,
                        "signal": trade_signal,
                        "executed": result is not None
                    })
        except Exception as e:
            logger.error(f"Auto-trade error for {symbol}: {e}")

    await manager.broadcast({
        "type": "auto_trading_started",
        "symbols": request.symbols,
        "trades_executed": len(results),
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "message": f"Auto-trading started for {len(request.symbols)} symbols",
        "trades": results
    }


@app.post("/api/auto/stop")
async def stop_auto_trading():
    """Stop autonomous trading"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")

    trading_engine.disable_ai()

    # Close all positions
    for name, connector in trading_engine.exchanges.items():
        if connector and hasattr(connector, 'is_connected') and connector.is_connected:
            await trading_engine.close_all_positions(name)

    await manager.broadcast({
        "type": "auto_trading_stopped",
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "message": "Auto-trading stopped, all positions closed"
    }


@app.get("/api/auto/status")
async def get_auto_trading_status():
    """Get auto-trading status"""
    if not trading_engine:
        return {
            "enabled": False,
            "message": "Trading engine not initialized"
        }

    return {
        "enabled": trading_engine.ai_enabled,
        "positions_count": len(trading_engine.positions) if hasattr(trading_engine, 'positions') else 0,
        "total_balance": sum(
            b.get('total', 0) for b in (trading_engine.balances.values() if hasattr(trading_engine, 'balances') else {})
        )
    }


# ============================================
# REAL TRADING SIGNALS ENDPOINTS
# ============================================

@app.get("/api/signals/live")
async def get_live_signals():
    """Get real-time trading signals based on live market data"""
    from signal_generator import get_live_signals

    try:
        signals = await get_live_signals()
        return {
            "success": True,
            "signals": signals,
            "count": len(signals),
            "timestamp": datetime.now().isoformat(),
            "source": "Live market data"
        }
    except Exception as e:
        logger.error(f"Signal generation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "signals": [],
            "count": 0
        }


@app.get("/api/signals/market-overview")
async def get_market_overview():
    """Get market overview with live prices"""
    from signal_generator import get_market_overview

    try:
        overview = await get_market_overview()
        return {
            "success": True,
            "data": overview
        }
    except Exception as e:
        logger.error(f"Market overview error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/signals/{symbol}")
async def get_signal_for_symbol(symbol: str):
    """Get trading signal for a specific symbol"""
    from signal_generator import signal_generator

    try:
        # Generate signal for specific symbol
        signals = await signal_generator.generate_signals([symbol])
        if signals:
            sig = signals[0]
            return {
                "success": True,
                "signal": {
                    "id": sig.id,
                    "symbol": sig.symbol,
                    "direction": sig.direction,
                    "entry_zone": sig.entry_zone,
                    "stop_loss": sig.stop_loss,
                    "take_profit": sig.take_profit,
                    "confidence": sig.confidence,
                    "timeframe": sig.timeframe,
                    "strategy": sig.strategy,
                    "entry_reason": sig.entry_reason,
                    "risk_reward": sig.risk_reward,
                    "price": sig.price,
                    "change_24h": sig.change_24h,
                    "timestamp": sig.timestamp
                }
            }
        else:
            return {
                "success": False,
                "message": f"No signal available for {symbol}"
            }
    except Exception as e:
        logger.error(f"Signal error for {symbol}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# EXPERT ADVISOR (EA) INTEGRATION ENDPOINTS
# ============================================

class ConnectMTRequest(BaseModel):
    mt_type: str = "MT5"
    login: str = ""
    password: str = ""
    server: str = ""
    path: str = ""


class EATradingModeRequest(BaseModel):
    mode: str = "copy_only"  # copy_only, hybrid, auto_execute


class ExecuteEATradeRequest(BaseModel):
    ea_name: str
    symbol: str
    action: str
    volume: float
    price: float = 0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@app.post("/api/ea/connect")
async def connect_metatrader(request: ConnectMTRequest):
    """Connect to MetaTrader 4 or 5 terminal with Expert Advisors"""
    from expert_advisor import ea_manager

    if request.mt_type == "MT4":
        success = await ea_manager.connect_mt4(path=request.path)
    else:
        success = await ea_manager.connect_mt5(
            login=request.login,
            password=request.password,
            server=request.server,
            path=request.path
        )

    return {
        "success": success,
        "mt_type": request.mt_type,
        "message": f"Connected to {request.mt_type}" if success else "Connection failed"
    }


@app.post("/api/ea/disconnect")
async def disconnect_metatrader(mt_type: str = "MT5"):
    """Disconnect from MetaTrader"""
    from expert_advisor import ea_manager

    if mt_type == "MT4" and ea_manager.mt4_connector:
        await ea_manager.mt4_connector.disconnect()
    elif mt_type == "MT5" and ea_manager.mt5_connector:
        await ea_manager.mt5_connector.disconnect()

    return {"success": True, "mt_type": mt_type}


@app.get("/api/ea/status")
async def get_ea_status():
    """Get Expert Advisor connection status"""
    from expert_advisor import ea_manager

    return {
        "mt4_connected": ea_manager.mt4_connector.is_connected if ea_manager.mt4_connector else False,
        "mt5_connected": ea_manager.mt5_connector.is_connected if ea_manager.mt5_connector else False,
        "trading_mode": ea_manager.trading_mode.value,
        "monitoring": ea_manager.is_monitoring,
        "total_signals": len(ea_manager.ea_signals)
    }


@app.post("/api/ea/mode")
async def set_ea_mode(request: EATradingModeRequest):
    """Set EA trading mode"""
    from expert_advisor import ea_manager, EATradingMode

    mode_map = {
        "copy_only": EATradingMode.COPY_ONLY,
        "hybrid": EATradingMode.HYBRID,
        "auto_execute": EATradingMode.AUTO_EXECUTE
    }

    mode = mode_map.get(request.mode, EATradingMode.COPY_ONLY)
    ea_manager.set_trading_mode(mode)

    return {
        "success": True,
        "mode": request.mode,
        "description": {
            "copy_only": "Copy EA signals to Kazzy account",
            "hybrid": "EA + Kazzy AI combined",
            "auto_execute": "Execute all EA signals automatically"
        }.get(request.mode, "")
    }


@app.get("/api/ea/list")
async def list_expert_advisors():
    """List all running Expert Advisors"""
    from expert_advisor import ea_manager

    experts = []

    if ea_manager.mt5_connector and ea_manager.mt5_connector.is_connected:
        mt5_experts = await ea_manager.mt5_connector.get_expert_advisors()
        for ea in mt5_experts:
            experts.append({
                "name": ea.name,
                "version": ea.version,
                "symbol": ea.symbol,
                "is_active": ea.is_active,
                "total_trades": ea.total_trades,
                "winning_trades": ea.winning_trades,
                "losing_trades": ea.losing_trades,
                "win_rate": round(ea.winning_trades / ea.total_trades * 100, 2) if ea.total_trades > 0 else 0,
                "mt_type": "MT5"
            })

    if ea_manager.mt4_connector and ea_manager.mt4_connector.is_connected:
        mt4_experts = await ea_manager.mt4_connector.get_expert_advisors()
        for ea in mt4_experts:
            experts.append({
                "name": ea.name,
                "version": ea.version,
                "symbol": ea.symbol,
                "is_active": ea.is_active,
                "total_trades": ea.total_trades,
                "winning_trades": ea.winning_trades,
                "losing_trades": ea.losing_trades,
                "win_rate": round(ea.winning_trades / ea.total_trades * 100, 2) if ea.total_trades > 0 else 0,
                "mt_type": "MT4"
            })

    return {
        "experts": experts,
        "count": len(experts)
    }


@app.get("/api/ea/signals")
async def get_ea_signals(limit: int = 100):
    """Get recent EA signals"""
    from expert_advisor import ea_manager

    signals = ea_manager.ea_signals[-limit:]

    return {
        "signals": [
            {
                "ea_name": s.ea_name,
                "symbol": s.symbol,
                "action": s.action,
                "lot_size": s.lot_size,
                "stop_loss": s.stop_loss,
                "take_profit": s.take_profit,
                "timestamp": s.timestamp,
                "confidence": s.confidence
            }
            for s in signals
        ],
        "count": len(signals)
    }


@app.post("/api/ea/import")
async def import_ea_signals(filepath: str):
    """Import EA signals from file"""
    from expert_advisor import ea_manager

    await ea_manager.import_ea_signals(filepath)

    return {
        "success": True,
        "message": f"Imported signals from {filepath}",
        "total_signals": len(ea_manager.ea_signals)
    }


@app.post("/api/ea/export")
async def export_ea_signals(filepath: str = "ea_signals.json"):
    """Export EA signals to file"""
    from expert_advisor import ea_manager

    await ea_manager.export_ea_signals(filepath)

    return {
        "success": True,
        "message": f"Exported signals to {filepath}",
        "total_signals": len(ea_manager.ea_signals)
    }


@app.get("/api/ea/performance")
async def get_ea_performance():
    """Get EA performance statistics"""
    from expert_advisor import ea_manager

    performance = await ea_manager.get_ea_performance()

    return performance


@app.post("/api/ea/monitor/start")
async def start_ea_monitoring():
    """Start monitoring EA signals"""
    from expert_advisor import ea_manager

    if not ea_manager.is_monitoring:
        asyncio.create_task(ea_manager.start_monitoring())

    return {
        "success": True,
        "message": "EA monitoring started"
    }


@app.post("/api/ea/monitor/stop")
async def stop_ea_monitoring():
    """Stop monitoring EA signals"""
    from expert_advisor import ea_manager

    await ea_manager.stop_monitoring()

    return {
        "success": True,
        "message": "EA monitoring stopped"
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
