
# Bitcoin Sticker Pack Bot

A Telegram bot that automatically updates a sticker pack with live cryptocurrency data, including Bitcoin prices, Ethereum prices, Fear & Greed Index, Bitcoin halving countdown, and ETF information.

## Features

- **Bitcoin Price Stickers**: Live BTC price with 24h change indicators
- **Ethereum Price Stickers**: Live ETH price in USD and BTC
- **Fear & Greed Index**: Regular and "troll" versions 
- **Bitcoin Halving Countdown**: Progress bar and time estimates
- **ETF Data**: Bitcoin ETF prices and market data
- **Smart Scheduling**: Updates based on market hours and data relevance

## Quick Start

### Prerequisites
- Python 3.7+
- Telegram Bot Token
- Required environment variables (see Configuration)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd hcn-stickerpack

# Install dependencies
pip install -r requirements.txt

# Set environment variables (see Configuration section)
export TG_BOT_TOKEN="your_bot_token"
export TG_USER_ID="your_user_id"
export TG_PACK_NAME="your_pack_name"

# Run the bot
python main.py
```

## Configuration

Required environment variables:
- `TG_BOT_TOKEN`: Your Telegram bot token from BotFather
- `TG_USER_ID`: Your Telegram user ID
- `TG_PACK_NAME`: Name of your sticker pack

## Usage

### Basic Usage
```bash
# Update stickers according to schedule
python main.py

# Force update all stickers regardless of schedule
python main.py --force

# Generate test PNG files for development
python main.py --test

# Custom output directory for test files
python main.py --test --output-dir ./test_output/
```

### Development

The project uses a modular architecture for easy maintenance and testing:

```
src/
├── config/      # Configuration management
├── data/        # API data fetching and models
├── graphics/    # Sticker rendering
├── bot/         # Telegram bot operations  
├── utils/       # Utilities (timing, etc.)
└── app.py       # Main application orchestrator
```

## Scheduling

The bot intelligently schedules updates:
- **Bitcoin/Ethereum**: Always updated
- **ETF Data**: Only during US market hours (9:30 AM - 4:00 PM ET, weekdays)
- **Fear & Greed Index**: Once per day at 12:00 UTC
- **Halving Countdown**: Once per day at 12:00 UTC

## Credits

- Initial work done by [sash13](https://github.com/sash13)
- Bank icon is from [svg icons](https://www.onlinewebfonts.com/icon) licensed by CC BY 4.0
- Refactored for better maintainability and modularity

## License

This project is open source. See the license file for details.
