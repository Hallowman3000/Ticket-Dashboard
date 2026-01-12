# -*- coding: utf-8 -*-
"""
Strategy package for MT5 Trading Bot.

This package contains all the modular components for the trading strategy:
- indicators: Technical indicator calculations (EMA, RSI, ATR)
- signals: Entry signal generation logic
- risk_manager: Position sizing and trailing stop management
- executor: MT5 order execution wrapper
- kill_switch: Safety mechanism for equity protection
"""

from strategy.indicators import calculate_ema, calculate_rsi, calculate_atr
from strategy.signals import SignalGenerator, Signal
from strategy.risk_manager import RiskManager, TrailingStopManager
from strategy.executor import MT5Executor
from strategy.kill_switch import KillSwitch

__all__ = [
    'calculate_ema',
    'calculate_rsi',
    'calculate_atr',
    'SignalGenerator',
    'Signal',
    'RiskManager',
    'TrailingStopManager',
    'MT5Executor',
    'KillSwitch',
]
