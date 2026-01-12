# MT5 Trading Bot

An automated trading strategy for MetaTrader 5 with trend filtering, RSI-based entries, ATR risk management, and comprehensive safety features.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![MetaTrader5](https://img.shields.io/badge/MetaTrader-5-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Trend Filter**: 200 EMA for directional bias
- **Entry Signals**: RSI(14) crossover strategy
- **Risk Management**: ATR-based Stop Loss and Take Profit
- **Trailing Stops**: Dynamic ATR-based trailing with breakeven trigger
- **Kill Switch**: Automatic shutdown at 5% equity drawdown
- **Secure Config**: Environment variable-based credential management

## Strategy Logic

| Signal | Trend Filter | Entry Trigger |
|--------|--------------|---------------|
| **LONG** | Price > EMA(200) | RSI crosses above 30 |
| **SHORT** | Price < EMA(200) | RSI crosses below 70 |

### Risk Parameters
- **Stop Loss**: 1.5 × ATR(14) from entry
- **Take Profit**: 2.0 × ATR(14) from entry
- **Breakeven**: Triggered at 1:1 risk-reward ratio
- **Trailing**: ATR-based, moves only in profit direction

## Project Structure

```
trading-bot/
├── config.py              # Configuration and credentials
├── main.py                # Entry point and event loop
├── requirements.txt       # Python dependencies
├── .env                   # Credentials (not in git)
├── .env.template          # Credential template
├── .gitignore             # Git exclusions
└── strategy/
    ├── __init__.py        # Package exports
    ├── indicators.py      # EMA, RSI, ATR calculations
    ├── signals.py         # Entry signal logic
    ├── risk_manager.py    # SL/TP and trailing stops
    ├── executor.py        # MT5 order execution
    └── kill_switch.py     # Equity protection
```

## Installation

### Prerequisites
- Python 3.8 or higher
- MetaTrader 5 terminal installed
- MT5 account with API access enabled

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trading-bot
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials**
   ```bash
   copy .env.template .env  # Windows
   # or
   cp .env.template .env    # Linux/Mac
   ```

5. **Edit `.env` with your MT5 credentials**
   ```env
   MT5_LOGIN=your_account_number
   MT5_PASSWORD=your_password
   MT5_SERVER=your_broker_server
   ```

## Usage

### Start the bot
```bash
python main.py
```

### Configuration Options

Edit `config.py` to customize:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SYMBOL` | EURUSD | Trading instrument |
| `TIMEFRAME` | H1 | Chart timeframe |
| `LOT_SIZE` | 0.01 | Position size |
| `EMA_PERIOD` | 200 | Trend filter period |
| `RSI_PERIOD` | 14 | RSI indicator period |
| `ATR_SL_MULTIPLIER` | 1.5 | Stop loss distance |
| `ATR_TP_MULTIPLIER` | 2.0 | Take profit distance |
| `EQUITY_DRAWDOWN_LIMIT` | 0.05 | Kill switch threshold (5%) |

## Safety Features

### Kill Switch
The bot automatically shuts down and closes all positions if account equity drops by 5% from session start.

### Credential Validation
Missing or empty credentials trigger an immediate, informative error before any connection attempt.

### Graceful Shutdown
- Press `Ctrl+C` to stop the bot safely
- All connections are properly closed
- Final account state is logged

## Logs

Trading activity is logged to:
- **Console**: Real-time output
- **File**: `trading_bot.log`

Log levels can be adjusted in `config.py` via `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR).

## ⚠️ Disclaimer

**This software is for educational purposes only.**

- Always test on a demo account first
- Past performance does not guarantee future results
- Trading forex/CFDs carries significant risk of loss
- Never trade with money you cannot afford to lose

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
