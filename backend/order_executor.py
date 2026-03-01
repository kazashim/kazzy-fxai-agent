"""
Order Execution Module for Kazzy Agent
Handles order placement, management, and monitoring
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("OrderExecutor")


class OrderExecutor:
    """Order execution and management system"""

    def __init__(self, risk_manager):
        self.risk_manager = risk_manager
        self.active_orders: Dict[str, Dict] = {}
        self.order_history: List[Dict] = []
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds

    async def execute(self, exchange, symbol: str, side: str, quantity: float,
                    order_type: str = 'market', stop_loss: Optional[float] = None,
                    take_profit: Optional[float] = None) -> Optional[Dict]:
        """
        Execute a trade order with retry logic
        """
        order_id = None
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Create the order
                result = await exchange.create_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    order_type=order_type,
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )

                if result and result.get('id'):
                    order_id = result['id']
                    order_data = {
                        'id': order_id,
                        'symbol': symbol,
                        'side': side,
                        'quantity': quantity,
                        'entry_price': result.get('price', 0),
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'status': 'open',
                        'exchange': exchange.name,
                        'created_at': self._get_timestamp()
                    }

                    self.active_orders[order_id] = order_data
                    logger.info(f"✅ Order executed: {side.upper()} {quantity} {symbol} @ {result.get('price', 'market')}")

                    # Add stop loss and take profit as separate orders if supported
                    if stop_loss or take_profit:
                        await self._attach_exits(exchange, order_id, symbol, side, quantity, stop_loss, take_profit)

                    return result

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Order attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        logger.error(f"❌ Order execution failed after {self.max_retries} attempts: {last_error}")
        return None

    async def _attach_exits(self, exchange, order_id: str, symbol: str, side: str,
                          quantity: float, stop_loss: Optional[float],
                          take_profit: Optional[float]):
        """Attach stop loss and take profit orders"""
        try:
            # For some exchanges, these need to be set during order creation
            # This is a placeholder for additional logic
            logger.info(f"Exit orders noted for {order_id}: SL={stop_loss}, TP={take_profit}")
        except Exception as e:
            logger.error(f"Error attaching exit orders: {e}")

    async def close_position(self, exchange, position_id: str) -> bool:
        """Close an existing position"""
        try:
            # Get position info first
            positions = await exchange.get_positions()
            position = None

            for pos in positions:
                if str(pos.get('id')) == str(position_id):
                    position = pos
                    break

            if not position:
                logger.error(f"Position not found: {position_id}")
                return False

            # Close the position
            symbol = position.get('symbol')
            side = 'sell' if position.get('side') == 'buy' else 'buy'
            size = position.get('size', 0)

            result = await exchange.create_order(
                symbol=symbol,
                side=side,
                quantity=size,
                order_type='market'
            )

            if result:
                # Update order tracking
                if position_id in self.active_orders:
                    self.active_orders[position_id]['status'] = 'closed'
                    self.order_history.append(self.active_orders[position_id])
                    del self.active_orders[position_id]

                logger.info(f"✅ Position closed: {position_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False

    async def close_all_positions(self, exchange) -> int:
        """Close all open positions"""
        try:
            positions = await exchange.get_positions()
            closed_count = 0

            for pos in positions:
                if await self.close_position(exchange, str(pos.get('id'))):
                    closed_count += 1

            logger.info(f"Closed {closed_count} positions")
            return closed_count

        except Exception as e:
            logger.error(f"Error closing all positions: {e}")
            return 0

    async def cancel_order(self, exchange, order_id: str) -> bool:
        """Cancel a pending order"""
        try:
            result = await exchange.close_order(order_id)
            if result and order_id in self.active_orders:
                self.active_orders[order_id]['status'] = 'cancelled'
                self.order_history.append(self.active_orders[order_id])
                del self.active_orders[order_id]
            return result
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False

    async def modify_order(self, exchange, order_id: str, **updates) -> bool:
        """Modify an existing order"""
        try:
            # Cancel and recreate with new parameters
            await self.cancel_order(exchange, order_id)

            if 'symbol' in updates and 'side' in updates and 'quantity' in updates:
                result = await self.execute(
                    exchange=exchange,
                    symbol=updates['symbol'],
                    side=updates['side'],
                    quantity=updates['quantity'],
                    order_type=updates.get('order_type', 'market'),
                    stop_loss=updates.get('stop_loss'),
                    take_profit=updates.get('take_profit')
                )
                return result is not None

            return False

        except Exception as e:
            logger.error(f"Error modifying order: {e}")
            return False

    def get_active_orders(self) -> List[Dict]:
        """Get all active orders"""
        return list(self.active_orders.values())

    def get_order_history(self) -> List[Dict]:
        """Get order history"""
        return self.order_history

    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get a specific order"""
        return self.active_orders.get(order_id)

    async def monitor_orders(self, exchange) -> Dict[str, Any]:
        """Monitor and update order statuses"""
        try:
            open_orders = await exchange.get_open_orders()

            # Update local tracking
            for order in open_orders:
                order_id = str(order.get('id'))
                if order_id in self.active_orders:
                    self.active_orders[order_id]['status'] = 'open'

            # Check for filled orders
            filled = []
            for order_id, order_data in list(self.active_orders.items()):
                if order_data['status'] == 'open':
                    # Check if order is still open on exchange
                    still_open = any(str(o.get('id')) == order_id for o in open_orders)
                    if not still_open:
                        order_data['status'] = 'filled'
                        filled.append(order_id)

            return {
                'active': len(self.active_orders),
                'filled': len(filled),
                'orders': self.active_orders
            }

        except Exception as e:
            logger.error(f"Error monitoring orders: {e}")
            return {'active': 0, 'filled': 0, 'orders': {}}

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
