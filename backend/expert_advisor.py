"""
Kazzy Agent - Expert Advisor Integration Module

This module allows Kazzy Agent to:
1. Connect to MetaTrader 4/5 terminals with running EAs
2. Read EA-generated trading signals
3. Execute trades based on EA signals
4. Monitor and manage EA performance
5. Import/export EA strategies
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import os

logger = logging.getLogger("KazzyEA")

class EATradingMode(Enum):
    """EA Trading modes"""
    COPY_ONLY = "copy_only"  # Copy EA signals to Kazzy account
    HYBRID = "hybrid"        # EA + Kazzy AI combined
    AUTO_EXECUTE = "auto_execute"  # Execute all EA signals automatically

@dataclass
class EASignal:
    """Represents a trading signal from an Expert Advisor"""
    ea_name: str
    symbol: str
    action: str  # buy, sell, close
    lot_size: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    magic_number: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 100.0  # EA signals have 100% confidence
    source: str = "expert_advisor"

@dataclass
class ExpertAdvisor:
    """Represents a MetaTrader Expert Advisor"""
    name: str
    version: str
    symbol: str
    trading_mode: str
    is_active: bool
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0

class MTConnector:
    """MetaTrader 4/5 Connection Handler"""

    def __init__(self, mt_type: str = "MT5"):
        self.mt_type = mt_type  # MT4 or MT5
        self.is_connected = False
        self.terminal_info = {}
        self.account_info = {}
        self.positions = []
        self.orders = []

    async def connect(self, login: str = "", password: str = "", server: str = "", path: str = ""):
        """
        Connect to MetaTrader terminal

        Options:
        - Direct API: Use MetaTrader Python API (mt5 library)
        - Gateway: Connect via MT5API.cloud or similar service
        - File-based: Read from shared files (for local MT installations)
        """
        logger.info(f"Connecting to {self.mt_type}...")

        try:
            # Try direct MT5 connection first
            import MetaTrader5 as mt5
            if mt5.initialize():
                self.is_connected = True
                self.terminal_info = mt5.terminal_info()
                self.account_info = mt5.account_info()
                logger.info(f"Connected to {self.mt_type} successfully")
                return True
        except ImportError:
            logger.warning("MetaTrader5 library not installed, trying alternative methods")

        # Alternative: Try file-based connection (for local MT installations)
        if path:
            return await self._connect_via_file(path)

        # Alternative: Gateway connection
        logger.info("Using gateway connection method")
        self.is_connected = True  # Simulated for demo
        return True

    async def _connect_via_file(self, shared_path: str):
        """Connect via shared file system (for local MT installations)"""
        # MT4/MT5 writes orders to shared files
        signal_file = os.path.join(shared_path, "signals.dat")
        if os.path.exists(signal_file):
            logger.info(f"Found signal file at {signal_file}")
            return True
        return False

    async def disconnect(self):
        """Disconnect from MetaTrader"""
        try:
            import MetaTrader5 as mt5
            mt5.shutdown()
        except:
            pass
        self.is_connected = False

    async def get_positions(self) -> List[Dict]:
        """Get all open positions from MT"""
        if not self.is_connected:
            return []

        try:
            import MetaTrader5 as mt5
            positions = mt5.positions_get()
            return [
                {
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": "buy" if pos.type == 0 else "sell",
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "price_current": pos.price_current,
                    "profit": pos.profit,
                    "magic": pos.magic,
                    "time": pos.time,
                    "comment": pos.comment
                }
                for pos in positions
            ]
        except:
            # Demo data
            return [
                {
                    "ticket": 12345,
                    "symbol": "EURUSD",
                    "type": "buy",
                    "volume": 0.1,
                    "price_open": 1.0845,
                    "price_current": 1.0850,
                    "profit": 5.50,
                    "magic": 123456,
                    "time": datetime.now().timestamp(),
                    "comment": "EA: GridTrader"
                }
            ]

    async def get_orders(self) -> List[Dict]:
        """Get pending orders from MT"""
        if not self.is_connected:
            return []

        try:
            import MetaTrader5 as mt5
            orders = mt5.orders_get()
            return [
                {
                    "ticket": order.ticket,
                    "symbol": order.symbol,
                    "type": "buy_limit" if order.type == 2 else "sell_limit",
                    "volume": order.volume_initial,
                    "price": order.price_open,
                    "magic": order.magic
                }
                for order in orders
            ]
        except:
            return []

    async def get_expert_advisors(self) -> List[ExpertAdvisor]:
        """Get list of running Expert Advisors"""
        # In real implementation, this would query MT5 for running EAs
        # Based on magic numbers or comments in positions
        positions = await self.get_positions()

        # Group positions by EA (identified by magic number or comment)
        ea_dict = {}
        for pos in positions:
            ea_id = pos.get("comment", "Unknown EA")
            if ea_id.startswith("EA: "):
                ea_name = ea_id.replace("EA: ", "")
                if ea_name not in ea_dict:
                    ea_dict[ea_name] = {
                        "name": ea_name,
                        "trades": [],
                        "wins": 0,
                        "losses": 0
                    }
                ea_dict[ea_name]["trades"].append(pos)
                if pos["profit"] > 0:
                    ea_dict[ea_name]["wins"] += 1
                else:
                    ea_dict[ea_name]["losses"] += 1

        # Convert to ExpertAdvisor objects
        experts = []
        for name, data in ea_dict.items():
            total = data["wins"] + data["losses"]
            win_rate = (data["wins"] / total * 100) if total > 0 else 0

            experts.append(ExpertAdvisor(
                name=name,
                version="1.0",
                symbol="*",  # Multi-symbol
                trading_mode="active",
                is_active=True,
                total_trades=total,
                winning_trades=data["wins"],
                losing_trades=data["losses"],
                profit_factor=win_rate / 100 if win_rate > 0 else 0
            ))

        return experts

    async def execute_trade(self, symbol: str, action: str, volume: float,
                           price: float = 0, sl: float = 0, tp: float = 0,
                           magic: int = 0, comment: str = "") -> Dict:
        """Execute trade via MetaTrader"""
        if not self.is_connected:
            return {"success": False, "error": "Not connected to MT"}

        try:
            import MetaTrader5 as mt5

            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return {"success": False, "error": f"Symbol {symbol} not found"}

            if not symbol_info.visible:
                mt5.symbol_select(symbol, True)

            point = symbol_info.point

            request = {
                "action": mt5.TRADE_ACTION_DEAL if action in ["buy", "sell"] else mt5.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL,
                "price": price if price > 0 else mt5.symbol_info_tick(symbol).ask,
                "deviation": 20,
                "magic": magic,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            if sl > 0:
                request["sl"] = sl
            if tp > 0:
                request["tp"] = tp

            result = mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return {
                    "success": True,
                    "order_id": result.order,
                    "result": result._asdict()
                }
            else:
                return {
                    "success": False,
                    "error": result.comment
                }

        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return {"success": False, "error": str(e)}


class EAIntegrationManager:
    """Manages Expert Advisor integration and signal processing"""

    def __init__(self):
        self.mt4_connector: Optional[MTConnector] = None
        self.mt5_connector: Optional[MTConnector] = None
        self.ea_signals: List[EASignal] = []
        self.trading_mode = EATradingMode.COPY_ONLY
        self.signal_callbacks: List[Callable] = []
        self.is_monitoring = False

    async def connect_mt4(self, path: str = "") -> bool:
        """Connect to MetaTrader 4"""
        self.mt4_connector = MTConnector("MT4")
        return await self.mt4_connector.connect(path=path)

    async def connect_mt5(self, login: str = "", password: str = "",
                         server: str = "", path: str = "") -> bool:
        """Connect to MetaTrader 5"""
        self.mt5_connector = MTConnector("MT5")
        return await self.mt5_connector.connect(
            login=login, password=password, server=server, path=path
        )

    def set_trading_mode(self, mode: EATradingMode):
        """Set EA trading mode"""
        self.trading_mode = mode
        logger.info(f"EA Trading mode set to: {mode.value}")

    def register_signal_callback(self, callback: Callable):
        """Register callback for EA signals"""
        self.signal_callbacks.append(callback)

    async def start_monitoring(self):
        """Start monitoring EA signals"""
        self.is_monitoring = True
        logger.info("Started EA monitoring")

        while self.is_monitoring:
            await self._poll_ea_signals()
            await asyncio.sleep(1)  # Poll every second

    async def stop_monitoring(self):
        """Stop monitoring EA signals"""
        self.is_monitoring = False
        logger.info("Stopped EA monitoring")

    async def _poll_ea_signals(self):
        """Poll for new EA signals from MetaTrader"""
        # Check MT5 first
        if self.mt5_connector and self.mt5_connector.is_connected:
            positions = await self.mt5_connector.get_positions()

            for pos in positions:
                # Check if this is an EA position (has EA comment)
                if pos.get("comment", "").startswith("EA:"):
                    signal = EASignal(
                        ea_name=pos["comment"].replace("EA: ", ""),
                        symbol=pos["symbol"],
                        action="buy" if pos["type"] == "buy" else "sell",
                        lot_size=pos["volume"],
                        magic_number=pos["magic"],
                        timestamp=datetime.fromtimestamp(pos["time"]).isoformat()
                    )

                    # Process signal based on trading mode
                    await self._process_ea_signal(signal)

        # Check MT4
        if self.mt4_connector and self.mt4_connector.is_connected:
            positions = await self.mt4_connector.get_positions()
            # Similar processing for MT4...

    async def _process_ea_signal(self, signal: EASignal):
        """Process an EA signal based on trading mode"""
        logger.info(f"EA Signal: {signal.ea_name} - {signal.action} {signal.symbol}")

        # Add to signal history
        self.ea_signals.append(signal)
        if len(self.ea_signals) > 1000:
            self.ea_signals = self.ea_signals[-1000:]

        # Execute based on mode
        if self.trading_mode == EATradingMode.COPY_ONLY:
            # Just copy - execute same trade on Kazzy account
            await self._execute_ea_trade(signal)

        elif self.trading_mode == EATradingMode.AUTO_EXECUTE:
            # Execute all EA signals automatically
            await self._execute_ea_trade(signal)

        elif self.trading_mode == EATradingMode.HYBRID:
            # Combine EA signal with Kazzy AI analysis
            await self._hybrid_trade(signal)

        # Call registered callbacks
        for callback in self.signal_callbacks:
            try:
                callback(signal)
            except Exception as e:
                logger.error(f"Signal callback error: {e}")

    async def _execute_ea_trade(self, signal: EASignal):
        """Execute EA signal as a trade"""
        # This would connect to the exchange connectors
        logger.info(f"Executing EA trade: {signal.action} {signal.symbol} {signal.lot_size}")
        # Trade execution would go through exchange_connectors

    async def _hybrid_trade(self, signal: EASignal):
        """Hybrid mode: Validate EA signal with Kazzy AI"""
        # Get AI analysis for the signal
        logger.info(f"Hybrid mode: Validating EA signal with AI")
        # AI analysis would go here

    async def get_ea_performance(self) -> Dict[str, Any]:
        """Get performance statistics for all EAs"""
        performance = {
            "total_signals": len(self.ea_signals),
            "by_ea": {},
            "by_symbol": {}
        }

        for signal in self.ea_signals:
            # Group by EA
            if signal.ea_name not in performance["by_ea"]:
                performance["by_ea"][signal.ea_name] = {
                    "signals": 0,
                    "buy_signals": 0,
                    "sell_signals": 0
                }
            performance["by_ea"][signal.ea_name]["signals"] += 1
            if signal.action == "buy":
                performance["by_ea"][signal.ea_name]["buy_signals"] += 1
            else:
                performance["by_ea"][signal.ea_name]["sell_signals"] += 1

            # Group by symbol
            if signal.symbol not in performance["by_symbol"]:
                performance["by_symbol"][signal.symbol] = {"signals": 0}
            performance["by_symbol"][signal.symbol]["signals"] += 1

        return performance

    async def export_ea_signals(self, filepath: str):
        """Export EA signals to file"""
        with open(filepath, 'w') as f:
            json.dump([
                {
                    "ea_name": s.ea_name,
                    "symbol": s.symbol,
                    "action": s.action,
                    "lot_size": s.lot_size,
                    "stop_loss": s.stop_loss,
                    "take_profit": s.take_profit,
                    "timestamp": s.timestamp
                }
                for s in self.ea_signals
            ], f, indent=2)
        logger.info(f"Exported {len(self.ea_signals)} signals to {filepath}")

    async def import_ea_signals(self, filepath: str):
        """Import EA signals from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        for item in data:
            signal = EASignal(
                ea_name=item["ea_name"],
                symbol=item["symbol"],
                action=item["action"],
                lot_size=item["lot_size"],
                stop_loss=item.get("stop_loss"),
                take_profit=item.get("take_profit"),
                timestamp=item.get("timestamp", datetime.now().isoformat())
            )
            self.ea_signals.append(signal)

        logger.info(f"Imported {len(data)} signals from {filepath}")


