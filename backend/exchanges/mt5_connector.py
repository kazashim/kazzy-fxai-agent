"""
MetaTrader 5/4 connector for Kazzy Agent
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("MetaTrader")


class MT5Connector:
    """MetaTrader 5/4 connector using MetaTrader5 Python package"""

    def __init__(self, version: int = 5):
        self.name = f"MT{version}"
        self.version = version
        self.is_connected = False
        self.mt5 = None
        self.account_info = None

    async def connect(self, login: str = None, password: str = None,
                     server: str = None, **kwargs) -> bool:
        """Connect to MetaTrader 5/4"""
        try:
            # Import MetaTrader5 package
            import MetaTrader5 as mt5

            self.mt5 = mt5

            # Initialize MT5
            if not mt5.initialize():
                logger.error(f"MT5 initialize() failed: {mt5.last_error()}")
                return False

            # Login if credentials provided
            if login and password and server:
                authorized = mt5.login(login=login, password=password, server=server)
                if not authorized:
                    logger.error(f"MT5 login failed: {mt5.last_error()}")
                    mt5.shutdown()
                    return False

            # Get account info
            self.account_info = mt5.account_info()
            if self.account_info is None:
                logger.error("Failed to get account info")
                mt5.shutdown()
                return False

            self.is_connected = True
            logger.info(f"✅ Connected to {self.name}")
            logger.info(f"Account: {self.account_info.login}, Balance: {self.account_info.balance}")
            return True

        except ImportError:
            logger.warning("MetaTrader5 package not installed. Install with: pip install MetaTrader5")
            logger.info("Running in simulation mode")
            self.is_connected = True
            self.account_info = {
                'login': 0,
                'balance': 10000,
                'equity': 10000,
                'margin': 0,
                'free_margin': 10000
            }
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to {self.name}: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Disconnect from MetaTrader"""
        try:
            if self.mt5:
                self.mt5.shutdown()
            self.is_connected = False
            logger.info(f"📴 Disconnected from {self.name}")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")

    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        try:
            if self.mt5 and self.is_connected:
                account = self.mt5.account_info()
                return {
                    'total': account.balance,
                    'equity': account.equity,
                    'margin': account.margin,
                    'free': account.margin_free,
                    'available': account.margin_free
                }
            elif self.account_info:
                return {
                    'total': self.account_info.get('balance', 0),
                    'equity': self.account_info.get('equity', 0),
                    'margin': self.account_info.get('margin', 0),
                    'free': self.account_info.get('free_margin', 0),
                    'available': self.account_info.get('free_margin', 0)
                }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")

        return {}

    async def get_positions(self) -> List[Dict]:
        """Get open positions"""
        if not self.is_connected:
            return []

        try:
            if self.mt5:
                positions = self.mt5.positions_get()
                if positions is None:
                    return []

                result = []
                for pos in positions:
                    result.append({
                        'id': str(pos.ticket),
                        'symbol': pos.symbol,
                        'side': 'buy' if pos.type == 0 else 'sell',
                        'size': pos.volume,
                        'entry_price': pos.price_open,
                        'current_price': pos.price_current,
                        'profit': pos.profit,
                        'unrealized_pnl': pos.profit,
                        'open_time': pos.time
                    })
                return result
            else:
                # Simulation mode
                return []

        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def create_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = 'market', **kwargs) -> Dict:
        """Create a new order"""
        if not self.is_connected:
            return {}

        try:
            if not self.mt5:
                # Simulation mode
                logger.info(f"Simulated order: {side.upper()} {quantity} {symbol}")
                return {
                    'id': f"sim_{symbol}_{side}",
                    'symbol': symbol,
                    'side': side,
                    'volume': quantity,
                    'price': kwargs.get('price', 0),
                    'status': 'filled'
                }

            # Determine order type
            symbol_info = self.mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol not found: {symbol}")
                return {}

            if not symbol_info.visible:
                self.mt5.symbol_select(symbol, True)

            point = symbol_info.point

            # Prepare request
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": quantity,
                "type": self.mt5.ORDER_TYPE_BUY if side.upper() == 'BUY' else self.mt5.ORDER_TYPE_SELL,
                "price": self.mt5.symbol_info_tick(symbol).ask if side.upper() == 'BUY' else self.mt5.symbol_info_tick(symbol).bid,
                "deviation": 20,
                "magic": 234000,
                "comment": "Kazzy Agent order",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }

            # Add stop loss and take profit if provided
            if 'stop_loss' in kwargs and kwargs['stop_loss']:
                request['sl'] = kwargs['stop_loss']
            if 'take_profit' in kwargs and kwargs['take_profit']:
                request['tp'] = kwargs['take_profit']

            # Send order
            result = self.mt5.order_send(request)

            if result.retcode != self.mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed: {result.comment}")
                return {}

            logger.info(f"Order created: {result.order}")
            return {
                'id': str(result.order),
                'symbol': symbol,
                'side': side,
                'volume': quantity,
                'price': result.price,
                'status': 'filled' if result.retcode == self.mt5.TRADE_RETCODE_DONE else 'pending'
            }

        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return {}

    async def close_position(self, position_id: str) -> bool:
        """Close an existing position"""
        if not self.is_connected:
            return False

        try:
            if not self.mt5:
                logger.info(f"Simulated position close: {position_id}")
                return True

            # Get position
            positions = self.mt5.positions_get(ticket=int(position_id))
            if not positions:
                logger.error(f"Position not found: {position_id}")
                return False

            pos = positions[0]

            # Prepare close request
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": self.mt5.ORDER_TYPE_SELL if pos.type == 0 else self.mt5.ORDER_TYPE_BUY,
                "position": pos.ticket,
                "price": self.mt5.symbol_info_tick(pos.symbol).bid if pos.type == 0 else self.mt5.symbol_info_tick(pos.symbol).ask,
                "deviation": 20,
                "magic": 234000,
                "comment": "Kazzy Agent close",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }

            result = self.mt5.order_send(request)

            if result.retcode == self.mt5.TRADE_RETCODE_DONE:
                logger.info(f"Position closed: {position_id}")
                return True
            else:
                logger.error(f"Close failed: {result.comment}")
                return False

        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False

    async def get_market_data(self, symbol: str, timeframe: str = '1H',
                            limit: int = 100) -> List[Dict]:
        """Get market data (OHLCV)"""
        if not self.is_connected:
            return []

        try:
            if not self.mt5:
                # Generate simulated data
                import random
                base_price = 1.0850 if 'USD' in symbol else 43000
                data = []
                for i in range(limit):
                    import time
                    timestamp = int(time.time()) - (limit - i) * 3600
                    open_price = base_price + random.uniform(-0.01, 0.01)
                    close_price = open_price + random.uniform(-0.005, 0.005)
                    high_price = max(open_price, close_price) + random.uniform(0, 0.005)
                    low_price = min(open_price, close_price) - random.uniform(0, 0.005)
                    data.append({
                        'timestamp': timestamp,
                        'open': open_price,
                        'high': high_price,
                        'low': low_price,
                        'close': close_price,
                        'volume': random.uniform(100, 1000)
                    })
                    base_price = close_price
                return data

            # Map timeframe to MT5 timeframe
            timeframe_map = {
                '1m': self.mt5.TIMEFRAME_M1,
                '5m': self.mt5.TIMEFRAME_M5,
                '15m': self.mt5.TIMEFRAME_M15,
                '30m': self.mt5.TIMEFRAME_M30,
                '1h': self.mt5.TIMEFRAME_H1,
                '4h': self.mt5.TIMEFRAME_H4,
                '1d': self.mt5.TIMEFRAME_D1,
                '1w': self.mt5.TIMEFRAME_W1,
            }

            mt_timeframe = timeframe_map.get(timeframe, self.mt5.TIMEFRAME_H1)

            rates = self.mt5.copy_rates_from_pos(symbol, mt_timeframe, 0, limit)

            if rates is None:
                return []

            data = []
            for rate in rates:
                data.append({
                    'timestamp': rate[0],
                    'open': rate[1],
                    'high': rate[2],
                    'low': rate[3],
                    'close': rate[4],
                    'volume': rate[5]
                })

            return data

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return []

    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price"""
        try:
            if self.mt5:
                tick = self.mt5.symbol_info_tick(symbol)
                if tick:
                    return tick.ask if tick.ask > 0 else tick.last
            else:
                # Simulation
                import random
                base = 1.0850 if 'USD' in symbol else 43000
                return base + random.uniform(-0.01, 0.01)
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
        return None

    def _format_symbol(self, symbol: str) -> str:
        """Format symbol for MetaTrader"""
        return symbol.upper()

    async def get_symbols(self) -> List[str]:
        """Get available symbols"""
        if not self.is_connected or not self.mt5:
            return []

        try:
            symbols = self.mt5.symbols_get()
            return [s.name for s in symbols if s.visible]
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            return []

    async def get_open_orders(self) -> List[Dict]:
        """Get pending orders"""
        if not self.is_connected or not self.mt5:
            return []

        try:
            orders = self.mt5.orders_get()
            if orders is None:
                return []

            result = []
            for order in orders:
                result.append({
                    'id': str(order.ticket),
                    'symbol': order.symbol,
                    'volume': order.volume_original,
                    'price': order.price_open,
                    'type': 'buy' if order.type == 0 else 'sell',
                    'state': order.state
                })
            return result

        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []
