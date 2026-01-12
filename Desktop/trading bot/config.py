# -*- coding: utf-8 -*-
"""
Configuration file for MT5 Trading Strategy.

Contains MT5 credentials (loaded from .env), trading parameters, and strategy settings.
Credentials are loaded securely from environment variables using python-dotenv.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import MetaTrader5 as mt5

# =============================================================================
# LOAD ENVIRONMENT VARIABLES
# =============================================================================
# Load .env file from the same directory as this config file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# =============================================================================
# MT5 ACCOUNT CREDENTIALS (from environment variables)
# =============================================================================
MT5_LOGIN = os.getenv("MT5_LOGIN", "")
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")

# Optional: Path to MT5 terminal (leave None for default installation)
MT5_PATH = os.getenv("MT5_PATH", None)


def validate_credentials() -> bool:
    """
    Validate that all required MT5 credentials are present.

    Returns:
        True if all credentials are valid, False otherwise.
    """
    missing = []

    if not MT5_LOGIN or MT5_LOGIN.strip() == "":
        missing.append("MT5_LOGIN")

    if not MT5_PASSWORD or MT5_PASSWORD.strip() == "":
        missing.append("MT5_PASSWORD")

    if not MT5_SERVER or MT5_SERVER.strip() == "":
        missing.append("MT5_SERVER")

    if missing:
        print("=" * 60)
        print("CONFIGURATION ERROR")
        print("=" * 60)
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print()
        print("Please ensure your .env file exists and contains:")
        print("  MT5_LOGIN=your_account_number")
        print("  MT5_PASSWORD=your_password")
        print("  MT5_SERVER=your_broker_server")
        print()
        print("See .env.template for an example.")
        print("=" * 60)
        return False

    return True


def get_mt5_login() -> int:
    """Get MT5 login as integer."""
    try:
        return int(MT5_LOGIN)
    except ValueError:
        print(f"CONFIGURATION ERROR: MT5_LOGIN must be a number, got: {MT5_LOGIN}")
        sys.exit(1)


# =============================================================================
# TRADING INSTRUMENT SETTINGS
# =============================================================================
SYMBOL = "EURUSD"  # Trading symbol
TIMEFRAME = mt5.TIMEFRAME_H1  # Timeframe for analysis (1 hour)
MAGIC_NUMBER = 234000  # Unique identifier for this strategy's trades
LOT_SIZE = 0.01  # Position size in lots

# =============================================================================
# INDICATOR PARAMETERS
# =============================================================================
EMA_PERIOD = 200  # Period for trend filter EMA
RSI_PERIOD = 14  # Period for RSI indicator
ATR_PERIOD = 14  # Period for ATR (volatility) indicator

# RSI thresholds for entry signals
RSI_OVERSOLD = 30  # RSI crossing above this triggers Long
RSI_OVERBOUGHT = 70  # RSI crossing below this triggers Short

# =============================================================================
# RISK MANAGEMENT PARAMETERS
# =============================================================================
ATR_SL_MULTIPLIER = 1.5  # Stop Loss = ATR * this multiplier
ATR_TP_MULTIPLIER = 2.0  # Take Profit = ATR * this multiplier

# Trailing stop settings
TRAILING_ATR_MULTIPLIER = 1.0  # Trailing stop distance in ATR units
BREAKEVEN_RR_RATIO = 1.0  # Move to breakeven at 1:1 risk-reward

# =============================================================================
# KILL SWITCH SETTINGS
# =============================================================================
EQUITY_DRAWDOWN_LIMIT = 0.05  # Maximum equity drawdown (5%) before kill switch

# =============================================================================
# DATA POLLING SETTINGS
# =============================================================================
BAR_CHECK_INTERVAL = 5  # Seconds between bar checks
BARS_TO_FETCH = 300  # Number of historical bars to fetch for indicators

# =============================================================================
# LOGGING SETTINGS
# =============================================================================
LOG_LEVEL = "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR
LOG_FILE = "trading_bot.log"  # Log file name
