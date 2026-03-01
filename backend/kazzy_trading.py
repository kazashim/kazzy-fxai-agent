#!/usr/bin/env python3
"""
Kazzy Agent Automated Trading System (KATS)
Main entry point for the trading engine
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kazzy_trading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("KazzyTrading")

class KazzyTradingEngine:
    """Main trading engine coordinating all components"""

    def __init__(self):
        self.is_running = False
        self.exchanges: Dict[str, Any] = {}
        self.positions: Dict[str, Any] = {}
        self.strategies: Dict[str, Any] = {}
        self.risk_manager = None
        self.order_executor = None

    async def initialize(self):
        """Initialize all trading components"""
        logger.info("🚀 Initializing Kazzy Agent Trading System...")

        # Initialize risk manager
        from risk_manager import RiskManager
        self.risk_manager = RiskManager(
            max_risk_per_trade=2.0,  # 2% max risk
            max_daily_loss=5.0,      # 5% max daily loss
            max_positions=5            # Max 5 open positions
        )

        # Initialize order executor
        from order_executor import OrderExecutor
        self.order_executor = OrderExecutor(self.risk_manager)

        # Initialize exchange connectors
        await self._initialize_exchanges()

        # Initialize strategies
        await self._initialize_strategies()

        logger.info("✅ Kazzy Agent initialized successfully")

    async def _initialize_exchanges(self):
        """Initialize exchange connections"""
        from exchanges.binance_connector import BinanceConnector
        from exchanges.bybit_connector import BybitConnector
        from exchanges.coinbase_connector import CoinbaseConnector
        from exchanges.mt5_connector import MT5Connector

        # Initialize available exchanges (will connect when API keys are provided)
        self.exchanges = {
            'binance': BinanceConnector(),
            'bybit': BybitConnector(),
            'coinbase': CoinbaseConnector(),
            'mt5': MT5Connector(),
            'mt4': MT5Connector(),  # MT5 package works for MT4
            'ctrader': None  # Placeholder
        }

        logger.info(f"📡 Exchange connectors initialized: {list(self.exchanges.keys())}")

    async def _initialize_strategies(self):
        """Initialize trading strategies"""
        from strategies.rsi_strategy import RSIStrategy
        from strategies.ma_crossover import MACrossoverStrategy
        from strategies.grid_strategy import GridStrategy

        self.strategies = {
            'rsi': RSIStrategy(),
            'ma_crossover': MACrossoverStrategy(),
            'grid': GridStrategy()
        }

        logger.info(f"🎯 Strategies loaded: {list(self.strategies.keys())}")

    async def connect_exchange(self, exchange_name: str, api_key: str, api_secret: str, **kwargs) -> bool:
        """Connect to a trading exchange"""
        if exchange_name not in self.exchanges:
            logger.error(f"Unknown exchange: {exchange_name}")
            return False

        connector = self.exchanges[exchange_name]
        if connector is None:
            logger.warning(f"Exchange {exchange_name} not yet implemented")
            return False

        try:
            success = await connector.connect(api_key, api_secret, **kwargs)
            if success:
                logger.info(f"✅ Connected to {exchange_name}")
            else:
                logger.error(f"❌ Failed to connect to {exchange_name}")
            return success
        except Exception as e:
            logger.error(f"Error connecting to {exchange_name}: {e}")
            return False

    async def disconnect_exchange(self, exchange_name: str):
        """Disconnect from an exchange"""
        if exchange_name in self.exchanges and self.exchanges[exchange_name]:
            await self.exchanges[exchange_name].disconnect()
            logger.info(f"📴 Disconnected from {exchange_name}")

    async def get_balance(self, exchange_name: str) -> Optional[Dict]:
        """Get account balance from exchange"""
        if exchange_name in self.exchanges and self.exchanges[exchange_name]:
            return await self.exchanges[exchange_name].get_balance()
        return None

    async def get_positions(self, exchange_name: str) -> Optional[list]:
        """Get open positions from exchange"""
        if exchange_name in self.exchanges and self.exchanges[exchange_name]:
            return await self.exchanges[exchange_name].get_positions()
        return None

    async def execute_trade(self, exchange_name: str, symbol: str, side: str,
                          quantity: float, order_type: str = 'market',
                          stop_loss: Optional[float] = None,
                          take_profit: Optional[float] = None) -> Optional[Dict]:
        """Execute a trade with risk management"""
        # Get account balance for risk calculation
        balance = await self.get_balance(exchange_name)
        if not balance:
            logger.error(f"Cannot get balance from {exchange_name}")
            return None

        # Validate trade with risk manager
        validation = self.risk_manager.validate_trade(
            balance=balance['available'],
            risk_percent=2.0,
            symbol=symbol,
            entry_price=0,  # Will be filled by executor
            stop_loss=stop_loss
        )

        if not validation['approved']:
            logger.warning(f"Trade rejected by risk manager: {validation['reason']}")
            return None

        # Execute trade
        result = await self.order_executor.execute(
            exchange=self.exchanges[exchange_name],
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        if result:
            logger.info(f"✅ Trade executed: {side} {quantity} {symbol} on {exchange_name}")
        else:
            logger.error(f"❌ Trade execution failed")

        return result

    async def close_position(self, exchange_name: str, position_id: str) -> bool:
        """Close an existing position"""
        result = await self.order_executor.close_position(
            exchange=self.exchanges[exchange_name],
            position_id=position_id
        )

        if result:
            logger.info(f"✅ Position closed: {position_id}")
        return result

    async def close_all_positions(self, exchange_name: str) -> bool:
        """Emergency: Close all positions on an exchange"""
        logger.warning(f"🛑 EMERGENCY: Closing all positions on {exchange_name}")

        positions = await self.get_positions(exchange_name)
        if not positions:
            return True

        success = True
        for pos in positions:
            if not await self.close_position(exchange_name, pos.get('id')):
                success = False

        return success

    async def run_strategy(self, strategy_name: str, exchange_name: str,
                          symbol: str, params: Dict = None) -> bool:
        """Run a trading strategy"""
        if strategy_name not in self.strategies:
            logger.error(f"Unknown strategy: {strategy_name}")
            return False

        strategy = self.strategies[strategy_name]

        # Get market data
        connector = self.exchanges.get(exchange_name)
        if not connector:
            logger.error(f"Exchange not connected: {exchange_name}")
            return False

        # Generate signal
        signal = await strategy.analyze(connector, symbol, params or {})

        if signal['action'] in ['BUY', 'SELL']:
            # Execute trade based on signal
            result = await self.execute_trade(
                exchange_name=exchange_name,
                symbol=symbol,
                side=signal['action'].lower(),
                quantity=signal.get('quantity', 0.01),
                order_type='market',
                stop_loss=signal.get('stop_loss'),
                take_profit=signal.get('take_profit')
            )
            return result is not None

        elif signal['action'] == 'CLOSE':
            # Close position
            return await self.close_position(exchange_name, signal.get('position_id'))

        return True

    async def start(self):
        """Start the trading engine"""
        self.is_running = True
        logger.info("▶️  Kazzy Agent Trading Engine Started")

    async def stop(self):
        """Stop the trading engine"""
        self.is_running = False
        logger.info("⏹️  Kazzy Agent Trading Engine Stopped")

    def get_status(self) -> Dict:
        """Get current system status"""
        exchange_status = {}
        for name, connector in self.exchanges.items():
            if connector:
                exchange_status[name] = connector.is_connected if hasattr(connector, 'is_connected') else False
            else:
                exchange_status[name] = False

        return {
            'is_running': self.is_running,
            'exchanges': exchange_status,
            'active_strategies': list(self.strategies.keys()),
            'open_positions': len(self.positions)
        }


# Global trading engine instance
trading_engine = KazzyTradingEngine()


async def main():
    """Main async entry point"""
    await trading_engine.initialize()
    await trading_engine.start()

    # Keep running
    try:
        while trading_engine.is_running:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await trading_engine.stop()


if __name__ == "__main__":
    asyncio.run(main())
