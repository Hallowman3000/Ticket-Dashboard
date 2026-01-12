# -*- coding: utf-8 -*-
"""
Risk Management Module.

Provides:
- Initial Stop Loss and Take Profit calculation based on ATR
- Trailing stop management with directional constraint
- Breakeven trigger at 1:1 risk-reward ratio
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

from strategy.indicators import calculate_atr
from strategy.signals import SignalType

logger = logging.getLogger(__name__)


@dataclass
class RiskLevels:
    """
    Contains calculated risk levels for a trade.

    Attributes:
        stop_loss: Initial stop loss price.
        take_profit: Take profit price.
        atr_value: ATR value used for calculations.
        risk_distance: Distance from entry to stop loss (in price).
    """
    stop_loss: float
    take_profit: float
    atr_value: float
    risk_distance: float


class RiskManager:
    """
    Calculates initial Stop Loss and Take Profit levels based on ATR.

    The ATR-based approach adapts risk levels to current market volatility:
    - Stop Loss = Entry ± (ATR × SL_MULTIPLIER)
    - Take Profit = Entry ± (ATR × TP_MULTIPLIER)

    Attributes:
        atr_period: Period for ATR calculation.
        sl_multiplier: ATR multiplier for stop loss distance.
        tp_multiplier: ATR multiplier for take profit distance.
    """

    def __init__(
        self,
        atr_period: int = 14,
        sl_multiplier: float = 1.5,
        tp_multiplier: float = 2.0
    ):
        """
        Initialize the risk manager.

        Args:
            atr_period: Period for ATR calculation.
            sl_multiplier: Multiplier for stop loss (e.g., 1.5 = 1.5 × ATR).
            tp_multiplier: Multiplier for take profit (e.g., 2.0 = 2.0 × ATR).
        """
        self.atr_period = atr_period
        self.sl_multiplier = sl_multiplier
        self.tp_multiplier = tp_multiplier

        logger.info(
            f"RiskManager initialized: ATR={atr_period}, "
            f"SL={sl_multiplier}x ATR, TP={tp_multiplier}x ATR"
        )

    def calculate_levels(
        self,
        signal_type: SignalType,
        entry_price: float,
        high_prices: np.ndarray,
        low_prices: np.ndarray,
        close_prices: np.ndarray
    ) -> Optional[RiskLevels]:
        """
        Calculate stop loss and take profit levels for a new trade.

        Args:
            signal_type: LONG or SHORT signal type.
            entry_price: The entry price of the trade.
            high_prices: Array of high prices for ATR calculation.
            low_prices: Array of low prices for ATR calculation.
            close_prices: Array of close prices for ATR calculation.

        Returns:
            RiskLevels object with calculated SL/TP, or None if invalid.
        """
        if signal_type == SignalType.NONE:
            return None

        # Calculate ATR
        atr = calculate_atr(high_prices, low_prices, close_prices, self.atr_period)
        current_atr = atr[-1]

        if np.isnan(current_atr) or current_atr <= 0:
            logger.warning("Invalid ATR value, cannot calculate risk levels")
            return None

        # Calculate distances
        sl_distance = current_atr * self.sl_multiplier
        tp_distance = current_atr * self.tp_multiplier

        # Calculate levels based on trade direction
        if signal_type == SignalType.LONG:
            stop_loss = entry_price - sl_distance
            take_profit = entry_price + tp_distance
        else:  # SHORT
            stop_loss = entry_price + sl_distance
            take_profit = entry_price - tp_distance

        logger.info(
            f"Risk levels calculated for {signal_type.name}: "
            f"Entry={entry_price:.5f}, SL={stop_loss:.5f}, TP={take_profit:.5f}, "
            f"ATR={current_atr:.5f}"
        )

        return RiskLevels(
            stop_loss=stop_loss,
            take_profit=take_profit,
            atr_value=current_atr,
            risk_distance=sl_distance
        )


@dataclass
class TrailingState:
    """
    Tracks the state of trailing stop for a position.

    Attributes:
        ticket: Position ticket number.
        entry_price: Original entry price.
        initial_sl: Initial stop loss price.
        current_sl: Current stop loss price (after trailing).
        risk_distance: Original risk distance (entry to SL).
        is_breakeven: Whether position has moved to breakeven.
        is_trailing: Whether trailing stop is active.
    """
    ticket: int
    entry_price: float
    initial_sl: float
    current_sl: float
    risk_distance: float
    is_breakeven: bool = False
    is_trailing: bool = False


class TrailingStopManager:
    """
    Manages trailing stops for open positions.

    Features:
    - Breakeven trigger: Moves SL to entry when trade reaches 1:1 R:R
    - ATR-based trailing: Trails stop by ATR distance, only in profit direction
    - Directional constraint: Stop can only move in the direction of profit

    Attributes:
        breakeven_rr: Risk-reward ratio to trigger breakeven (default 1.0).
        trailing_atr_mult: ATR multiplier for trailing distance.
    """

    def __init__(
        self,
        breakeven_rr: float = 1.0,
        trailing_atr_mult: float = 1.0
    ):
        """
        Initialize the trailing stop manager.

        Args:
            breakeven_rr: R:R ratio to trigger breakeven move.
            trailing_atr_mult: ATR multiplier for trailing stop distance.
        """
        self.breakeven_rr = breakeven_rr
        self.trailing_atr_mult = trailing_atr_mult
        self._positions: dict[int, TrailingState] = {}

        logger.info(
            f"TrailingStopManager initialized: Breakeven at {breakeven_rr}:1 R:R, "
            f"Trailing distance={trailing_atr_mult}x ATR"
        )

    def register_position(
        self,
        ticket: int,
        entry_price: float,
        stop_loss: float,
        risk_distance: float
    ) -> None:
        """
        Register a new position for trailing stop management.

        Args:
            ticket: Position ticket number.
            entry_price: Entry price of the position.
            stop_loss: Initial stop loss price.
            risk_distance: Distance from entry to stop loss.
        """
        self._positions[ticket] = TrailingState(
            ticket=ticket,
            entry_price=entry_price,
            initial_sl=stop_loss,
            current_sl=stop_loss,
            risk_distance=risk_distance
        )
        logger.debug(f"Position {ticket} registered for trailing management")

    def unregister_position(self, ticket: int) -> None:
        """Remove a closed position from tracking."""
        if ticket in self._positions:
            del self._positions[ticket]
            logger.debug(f"Position {ticket} unregistered from trailing management")

    def update(
        self,
        ticket: int,
        current_price: float,
        current_atr: float,
        is_long: bool
    ) -> Optional[float]:
        """
        Update trailing stop for a position and return new SL if changed.

        The trailing stop logic works as follows:
        1. Check if breakeven should be triggered (1:1 R:R reached)
        2. If already at breakeven, check if trailing stop should move
        3. Trailing stop only moves in the direction of profit

        Args:
            ticket: Position ticket number.
            current_price: Current market price.
            current_atr: Current ATR value.
            is_long: True if long position, False if short.

        Returns:
            New stop loss price if it should be updated, None otherwise.
        """
        if ticket not in self._positions:
            logger.warning(f"Position {ticket} not found in trailing manager")
            return None

        state = self._positions[ticket]
        new_sl = None

        # Calculate current profit in terms of risk distance
        if is_long:
            profit_distance = current_price - state.entry_price
        else:
            profit_distance = state.entry_price - current_price

        profit_rr = profit_distance / state.risk_distance if state.risk_distance > 0 else 0

        # =================================================================
        # BREAKEVEN LOGIC
        # =================================================================
        # Trigger breakeven when trade reaches the specified R:R ratio
        # Move stop loss to entry price to lock in a risk-free trade
        # =================================================================
        if not state.is_breakeven and profit_rr >= self.breakeven_rr:
            state.is_breakeven = True
            state.is_trailing = True
            state.current_sl = state.entry_price
            new_sl = state.entry_price

            logger.info(
                f"Position {ticket}: BREAKEVEN triggered at {self.breakeven_rr}:1 R:R, "
                f"SL moved to entry {state.entry_price:.5f}"
            )

        # =================================================================
        # TRAILING STOP LOGIC
        # =================================================================
        # Once at breakeven, trail the stop using ATR distance
        # IMPORTANT: Stop can only move in the direction of profit
        # - Long: Stop can only move UP
        # - Short: Stop can only move DOWN
        # =================================================================
        elif state.is_trailing:
            trailing_distance = current_atr * self.trailing_atr_mult

            if is_long:
                # For long positions: trail below current price
                potential_sl = current_price - trailing_distance
                # Only update if new SL is HIGHER than current SL
                if potential_sl > state.current_sl:
                    new_sl = potential_sl
                    logger.info(
                        f"Position {ticket}: Trailing SL updated "
                        f"{state.current_sl:.5f} -> {new_sl:.5f}"
                    )
                    state.current_sl = new_sl
            else:
                # For short positions: trail above current price
                potential_sl = current_price + trailing_distance
                # Only update if new SL is LOWER than current SL
                if potential_sl < state.current_sl:
                    new_sl = potential_sl
                    logger.info(
                        f"Position {ticket}: Trailing SL updated "
                        f"{state.current_sl:.5f} -> {new_sl:.5f}"
                    )
                    state.current_sl = new_sl

        return new_sl

    def get_state(self, ticket: int) -> Optional[TrailingState]:
        """Get the current trailing state for a position."""
        return self._positions.get(ticket)

    def clear_all(self) -> None:
        """Clear all tracked positions."""
        self._positions.clear()
        logger.info("All positions cleared from trailing manager")
