"""
Coinbase exchange connector for Kazzy Agent
"""

import asyncio
import ccxt
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("Coinbase")


class CoinbaseConnector:
    """Coinbase exchange connector using CCXT"""

    def __init__(self):
        self.name = "Coinbase"
        self.is_connected = False
        self.exchange = None
        self.api_key = None
        self.api_secret = None

    async def connect(self, api_key: str, api_secret: str, **kwargs) -> bool:
        """Connect to Coinbase"""
        try:
            self.api_key = api_key
            self.api_secret = api_secret

            # Create CCXT exchange instance
            self.exchange = ccxt.coinbase({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })

            # Test connection
            await self.exchange.fetch_time()
            self.is_connected = True
            logger.info("✅ Connected to Coinbase")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to Coinbase: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Disconnect from Coinbase"""
        self.is_connected = False
        self.exchange = None
        logger.info("📴 Disconnected from Coinbase")

    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        if not self.is_connected or not self.exchange:
            return {}

        try:
            balance = await self.exchange.fetch_balance()
            return {
                'total': balance['total'],
                'free': balance['free'],
                'used': balance['used'],
                'available': balance['free']
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}

    async def get_positions(self) -> List[Dict]:
        """Get open positions"""
        if not self.is_connected or not self.exchange:
            return []

        try:
            positions = []
            balance = await self.exchange.fetch_balance()

            for currency, data in balance['total'].items():
                if data > 0:
                    positions.append({
                        'id': f"{self.name}_{currency}",
                        'symbol': currency,
                        'side': 'buy',
                        'size': data,
                        'entry_price': 0,
                        'current_price': 0,
                        'unrealized_pnl': 0
                    })

            return positions
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def create_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = 'market', **kwargs) -> Dict:
        """Create a new order"""
        if not self.is_connected or not self.exchange:
            return {}

        try:
            formatted_symbol = self._format_symbol(symbol)

            if order_type.lower() == 'market':
                order = await self.exchange.create_order(
                    symbol=formatted_symbol,
                    type='market',
                    side=side.upper(),
                    amount=quantity
                )
            else:
                order = await self.exchange.create_order(
                    symbol=formatted_symbol,
                    type=order_type.upper(),
                    side=side.upper(),
                    amount=quantity,
                    price=kwargs.get('price')
                )

            logger.info(f"Order created: {order['id']}")
            return order

        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return {}

    async def close_order(self, order_id: str) -> bool:
        """Close an existing order"""
        if not self.is_connected or not self.exchange:
            return False

        try:
            await self.exchange.cancel_order(order_id)
            return True
        except Exception as e:
            logger.error(f"Error closing order: {e}")
            return False

    async def get_market_data(self, symbol: str, timeframe: str = '1m',
                            limit: int = 100) -> List[Dict]:
        """Get market data (OHLCV)"""
        if not self.is_connected or not self.exchange:
            return []

        try:
            formatted_symbol = self._format_symbol(symbol)
            ohlcv = await self.exchange.fetch_ohlcv(
                symbol=formatted_symbol,
                timeframe=timeframe,
                limit=limit
            )

            data = []
            for candle in ohlcv:
                data.append({
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })

            return data

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return []

    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price"""
        try:
            formatted_symbol = self._format_symbol(symbol)
            ticker = await self.exchange.fetch_ticker(formatted_symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            return None

    def _format_symbol(self, symbol: str) -> str:
        """Format symbol for Coinbase"""
        if '/' not in symbol:
            return f"{symbol.upper()}-USD"
        return symbol.upper().replace('/', '-')

    async def get_open_orders(self) -> List[Dict]:
        """Get open orders"""
        if not self.is_connected or not self.exchange:
            return []

        try:
            return await self.exchange.fetch_open_orders()
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []
