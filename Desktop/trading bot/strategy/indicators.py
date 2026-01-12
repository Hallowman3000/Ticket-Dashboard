# -*- coding: utf-8 -*-
"""
Technical Indicators Module.

Provides efficient calculations for:
- Exponential Moving Average (EMA)
- Relative Strength Index (RSI)
- Average True Range (ATR)

All functions are designed to work with NumPy arrays for performance.
"""

import numpy as np
from typing import Union


def calculate_ema(
    data: Union[np.ndarray, list],
    period: int
) -> np.ndarray:
    """
    Calculate Exponential Moving Average (EMA).

    The EMA gives more weight to recent prices, making it more responsive
    to new information compared to a Simple Moving Average.

    Args:
        data: Array of price data (typically close prices).
        period: EMA period (number of bars).

    Returns:
        NumPy array of EMA values. First (period-1) values will be NaN.

    Example:
        >>> closes = np.array([1.1, 1.2, 1.15, 1.18, 1.22])
        >>> ema = calculate_ema(closes, period=3)
    """
    data = np.asarray(data, dtype=np.float64)
    ema = np.full_like(data, np.nan)

    if len(data) < period:
        return ema

    # Initialize EMA with SMA for the first period
    ema[period - 1] = np.mean(data[:period])

    # EMA multiplier: 2 / (period + 1)
    multiplier = 2.0 / (period + 1)

    # Calculate EMA for remaining values
    for i in range(period, len(data)):
        ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1]

    return ema


def calculate_rsi(
    data: Union[np.ndarray, list],
    period: int = 14
) -> np.ndarray:
    """
    Calculate Relative Strength Index (RSI).

    RSI measures the speed and magnitude of recent price changes to
    evaluate overbought or oversold conditions. Values range from 0 to 100.

    Args:
        data: Array of price data (typically close prices).
        period: RSI period (default 14).

    Returns:
        NumPy array of RSI values. First 'period' values will be NaN.

    Example:
        >>> closes = np.array([44, 44.34, 44.09, 43.61, 44.33, 44.83])
        >>> rsi = calculate_rsi(closes, period=5)
    """
    data = np.asarray(data, dtype=np.float64)
    rsi = np.full_like(data, np.nan)

    if len(data) < period + 1:
        return rsi

    # Calculate price changes
    deltas = np.diff(data)

    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    # Calculate initial average gain/loss using SMA
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    # Calculate first RSI value
    if avg_loss == 0:
        rsi[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi[period] = 100.0 - (100.0 / (1.0 + rs))

    # Calculate subsequent RSI values using smoothed averages (Wilder's method)
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            rsi[i + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i + 1] = 100.0 - (100.0 / (1.0 + rs))

    return rsi


def calculate_atr(
    high: Union[np.ndarray, list],
    low: Union[np.ndarray, list],
    close: Union[np.ndarray, list],
    period: int = 14
) -> np.ndarray:
    """
    Calculate Average True Range (ATR).

    ATR measures market volatility by analyzing the range of price movement.
    It considers gaps by including the previous close in the calculation.

    Args:
        high: Array of high prices.
        low: Array of low prices.
        close: Array of close prices.
        period: ATR period (default 14).

    Returns:
        NumPy array of ATR values. First 'period' values will be NaN.

    Example:
        >>> high = np.array([48.7, 48.72, 48.9, 48.87, 48.82])
        >>> low = np.array([47.79, 48.14, 48.39, 48.37, 48.24])
        >>> close = np.array([48.16, 48.61, 48.75, 48.63, 48.74])
        >>> atr = calculate_atr(high, low, close, period=3)
    """
    high = np.asarray(high, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    close = np.asarray(close, dtype=np.float64)

    atr = np.full_like(close, np.nan)

    if len(close) < period + 1:
        return atr

    # Calculate True Range components
    # TR = max(High - Low, |High - Previous Close|, |Low - Previous Close|)
    tr = np.zeros(len(close))
    tr[0] = high[0] - low[0]  # First TR is just the range

    for i in range(1, len(close)):
        hl = high[i] - low[i]
        hpc = abs(high[i] - close[i - 1])
        lpc = abs(low[i] - close[i - 1])
        tr[i] = max(hl, hpc, lpc)

    # Calculate initial ATR as SMA of first 'period' TR values
    atr[period] = np.mean(tr[1:period + 1])

    # Calculate subsequent ATR values using smoothed average (Wilder's method)
    for i in range(period + 1, len(close)):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period

    return atr
