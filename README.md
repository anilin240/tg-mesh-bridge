# Telegram-Mesh Bridge

A bridge between MeshTastic network and Telegram bot via MQTT protocol.

## Description

This project is a Telegram bot that serves as a bridge between MeshTastic devices and Telegram users. The bot receives messages from the Mesh network via MQTT and forwards them to Telegram, and also allows users to send messages back to the Mesh network.

## Architecture

- **Telegram Bot** - interface for users
- **MQTT Broker** (Mosquitto) - receiving messages from MeshTastic
- **PostgreSQL** - storing user data and messages
- **Python Application** - message processing and bot logic

## Features

- **TG Code**: Unique codes for user identification
- **My Nodes**: Device management (up to 3 per user)
- **Nearby**: View active nodes in the network
- **Mesh→TG**: Automatic message delivery from Mesh to Telegram
- **TG→Mesh**: Send messages from Telegram to Mesh network
- **Device Renaming**: Custom labels for devices

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Telegram Bot Token
- MeshTastic device

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tg-mesh-bridge
```

2. Create `.env` file with settings:
```bash
BOT_TOKEN=your_telegram_bot_token
MQTT_HOST=your_mqtt_host_ip
MQTT_USER=your_mqtt_username
MQTT_PASS=your_mqtt_password
```

3. Start the application:
```bash
make up
```

4. Apply database migrations:
```bash
make db
```

### Usage

1. Find the bot in Telegram by token
2. Send `/start` to begin
3. Use the menu to navigate through functions

## How to Use the Menu

### Main Menu
- **TG Code**: Manage your unique code
- **My Nodes**: Device management (up to 3 per user)
- **Nearby**: View active nodes in the network
- **Help**: Usage instructions

### TG Code
- **Show Code**: Displays your current code
- **Change Code**: Generates a new unique code
- **Set Code**: Allows you to set your own code (4-8 characters, letters and numbers)

### My Nodes
- **Add**: Link a new device to your account
- **List**: Show all your devices with labels
- **Edit**: Manage a specific device
  - **Write**: Send a message to the device
  - **Rename**: Set a custom label
  - **Delete**: Unlink device from account

### Nearby
- **Refresh**: Update the list of active nodes in the network
- Displays nodes with last activity time

## MeshTastic Configuration

To connect MeshTastic to MQTT broker, use the following settings:

- **Server**: your_mqtt_host_ip
- **Port**: 1883
- **Username**: your_mqtt_username
- **Password**: your_mqtt_password
- **Topic**: msh/US/2/json/#

## TG Code Workflow

```
MeshTastic → MQTT → @tg:CODE message → Telegram DM
```

1. **Send from Mesh**: `@tg:ABCD1234 Hello!`
2. **Processing**: Bot extracts code `ABCD1234` and message `Hello!`
3. **Auto-linking**: If device is not linked, it's automatically linked to the user
4. **Delivery**: Message is delivered to Telegram user with code `ABCD1234`

### Limits
- **Devices per user**: maximum 3
- **When limit exceeded**: message is delivered but device is not linked
- **Code**: 4-8 characters, letters and numbers only

## Project Structure

```
tg-mesh-bridge/
├── app/                    # Main application
│   ├── src/
│   │   ├── bot/           # Telegram bot
│   │   ├── bridge/        # MQTT bridge
│   │   └── common/        # Common modules
│   ├── alembic/           # Database migrations
│   └── tests/             # Tests
├── infra/                 # Docker infrastructure
│   ├── docker-compose.yml
│   └── mosquitto/         # MQTT broker
├── docs/                  # Documentation
└── scripts/               # Scripts
```

## Make Commands

- `make up` - start all services
- `make down` - stop all services
- `make logs` - view application logs
- `make db` - apply database migrations
- `make test` - run tests

## Logging

The bot logs key events:

### User Actions
- Menu button clicks
- TG code changes
- Adding/removing devices
- Device renaming

### System Events
- MQTT connections and errors
- Telegram DM sending errors
- Device auto-linking
- Limit exceedances

### Viewing Logs
```bash
# Application logs
make logs

# MQTT broker logs
docker logs tg-mesh-mosquitto

# Database logs
docker logs tg-mesh-postgres
```

## Development

### Adding New Features

1. Create a new branch: `git checkout -b feature/new-feature`
2. Make changes
3. Add tests
4. Create Pull Request

### Testing

```bash
make test
```

## License

MIT License

## Support

For questions and suggestions, create Issues in the repository.
