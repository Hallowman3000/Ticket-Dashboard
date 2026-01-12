# -*- coding: utf-8 -*-
"""
MT5 Trading Bot - Main Entry Point.

Event-driven trading strategy with:
- Trend filter (200 EMA)
- RSI crossover entries
- ATR-based risk management
- Trailing stops with breakeven
- Kill switch for equity protection

Usage:
    python main.py
"""

import logging
import signal
import sys
import time
from datetime import datetime
from typing import Optional

import MetaTrader5 as mt5
import numpy as np

import config
from strategy import (
    SignalGenerator,
    SignalType,
    RiskManager,
    TrailingStopManager,
    MT5Executor,
    KillSwitch,
    calculate_atr,
)


# =============================================================================
# LOGGING SETUP
# =============================================================================
def setup_logging() -> logging.Logger:
    """Configure logging for the trading bot."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logging.getLogger(__name__)


logger = setup_logging()


# =============================================================================
# MT5 INITIALIZATION
# =============================================================================
def initialize_mt5() -> bool:
    """
    Initialize connection to MetaTrader 5.

    Returns:
        True if connection successful, False otherwise.
    """
    # Initialize MT5
    init_params = {}
    if config.MT5_PATH:
        init_params['path'] = config.MT5_PATH

    if not mt5.initialize(**init_params):
        logger.error(f"MT5 initialization failed: {mt5.last_error()}")
        return False

    # Login to account
    if not mt5.login(
        login=config.get_mt5_login(),
        password=config.MT5_PASSWORD,
        server=config.MT5_SERVER
    ):
        logger.error(f"MT5 login failed: {mt5.last_error()}")
        mt5.shutdown()
        return False

    # Get account info
    account = mt5.account_info()
    if account:
        logger.info(
            f"Connected to MT5: Account #{account.login}, "
            f"Balance: ${account.balance:.2f}, Server: {account.server}"
        )

    # Verify symbol is available
    symbol_info = mt5.symbol_info(config.SYMBOL)
    if symbol_info is None:
        logger.error(f"Symbol {config.SYMBOL} not found")
        mt5.shutdown()
        return False

    if not symbol_info.visible:
        if not mt5.symbol_select(config.SYMBOL, True):
            logger.error(f"Failed to select symbol {config.SYMBOL}")
            mt5.shutdown()
            return False

    logger.info(f"Symbol {config.SYMBOL} ready for trading")
    return True


# =============================================================================
# DATA FETCHING
# =============================================================================
def fetch_ohlc_data() -> Optional[dict]:
    """
    Fetch OHLC data from MT5.

    Returns:
        Dictionary with open, high, low, close arrays, or None on error.
    """
    rates = mt5.copy_rates_from_pos(
        config.SYMBOL,
        config.TIMEFRAME,
        0,  # Start from current bar
        config.BARS_TO_FETCH
    )

    if rates is None or len(rates) == 0:
        logger.error(f"Failed to fetch rates: {mt5.last_error()}")
        return None

    return {
        'open': np.array([r['open'] for r in rates]),
        'high': np.array([r['high'] for r in rates]),
        'low': np.array([r['low'] for r in rates]),
        'close': np.array([r['close'] for r in rates]),
        'time': np.array([r['time'] for r in rates]),
    }


def get_current_bar_time() -> Optional[int]:
    """Get the timestamp of the current bar."""
    rates = mt5.copy_rates_from_pos(config.SYMBOL, config.TIMEFRAME, 0, 1)
    if rates is None or len(rates) == 0:
        return None
    return rates[0]['time']


# =============================================================================
# EVENT-DRIVEN BAR PROCESSING
# =============================================================================
class TradingBot:
    """
    Main trading bot class implementing event-driven bar processing.

    The on_bar method is called each time a new bar completes. It:
    1. Checks the kill switch
    2. Fetches latest OHLC data
    3. Manages existing positions (trailing/breakeven)
    4. Generates new signals
    5. Executes trades if conditions are met
    """

    def __init__(self):
        """Initialize all strategy components."""
        # Initialize components
        self.signal_generator = SignalGenerator(
            ema_period=config.EMA_PERIOD,
            rsi_period=config.RSI_PERIOD,
            rsi_oversold=config.RSI_OVERSOLD,
            rsi_overbought=config.RSI_OVERBOUGHT
        )

        self.risk_manager = RiskManager(
            atr_period=config.ATR_PERIOD,
            sl_multiplier=config.ATR_SL_MULTIPLIER,
            tp_multiplier=config.ATR_TP_MULTIPLIER
        )

        self.trailing_manager = TrailingStopManager(
            breakeven_rr=config.BREAKEVEN_RR_RATIO,
            trailing_atr_mult=config.TRAILING_ATR_MULTIPLIER
        )

        self.executor = MT5Executor(
            magic_number=config.MAGIC_NUMBER,
            slippage=20
        )

        self.kill_switch = KillSwitch(
            drawdown_limit=config.EQUITY_DRAWDOWN_LIMIT,
            magic_number=config.MAGIC_NUMBER
        )

        self._last_bar_time: Optional[int] = None
        self._is_running: bool = False

        logger.info("TradingBot initialized with all components")

    def on_bar(self) -> None:
        """
        Event handler called when a new bar completes.

        This is the core event-driven logic that processes each bar:

        1. KILL SWITCH CHECK
           - Verify account equity is within acceptable limits
           - If triggered, close all positions and stop trading

        2. DATA FETCH
           - Get latest OHLC data for indicator calculations

        3. POSITION MANAGEMENT
           - Update trailing stops for existing positions
           - Check for breakeven triggers

        4. SIGNAL GENERATION
           - Evaluate trend filter (price vs EMA)
           - Check RSI crossover conditions

        5. TRADE EXECUTION
           - If valid signal and no existing position, open new trade
           - Calculate SL/TP based on ATR
        """
        # =====================================================================
        # STEP 1: KILL SWITCH CHECK
        # =====================================================================
        if self.kill_switch.check():
            logger.critical("Kill switch active - stopping all trading")
            self.kill_switch.execute_kill()
            self._is_running = False
            return

        # =====================================================================
        # STEP 2: FETCH OHLC DATA
        # =====================================================================
        data = fetch_ohlc_data()
        if data is None:
            logger.error("Failed to fetch OHLC data, skipping bar")
            return

        close_prices = data['close']
        high_prices = data['high']
        low_prices = data['low']

        current_price = close_prices[-1]
        logger.debug(f"Processing bar: Price={current_price:.5f}")

        # Calculate current ATR for trailing stops
        atr = calculate_atr(high_prices, low_prices, close_prices, config.ATR_PERIOD)
        current_atr = atr[-1] if not np.isnan(atr[-1]) else 0

        # =====================================================================
        # STEP 3: MANAGE EXISTING POSITIONS
        # =====================================================================
        positions = self.executor.get_open_positions(config.SYMBOL)

        for pos in positions:
            # Update trailing stop
            new_sl = self.trailing_manager.update(
                ticket=pos.ticket,
                current_price=current_price,
                current_atr=current_atr,
                is_long=pos.is_long
            )

            # Modify position if trailing stop updated
            if new_sl is not None:
                self.executor.modify_position(pos.ticket, stop_loss=new_sl)

        # =====================================================================
        # STEP 4: SIGNAL GENERATION
        # =====================================================================
        # Only generate signals if no open positions
        if len(positions) > 0:
            logger.debug(f"Position already open, skipping signal generation")
            return

        signal = self.signal_generator.generate(close_prices, current_price)

        # =====================================================================
        # STEP 5: TRADE EXECUTION
        # =====================================================================
        if not signal.is_valid:
            logger.debug(
                f"No signal: RSI={signal.rsi_value:.2f}, "
                f"EMA={signal.ema_value:.5f}, Price={current_price:.5f}"
            )
            return

        # Calculate risk levels
        risk_levels = self.risk_manager.calculate_levels(
            signal_type=signal.signal_type,
            entry_price=signal.entry_price,
            high_prices=high_prices,
            low_prices=low_prices,
            close_prices=close_prices
        )

        if risk_levels is None:
            logger.warning("Could not calculate risk levels, skipping trade")
            return

        # Execute trade
        is_long = signal.signal_type == SignalType.LONG
        ticket = self.executor.open_position(
            symbol=config.SYMBOL,
            is_long=is_long,
            volume=config.LOT_SIZE,
            stop_loss=risk_levels.stop_loss,
            take_profit=risk_levels.take_profit,
            comment=f"{'LONG' if is_long else 'SHORT'} RSI+EMA"
        )

        if ticket:
            # Register for trailing stop management
            self.trailing_manager.register_position(
                ticket=ticket,
                entry_price=signal.entry_price,
                stop_loss=risk_levels.stop_loss,
                risk_distance=risk_levels.risk_distance
            )
            logger.info(f"Trade executed: Ticket={ticket}")

    def run(self) -> None:
        """
        Main trading loop.

        Polls for new bars and calls on_bar when a new bar is detected.
        Uses bar completion detection to ensure we only process complete bars.
        """
        logger.info("=" * 60)
        logger.info("TRADING BOT STARTED")
        logger.info(f"Symbol: {config.SYMBOL}, Timeframe: {config.TIMEFRAME}")
        logger.info("=" * 60)

        # Initialize kill switch
        if not self.kill_switch.initialize():
            logger.error("Kill switch initialization failed")
            return

        self._is_running = True
        self._last_bar_time = get_current_bar_time()

        try:
            while self._is_running:
                # Check for new bar
                current_bar_time = get_current_bar_time()

                if current_bar_time and current_bar_time != self._last_bar_time:
                    # New bar detected
                    logger.info(
                        f"New bar detected: {datetime.fromtimestamp(current_bar_time)}"
                    )
                    self._last_bar_time = current_bar_time

                    # Process the new bar
                    self.on_bar()

                # Sleep before next check
                time.sleep(config.BAR_CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")

        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Clean shutdown of the trading bot."""
        logger.info("Shutting down trading bot...")
        self._is_running = False

        # Log final account state
        account = mt5.account_info()
        if account:
            logger.info(
                f"Final account state: Balance=${account.balance:.2f}, "
                f"Equity=${account.equity:.2f}"
            )

        # Shutdown MT5
        mt5.shutdown()
        logger.info("MT5 connection closed. Goodbye!")


# =============================================================================
# SIGNAL HANDLERS
# =============================================================================
def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    sys.exit(0)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def main():
    """Main entry point for the trading bot."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("MT5 Trading Bot v1.0")
    logger.info("-" * 40)

    # Validate credentials before attempting connection
    if not config.validate_credentials():
        sys.exit(1)

    # Initialize MT5
    if not initialize_mt5():
        logger.error("Failed to initialize MT5. Exiting.")
        sys.exit(1)

    # Create and run bot
    bot = TradingBot()
    bot.run()


if __name__ == "__main__":
    main()
