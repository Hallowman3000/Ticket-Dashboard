# -*- coding: utf-8 -*-
"""
MT5 Executor Module.

Provides a wrapper for MetaTrader 5 order execution with:
- Market order opening
- Position modification
- Position closing
- Position queries

All methods include error handling and logging.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

import MetaTrader5 as mt5

logger = logging.getLogger(__name__)


@dataclass
class PositionInfo:
    """
    Information about an open position.

    Attributes:
        ticket: Unique position identifier.
        symbol: Trading symbol.
        type: Position type (0=BUY, 1=SELL).
        volume: Position size in lots.
        price_open: Entry price.
        sl: Current stop loss.
        tp: Current take profit.
        profit: Current profit/loss.
        magic: Magic number identifying the EA.
    """
    ticket: int
    symbol: str
    type: int
    volume: float
    price_open: float
    sl: float
    tp: float
    profit: float
    magic: int

    @property
    def is_long(self) -> bool:
        """Check if position is a long (buy) position."""
        return self.type == mt5.ORDER_TYPE_BUY


class MT5Executor:
    """
    Wrapper for MetaTrader 5 trading operations.

    This class provides a clean interface for:
    - Opening market orders with SL/TP
    - Modifying existing positions
    - Closing positions
    - Querying open positions

    Attributes:
        magic_number: Unique identifier for this strategy's trades.
        slippage: Maximum allowed slippage in points.
    """

    def __init__(self, magic_number: int, slippage: int = 20):
        """
        Initialize the MT5 executor.

        Args:
            magic_number: Magic number to identify this strategy's trades.
            slippage: Maximum slippage in points (default 20).
        """
        self.magic_number = magic_number
        self.slippage = slippage

        logger.info(
            f"MT5Executor initialized: Magic={magic_number}, Slippage={slippage}"
        )

    def open_position(
        self,
        symbol: str,
        is_long: bool,
        volume: float,
        stop_loss: float,
        take_profit: float,
        comment: str = ""
    ) -> Optional[int]:
        """
        Open a new market position.

        Args:
            symbol: Trading symbol (e.g., "EURUSD").
            is_long: True for buy, False for sell.
            volume: Position size in lots.
            stop_loss: Stop loss price.
            take_profit: Take profit price.
            comment: Optional comment for the order.

        Returns:
            Position ticket number if successful, None otherwise.
        """
        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} not found")
            return None

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Failed to select symbol {symbol}")
                return None

        # Get current price
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.error(f"Failed to get tick for {symbol}")
            return None

        # Determine order type and price
        if is_long:
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
        else:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid

        # Prepare order request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": self.slippage,
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)

        if result is None:
            logger.error(f"Order send failed: {mt5.last_error()}")
            return None

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(
                f"Order failed: retcode={result.retcode}, "
                f"comment={result.comment}"
            )
            return None

        logger.info(
            f"Position opened: Ticket={result.order}, "
            f"{'LONG' if is_long else 'SHORT'} {volume} lots @ {price:.5f}, "
            f"SL={stop_loss:.5f}, TP={take_profit:.5f}"
        )

        return result.order

    def modify_position(
        self,
        ticket: int,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """
        Modify an existing position's SL/TP.

        Args:
            ticket: Position ticket number.
            stop_loss: New stop loss price (None to keep current).
            take_profit: New take profit price (None to keep current).

        Returns:
            True if modification successful, False otherwise.
        """
        # Get current position
        position = mt5.positions_get(ticket=ticket)
        if not position:
            logger.error(f"Position {ticket} not found")
            return False

        position = position[0]

        # Use current values if not specified
        new_sl = stop_loss if stop_loss is not None else position.sl
        new_tp = take_profit if take_profit is not None else position.tp

        # Skip if no change needed
        if new_sl == position.sl and new_tp == position.tp:
            return True

        # Prepare modification request
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": position.symbol,
            "sl": new_sl,
            "tp": new_tp,
        }

        # Send modification
        result = mt5.order_send(request)

        if result is None:
            logger.error(f"Position modify failed: {mt5.last_error()}")
            return False

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(
                f"Modify failed: retcode={result.retcode}, "
                f"comment={result.comment}"
            )
            return False

        logger.info(
            f"Position {ticket} modified: SL={new_sl:.5f}, TP={new_tp:.5f}"
        )

        return True

    def close_position(self, ticket: int) -> bool:
        """
        Close an open position.

        Args:
            ticket: Position ticket number.

        Returns:
            True if close successful, False otherwise.
        """
        # Get position info
        position = mt5.positions_get(ticket=ticket)
        if not position:
            logger.error(f"Position {ticket} not found")
            return False

        position = position[0]

        # Get current price
        tick = mt5.symbol_info_tick(position.symbol)
        if tick is None:
            logger.error(f"Failed to get tick for {position.symbol}")
            return False

        # Determine close type and price
        if position.type == mt5.ORDER_TYPE_BUY:
            close_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            close_type = mt5.ORDER_TYPE_BUY
            price = tick.ask

        # Prepare close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": close_type,
            "price": price,
            "deviation": self.slippage,
            "magic": self.magic_number,
            "comment": "Close by strategy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send close order
        result = mt5.order_send(request)

        if result is None:
            logger.error(f"Position close failed: {mt5.last_error()}")
            return False

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(
                f"Close failed: retcode={result.retcode}, "
                f"comment={result.comment}"
            )
            return False

        logger.info(
            f"Position {ticket} closed: {position.volume} lots @ {price:.5f}, "
            f"Profit={position.profit:.2f}"
        )

        return True

    def get_open_positions(
        self,
        symbol: Optional[str] = None
    ) -> List[PositionInfo]:
        """
        Get all open positions for this strategy.

        Args:
            symbol: Optional filter by symbol.

        Returns:
            List of PositionInfo objects for matching positions.
        """
        # Get all positions for this magic number
        if symbol:
            positions = mt5.positions_get(symbol=symbol)
        else:
            positions = mt5.positions_get()

        if positions is None:
            return []

        # Filter by magic number and convert to PositionInfo
        result = []
        for pos in positions:
            if pos.magic == self.magic_number:
                result.append(PositionInfo(
                    ticket=pos.ticket,
                    symbol=pos.symbol,
                    type=pos.type,
                    volume=pos.volume,
                    price_open=pos.price_open,
                    sl=pos.sl,
                    tp=pos.tp,
                    profit=pos.profit,
                    magic=pos.magic
                ))

        return result

    def close_all_positions(self, symbol: Optional[str] = None) -> int:
        """
        Close all positions for this strategy.

        Args:
            symbol: Optional filter by symbol.

        Returns:
            Number of positions successfully closed.
        """
        positions = self.get_open_positions(symbol)
        closed_count = 0

        for pos in positions:
            if self.close_position(pos.ticket):
                closed_count += 1

        logger.info(f"Closed {closed_count}/{len(positions)} positions")
        return closed_count
