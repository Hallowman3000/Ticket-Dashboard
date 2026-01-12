# -*- coding: utf-8 -*-
"""
Kill Switch Module.

Safety mechanism to protect account equity:
- Monitors session equity vs current equity
- Triggers when equity drops by specified percentage (default 5%)
- Closes all positions and disables trading when triggered
"""

import logging
from typing import Optional
import MetaTrader5 as mt5

logger = logging.getLogger(__name__)


class KillSwitch:
    """
    Safety mechanism to protect account from excessive drawdown.

    Attributes:
        drawdown_limit: Maximum allowed drawdown as decimal (0.05 = 5%).
        magic_number: Magic number to identify positions to close.
    """

    def __init__(self, drawdown_limit: float = 0.05, magic_number: int = 0):
        self.drawdown_limit = drawdown_limit
        self.magic_number = magic_number
        self._starting_equity: Optional[float] = None
        self._is_triggered: bool = False
        self._is_initialized: bool = False
        logger.info(f"KillSwitch initialized: Drawdown limit={drawdown_limit * 100:.1f}%")

    def initialize(self) -> bool:
        """Initialize by recording starting equity at session start."""
        account_info = mt5.account_info()
        if account_info is None:
            logger.error("Failed to get account info for kill switch")
            return False

        self._starting_equity = account_info.equity
        self._is_triggered = False
        self._is_initialized = True
        logger.info(f"KillSwitch armed: Starting equity=${self._starting_equity:.2f}")
        return True

    def check(self) -> bool:
        """Check if kill switch should trigger. Returns True if triggered."""
        if self._is_triggered:
            return True

        if not self._is_initialized or self._starting_equity is None:
            return False

        account_info = mt5.account_info()
        if account_info is None:
            self._is_triggered = True
            return True

        drawdown = (self._starting_equity - account_info.equity) / self._starting_equity

        if drawdown >= self.drawdown_limit:
            logger.critical(f"KILL SWITCH TRIGGERED! Drawdown {drawdown*100:.2f}%")
            self._is_triggered = True
            return True

        return False

    def execute_kill(self) -> int:
        """Close all positions. Returns count of positions closed."""
        if not self._is_triggered:
            return 0

        logger.critical("EXECUTING KILL SWITCH - Closing all positions")
        positions = mt5.positions_get()
        if positions is None:
            return 0

        closed_count = 0
        for pos in positions:
            if self.magic_number > 0 and pos.magic != self.magic_number:
                continue

            tick = mt5.symbol_info_tick(pos.symbol)
            if tick is None:
                continue

            close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": pos.ticket,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": close_type,
                "price": price,
                "deviation": 50,
                "magic": pos.magic,
                "comment": "KILL SWITCH",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                closed_count += 1

        logger.critical(f"Kill switch: {closed_count} positions closed")
        return closed_count

    @property
    def is_triggered(self) -> bool:
        return self._is_triggered

    @property
    def starting_equity(self) -> Optional[float]:
        return self._starting_equity
