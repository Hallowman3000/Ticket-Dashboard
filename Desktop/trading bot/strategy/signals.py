# -*- coding: utf-8 -*-
"""
Signal Generation Module.

Implements the entry signal logic based on:
- Trend Filter: Price must be above/below 200 EMA
- Entry Trigger: RSI crossing above 30 (Long) or below 70 (Short)
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np

from strategy.indicators import calculate_ema, calculate_rsi

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Enumeration of possible signal types."""
    NONE = 0
    LONG = 1
    SHORT = -1


@dataclass
class Signal:
    """
    Represents a trading signal.

    Attributes:
        signal_type: The type of signal (LONG, SHORT, or NONE).
        entry_price: The suggested entry price (current close).
        ema_value: Current EMA value for reference.
        rsi_value: Current RSI value for reference.
    """
    signal_type: SignalType
    entry_price: float
    ema_value: float
    rsi_value: float

    @property
    def is_valid(self) -> bool:
        """Check if signal is actionable."""
        return self.signal_type != SignalType.NONE


class SignalGenerator:
    """
    Generates trading signals based on trend and momentum conditions.

    Strategy Logic:
    ---------------
    LONG Entry:
        1. Price is ABOVE 200 EMA (uptrend filter)
        2. RSI crosses ABOVE 30 (momentum reversal from oversold)

    SHORT Entry:
        1. Price is BELOW 200 EMA (downtrend filter)
        2. RSI crosses BELOW 70 (momentum reversal from overbought)

    Attributes:
        ema_period: Period for the trend filter EMA.
        rsi_period: Period for RSI calculation.
        rsi_oversold: Threshold for long entry (default 30).
        rsi_overbought: Threshold for short entry (default 70).
    """

    def __init__(
        self,
        ema_period: int = 200,
        rsi_period: int = 14,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0
    ):
        """
        Initialize the signal generator.

        Args:
            ema_period: Period for trend filter EMA.
            rsi_period: Period for RSI indicator.
            rsi_oversold: RSI level for long entry trigger.
            rsi_overbought: RSI level for short entry trigger.
        """
        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought

        logger.info(
            f"SignalGenerator initialized: EMA={ema_period}, RSI={rsi_period}, "
            f"Oversold={rsi_oversold}, Overbought={rsi_overbought}"
        )

    def generate(
        self,
        close_prices: np.ndarray,
        current_price: Optional[float] = None
    ) -> Signal:
        """
        Generate a trading signal based on current market data.

        This method evaluates the trend filter (EMA) and momentum condition
        (RSI crossover) to determine if an entry signal should be generated.

        Args:
            close_prices: Array of historical close prices.
            current_price: Current price (defaults to last close).

        Returns:
            Signal object containing the signal type and reference values.
        """
        if len(close_prices) < max(self.ema_period, self.rsi_period) + 2:
            logger.warning("Insufficient data for signal generation")
            return Signal(
                signal_type=SignalType.NONE,
                entry_price=0.0,
                ema_value=0.0,
                rsi_value=0.0
            )

        # Calculate indicators
        ema = calculate_ema(close_prices, self.ema_period)
        rsi = calculate_rsi(close_prices, self.rsi_period)

        # Get current and previous values
        current_close = current_price if current_price else close_prices[-1]
        current_ema = ema[-1]
        current_rsi = rsi[-1]
        previous_rsi = rsi[-2]

        # Check for valid indicator values
        if np.isnan(current_ema) or np.isnan(current_rsi) or np.isnan(previous_rsi):
            logger.debug("Indicator values contain NaN, no signal generated")
            return Signal(
                signal_type=SignalType.NONE,
                entry_price=current_close,
                ema_value=current_ema if not np.isnan(current_ema) else 0.0,
                rsi_value=current_rsi if not np.isnan(current_rsi) else 0.0
            )

        signal_type = SignalType.NONE

        # =================================================================
        # LONG SIGNAL CONDITIONS
        # =================================================================
        # 1. Trend Filter: Price must be above EMA (uptrend)
        # 2. Entry Trigger: RSI crosses above oversold level (30)
        #    - Previous RSI <= 30 AND Current RSI > 30
        # =================================================================
        if current_close > current_ema:
            if previous_rsi <= self.rsi_oversold < current_rsi:
                signal_type = SignalType.LONG
                logger.info(
                    f"LONG Signal: Price {current_close:.5f} > EMA {current_ema:.5f}, "
                    f"RSI crossed above {self.rsi_oversold} ({previous_rsi:.2f} -> {current_rsi:.2f})"
                )

        # =================================================================
        # SHORT SIGNAL CONDITIONS
        # =================================================================
        # 1. Trend Filter: Price must be below EMA (downtrend)
        # 2. Entry Trigger: RSI crosses below overbought level (70)
        #    - Previous RSI >= 70 AND Current RSI < 70
        # =================================================================
        elif current_close < current_ema:
            if previous_rsi >= self.rsi_overbought > current_rsi:
                signal_type = SignalType.SHORT
                logger.info(
                    f"SHORT Signal: Price {current_close:.5f} < EMA {current_ema:.5f}, "
                    f"RSI crossed below {self.rsi_overbought} ({previous_rsi:.2f} -> {current_rsi:.2f})"
                )

        return Signal(
            signal_type=signal_type,
            entry_price=current_close,
            ema_value=current_ema,
            rsi_value=current_rsi
        )