# Global instance
ea_manager = EAIntegrationManager()


# Example EA signal parser for common formats
class EASignalParser:
    """Parse EA signals from various formats"""

    @staticmethod
    def parse_mt5_signal(position_data: Dict) -> EASignal:
        """Parse signal from MT5 position data"""
        return EASignal(
            ea_name=position_data.get("comment", "Unknown").replace("EA: ", ""),
            symbol=position_data["symbol"],
            action="buy" if position_data.get("type") == 0 else "sell",
            lot_size=position_data.get("volume", 0.01),
            stop_loss=position_data.get("sl"),
            take_profit=position_data.get("tp"),
            magic_number=position_data.get("magic", 0)
        )

    @staticmethod
    def parse_csignal(data: Dict) -> EASignal:
        """Parse from cSignal format (common EA output)"""
        return EASignal(
            ea_name=data.get("ea_name", "cSignal EA"),
            symbol=data["symbol"],
            action=data["action"],
            lot_size=data.get("lot", 0.01),
            stop_loss=data.get("stop_loss"),
            take_profit=data.get("take_profit"),
            confidence=data.get("confidence", 100)
        )

    @staticmethod
    def parse_json_signal(data: Dict) -> EASignal:
        """Parse from generic JSON format"""
        return EASignal(
            ea_name=data.get("expert", data.get("ea", "Unknown")),
            symbol=data["symbol"],
            action=data["cmd"] if "cmd" in data else data["action"],
            lot_size=data.get("volume", data.get("lots", 0.01)),
            stop_loss=data.get("sl", data.get("stoploss")),
            take_profit=data.get("tp", data.get("takeprofit"))
        )
