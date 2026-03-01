"""
Binance exchange connector for Kazzy Agent
"""

import asyncio
import ccxt
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("Binance")


class BinanceConnector:
    """Binance exchange connector using CCXT"""

    def __init__(self):
        self.name = "Binance"
        self.is_connected = False
        self.exchange = None
        self.api_key = None
        self.api_secret = None

    async def connect(self, api_key: str, api_secret: str, testnet: bool = False, **kwargs) -> bool:
        """Connect to Binance"""
        try:
            self.api_key = api_key
            self.api_secret = api_secret

            # Create CCXT exchange instance
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })

            # Testnet mode if requested
            if testnet:
                self.exchange.set_sandbox_mode(True)
                logger.info("Binance testnet mode enabled")

            # Test connection by fetching time
            await self.exchange.fetch_time()
            self.is_connected = True
            logger.info("✅ Connected to Binance")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to Binance: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Disconnect from Binance"""
        self.is_connected = False
        self.exchange = None
        logger.info("📴 Disconnected from Binance")

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

            # Get all non-zero balances as positions
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
            # Format symbol for Binance
            formatted_symbol = self._format_symbol(symbol)

            order_params = {
                'symbol': formatted_symbol,
                'side': side.upper(),
                'amount': quantity,
                'type': order_type.upper()
            }

            # Add optional parameters
            if 'price' in kwargs:
                order_params['price'] = kwargs['price']

            if 'stop_loss' in kwargs:
                order_params['stopLoss'] = kwargs['stop_loss']

            if 'take_profit' in kwargs:
                order_params['takeProfit'] = kwargs['take_profit']

            # For market orders, use simplified approach
            if order_type.lower() == 'market':
                if side.upper() == 'BUY':
                    order = await self.exchange.create_order(
                        symbol=formatted_symbol,
                        type='market',
                        side='buy',
                        amount=quantity
                    )
                else:
                    order = await self.exchange.create_order(
                        symbol=formatted_symbol,
                        type='market',
                        side='sell',
                        amount=quantity
                    )
            else:
                order = await self.exchange.create_order(**order_params)

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
            logger.info(f"Order cancelled: {order_id}")
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

            # Format data
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
        """Get current price for a symbol"""
        try:
            formatted_symbol = self._format_symbol(symbol)
            ticker = await self.exchange.fetch_ticker(formatted_symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            return None

    def _format_symbol(self, symbol: str) -> str:
        """Format symbol for Binance (e.g., BTC/USDT)"""
        # Add /USDT if not present
        if '/' not in symbol:
            # Check if it's a common pair
            stablecoins = ['USDT', 'USDC', 'BUSD', 'USD']
            for stable in stablecoins:
                if symbol.endswith(stable):
                    return f"{symbol[:-len(stable)]}/{stable}"
            return f"{symbol}/USDT"
        return symbol.upper()

    async def get_open_orders(self) -> List[Dict]:
        """Get open orders"""
        if not self.is_connected or not self.exchange:
            return []

        try:
            orders = await self.exchange.fetch_open_orders()
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Get order book"""
        if not self.is_connected or not self.exchange:
            return {}

        try:
            formatted_symbol = self._format_symbol(symbol)
            order_book = await self.exchange.fetch_order_book(formatted_symbol, limit)
            return order_book
        except Exception as e:
            logger.error(f"Error fetching order book: {e}")
            return {}
