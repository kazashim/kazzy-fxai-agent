"""
Exchange connectors for Kazzy Agent
Unified interface for all trading platforms
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

logger = logging.getLogger("Exchanges")


class BaseExchange(ABC):
    """Base class for all exchange connectors"""

    def __init__(self, name: str):
        self.name = name
        self.is_connected = False
        self.api_key = None
        self.api_secret = None

    @abstractmethod
    async def connect(self, api_key: str, api_secret: str, **kwargs) -> bool:
        """Connect to the exchange"""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the exchange"""
        pass

    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        pass

    @abstractmethod
    async def get_positions(self) -> List[Dict]:
        """Get open positions"""
        pass

    @abstractmethod
    async def create_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = 'market', **kwargs) -> Dict:
        """Create a new order"""
        pass

    @abstractmethod
    async def close_order(self, order_id: str) -> bool:
        """Close an existing order"""
        pass

    @abstractmethod
    async def get_market_data(self, symbol: str, timeframe: str = '1m',
                            limit: int = 100) -> List[Dict]:
        """Get market data (OHLCV)"""
        pass

    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get current ticker price"""
        try:
            data = await self.get_market_data(symbol, '1m', 1)
            if data:
                return data[-1]
        except Exception as e:
            logger.error(f"Error getting ticker for {symbol}: {e}")
        return None

    def _format_symbol(self, symbol: str) -> str:
        """Format symbol for exchange"""
        return symbol.upper()

    def _parse_symbol(self, symbol: str) -> str:
        """Parse exchange symbol to standard format"""
        return symbol.upper()
