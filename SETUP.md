# Setup Instructions

This document contains setup instructions for the Telegram-Mesh Bridge project.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Telegram Bot Token (get from @BotFather)
- MeshTastic device

## Initial Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd tg-mesh-bridge
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file**
   ```bash
   # Required: Your Telegram Bot Token
   BOT_TOKEN=your_telegram_bot_token_here
   
   # MQTT Configuration
   MQTT_HOST=your_mqtt_host_ip
   MQTT_USER=your_mqtt_username
   MQTT_PASS=your_mqtt_password
   
   # PostgreSQL Configuration (optional, defaults are provided)
   POSTGRES_DB=tgmesh
   POSTGRES_USER=tgmesh
   POSTGRES_PASSWORD=your_secure_password
   ```

4. **Update MQTT credentials**
   
   Edit `infra/mosquitto/passwords` and replace the placeholder with your actual hashed password:
   ```
   your_mqtt_username:$7$101$your_actual_hashed_password
   ```
   
   To generate a hashed password:
   ```bash
   docker run --rm eclipse-mosquitto:2 mosquitto_passwd -U passwords
   ```

5. **Update MQTT ACL**
   
   Edit `infra/mosquitto/acl` and replace the username:
   ```
   user your_actual_mqtt_username
   topic readwrite msh/#
   ```

6. **Start the application**
   ```bash
   make up
   ```

7. **Apply database migrations**
   ```bash
   make db
   ```

## Configuration Details

### MQTT Broker
- **Default port**: 1883
- **Authentication**: Username/password
- **Topics**: `msh/US/2/json/#`
- **Access**: Read/write for all mesh topics

### PostgreSQL Database
- **Database**: tgmesh
- **User**: tgmesh
- **Port**: 5432 (internal)
- **Data persistence**: Docker volumes

### Telegram Bot
- **Commands**: `/start`, menu-based navigation
- **Features**: TG codes, device management, message bridging

## Testing

1. **Test MQTT connection**
   ```bash
   make test
   ```

2. **Test bot functionality**
   ```bash
   # Find your bot in Telegram and send /start
   ```

3. **Test mesh integration**
   ```bash
   # Send message from MeshTastic: @tg:YOURCODE Hello!
   ```

## Troubleshooting

### Common Issues

1. **MQTT connection failed**
   - Check MQTT credentials in `.env`
   - Verify MQTT broker is running: `docker logs tg-mesh-mosquitto`

2. **Database connection failed**
   - Check PostgreSQL credentials
   - Verify database is running: `docker logs tg-mesh-postgres`

3. **Bot not responding**
   - Check BOT_TOKEN in `.env`
   - Verify app is running: `make logs`

### Logs

View application logs:
```bash
make logs
```

View specific service logs:
```bash
docker logs tg-mesh-app
docker logs tg-mesh-mosquitto
docker logs tg-mesh-postgres
```

## Security Notes

- Change all default passwords
- Use strong passwords for MQTT and PostgreSQL
- Keep your bot token secure
- Consider using environment variables for production
- Review MQTT ACL permissions

## Production Deployment

For production deployment:

1. Use environment variables instead of `.env` file
2. Set up proper SSL/TLS for MQTT
3. Use external PostgreSQL instance
4. Configure proper logging and monitoring
5. Set up backup procedures for database
6. Use reverse proxy for external access
