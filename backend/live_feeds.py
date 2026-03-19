"""
Kazzy Agent - Live Trading Feeds System
Real-time WebSocket streaming for prices, orders, positions
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
import random

logger = logging.getLogger("KazzyFeeds")

class FeedType(Enum):
    """Types of live feeds"""
    TICKER = "ticker"
    ORDER_BOOK = "order_book"
    TRADES = "trades"
    POSITIONS = "positions"
    ORDERS = "orders"
    BALANCE = "balance"
    SYSTEM = "system"


@dataclass
class FeedMessage:
    """Feed message structure"""
    type: str
    exchange: str
    data: Dict[str, Any]
    timestamp: str = ""


class LiveFeedManager:
    """
    Manages all live trading feeds via WebSocket
    Provides real-time streaming for prices, positions, orders
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.feed_history: Dict[str, List] = {}
        self.is_streaming = False
        self.stream_tasks = []

        # Price simulation for demo
        self.base_prices = {
            'BTC/USDT': 67500, 'ETH/USDT': 3450, 'SOL/USDT': 145,
            'BNB/USDT': 580, 'XRP/USDT': 0.52, 'ADA/USDT': 0.45,
            'EUR/USD': 1.0850, 'GBP/USD': 1.2650, 'USD/JPY': 149.50,
            'XAU/USD': 2350, 'XAG/USD': 27.50, 'WTI': 78.50,
            'AAPL': 178.50, 'MSFT': 405.20, 'GOOGL': 142.50,
            'TSLA': 245.80, 'NVDA': 875.50, 'META': 485.20,
            'US30': 38500, 'US500': 5150, 'NAS100': 17500,
            'UK100': 7700, 'GER40': 18000, 'JPN225': 37000
        }
        self.current_prices = self.base_prices.copy()

    async def start_streaming(self):
        """Start live feed streaming"""
        if self.is_streaming:
            return

        self.is_streaming = True
        logger.info("📡 Starting live trading feeds...")

        # Start multiple feed streams
        self.stream_tasks = [
            asyncio.create_task(self._stream_ticker_prices()),
            asyncio.create_task(self._stream_order_book()),
            asyncio.create_task(self._stream_positions()),
            asyncio.create_task(self._stream_balance()),
            asyncio.create_task(self._stream_system_status()),
        ]

        logger.info("✅ Live feeds streaming started")

    async def stop_streaming(self):
        """Stop all live feeds"""
        self.is_streaming = False
        for task in self.stream_tasks:
            task.cancel()
        self.stream_tasks = []
        logger.info("⏹️ Live feeds stopped")

    def subscribe(self, feed_type: str, callback: Callable):
        """Subscribe to a feed type"""
        if feed_type not in self.subscribers:
            self.subscribers[feed_type] = []
        self.subscribers[feed_type].append(callback)
        logger.info(f"📬 Subscribed to {feed_type} feed")

    def unsubscribe(self, feed_type: str, callback: Callable):
        """Unsubscribe from a feed"""
        if feed_type in self.subscribers:
            self.subscribers[feed_type].remove(callback)

    async def _broadcast(self, feed_type: str, message: FeedMessage):
        """Broadcast message to all subscribers"""
        if feed_type in self.subscribers:
            for callback in self.subscribers[feed_type]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Feed callback error: {e}")

    async def _stream_ticker_prices(self):
        """Stream real-time price updates"""
        while self.is_streaming:
            try:
                # Update prices with small random changes
                for symbol in self.current_prices:
                    change_percent = random.uniform(-0.5, 0.5)  # 0.5% max change
                    self.current_prices[symbol] *= (1 + change_percent / 100)

                # Create ticker data
                for symbol, price in self.current_prices.items():
                    ticker_data = {
                        "symbol": symbol,
                        "price": round(price, 4),
                        "bid": round(price * 0.9995, 4),
                        "ask": round(price * 1.0005, 4),
                        "change_24h": round(random.uniform(-5, 5), 2),
                        "change_percent_24h": round(random.uniform(-3, 3), 2),
                        "volume_24h": round(random.uniform(1000, 100000), 2),
                        "high_24h": round(price * 1.02, 4),
                        "low_24h": round(price * 0.98, 4)
                    }

                    message = FeedMessage(
                        type=FeedType.TICKER.value,
                        exchange="all",
                        data=ticker_data,
                        timestamp=datetime.now().isoformat()
                    )

                    await self._broadcast(FeedType.TICKER.value, message)

                # Store in history
                if FeedType.TICKER.value not in self.feed_history:
                    self.feed_history[FeedType.TICKER.value] = []
                self.feed_history[FeedType.TICKER.value].append({
                    "prices": self.current_prices.copy(),
                    "timestamp": datetime.now().isoformat()
                })

                await asyncio.sleep(1)  # Update every second

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ticker stream error: {e}")
                await asyncio.sleep(1)

    async def _stream_order_book(self):
        """Stream order book updates"""
        while self.is_streaming:
            try:
                for symbol, price in self.current_prices.items():
                    # Generate order book
                    bids = []
                    asks = []

                    for i in range(10):
                        bid_price = price * (1 - (i + 1) * 0.001)
                        ask_price = price * (1 + (i + 1) * 0.001)
                        bid_qty = round(random.uniform(0.1, 10), 4)
                        ask_qty = round(random.uniform(0.1, 10), 4)
                        bids.append([bid_price, bid_qty])
                        asks.append([ask_price, ask_qty])

                    order_book_data = {
                        "symbol": symbol,
                        "bids": bids,
                        "asks": asks,
                        "spread": round(asks[0][0] - bids[0][0], 4)
                    }

                    message = FeedMessage(
                        type=FeedType.ORDER_BOOK.value,
                        exchange="all",
                        data=order_book_data,
                        timestamp=datetime.now().isoformat()
                    )

                    await self._broadcast(FeedType.ORDER_BOOK.value, message)

                await asyncio.sleep(2)  # Update every 2 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Order book stream error: {e}")
                await asyncio.sleep(2)

    async def _stream_positions(self):
        """Stream position updates"""
        while self.is_streaming:
            try:
                # Demo positions
                positions = [
                    {
                        "id": "pos_1",
                        "symbol": "BTC/USDT",
                        "side": "long",
                        "quantity": 0.5,
                        "entry_price": 65000,
                        "current_price": self.current_prices.get('BTC/USDT', 67500),
                        "unrealized_pnl": round((self.current_prices.get('BTC/USDT', 67500) - 65000) * 0.5, 2),
                        "leverage": 3,
                        "margin": 10833
                    },
                    {
                        "id": "pos_2",
                        "symbol": "ETH/USDT",
                        "side": "long",
                        "quantity": 5,
                        "entry_price": 3200,
                        "current_price": self.current_prices.get('ETH/USDT', 3450),
                        "unrealized_pnl": round((self.current_prices.get('ETH/USDT', 3450) - 3200) * 5, 2),
                        "leverage": 2,
                        "margin": 5750
                    },
                    {
                        "id": "pos_3",
                        "symbol": "XAU/USD",
                        "side": "long",
                        "quantity": 10,
                        "entry_price": 2300,
                        "current_price": self.current_prices.get('XAU/USD', 2350),
                        "unrealized_pnl": round((self.current_prices.get('XAU/USD', 2350) - 2300) * 10, 2),
                        "leverage": 1,
                        "margin": 23000
                    }
                ]

                total_pnl = sum(p["unrealized_pnl"] for p in positions)
                total_margin = sum(p["margin"] for p in positions)

                positions_data = {
                    "positions": positions,
                    "total_unrealized_pnl": round(total_pnl, 2),
                    "total_margin": total_margin,
                    "positions_count": len(positions)
                }

                message = FeedMessage(
                    type=FeedType.POSITIONS.value,
                    exchange="all",
                    data=positions_data,
                    timestamp=datetime.now().isoformat()
                )

                await self._broadcast(FeedType.POSITIONS.value, message)

                await asyncio.sleep(3)  # Update every 3 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Positions stream error: {e}")
                await asyncio.sleep(3)

    async def _stream_balance(self):
        """Stream balance updates"""
        while self.is_streaming:
            try:
                total_equity = 150000 + random.uniform(-1000, 1000)
                available = total_equity - random.uniform(3000, 5000)
                margin = total_equity - available

                balance_data = {
                    "total_equity": round(total_equity, 2),
                    "available_balance": round(available, 2),
                    "margin_used": round(margin, 2),
                    "unrealized_pnl": round(random.uniform(-500, 1000), 2),
                    "currency": "USD",
                    "daily_pnl": round(random.uniform(-1000, 2000), 2),
                    "weekly_pnl": round(random.uniform(-2000, 5000), 2),
                    "monthly_pnl": round(random.uniform(-5000, 15000), 2)
                }

                message = FeedMessage(
                    type=FeedType.BALANCE.value,
                    exchange="all",
                    data=balance_data,
                    timestamp=datetime.now().isoformat()
                )

                await self._broadcast(FeedType.BALANCE.value, message)

                await asyncio.sleep(2)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Balance stream error: {e}")
                await asyncio.sleep(2)

    async def _stream_system_status(self):
        """Stream system status updates"""
        while self.is_streaming:
            try:
                # Get connected exchanges status
                exchanges = [
                    {"name": "Binance", "status": "connected", "latency": random.randint(10, 50)},
                    {"name": "MT5", "status": "connected", "latency": random.randint(20, 80)},
                    {"name": "Alpaca", "status": "connected", "latency": random.randint(30, 100)},
                    {"name": "Bybit", "status": "connected", "latency": random.randint(15, 60)}
                ]

                system_data = {
                    "status": "online",
                    "uptime": random.randint(3600, 86400),
                    "cpu_usage": round(random.uniform(10, 40), 1),
                    "memory_usage": round(random.uniform(30, 60), 1),
                    "exchanges": exchanges,
                    "auto_trading": True,
                    "ai_enabled": True,
                    "last_update": datetime.now().isoformat()
                }

                message = FeedMessage(
                    type=FeedType.SYSTEM.value,
                    exchange="all",
                    data=system_data,
                    timestamp=datetime.now().isoformat()
                )

                await self._broadcast(FeedType.SYSTEM.value, message)

                await asyncio.sleep(5)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"System status stream error: {e}")
                await asyncio.sleep(5)

    def get_latest_prices(self) -> Dict[str, float]:
        """Get latest prices"""
        return self.current_prices.copy()

    def get_price_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get price history for a symbol"""
        history = []
        if FeedType.TICKER.value in self.feed_history:
            for entry in self.feed_history[FeedType.TICKER.value][-limit:]:
                if symbol in entry.get("prices", {}):
                    history.append({
                        "price": entry["prices"][symbol],
                        "timestamp": entry["timestamp"]
                    })
        return history


# Global instance
live_feed_manager = LiveFeedManager()
