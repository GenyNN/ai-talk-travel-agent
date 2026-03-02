# Telegram Bot Integration for AI Travel Agent

This document explains how to set up and use the Telegram bot integration for the AI Travel Agent.

## Features

- 🤖 **Full Telegram Bot Integration**: Complete webhook-based Telegram bot
- 🌍 **Travel Planning**: Interactive travel planning through Telegram
- 📱 **User Sessions**: Maintains conversation state per user
- 🔄 **Webhook Support**: Production-ready webhook implementation
- 🛠️ **Easy Setup**: Simple configuration and deployment

## Prerequisites

1. **Telegram Bot Token**: You already have this: `8197325061:AAFM8AEd5-ull-Xltqz6mFofPrfpGDhSlZ0`
2. **Public Server**: Your server must be accessible from the internet for webhooks
3. **HTTPS**: Telegram requires HTTPS for webhooks (use ngrok for development)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your configuration:

```bash
cp env.example .env
```

Edit `.env` and ensure you have:

```env
TELEGRAM_BOT_TOKEN=8197325061:AAFM8AEd5-ull-Xltqz6mFofPrfpGDhSlZ0
PERPLEXITY_API_KEY=your_perplexity_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 3. Start the Server

```bash
python main.py
```

The server will start on `http://localhost:8001`

### 4. Set Up Webhook (Production)

For production, set your webhook URL:

```bash
curl -X POST "http://localhost:8001/telegram/set-webhook" \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://yourdomain.com/telegram/webhook"}'
```

### 5. Development with ngrok

For development, use ngrok to expose your local server:

```bash
# Install ngrok
npm install -g ngrok

# Expose your local server
ngrok http 8001

# Use the HTTPS URL for webhook
curl -X POST "http://localhost:8001/telegram/set-webhook" \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://your-ngrok-url.ngrok.io/telegram/webhook"}'
```

## API Endpoints

### Telegram Webhook
- **POST** `/telegram/webhook` - Receives updates from Telegram
- **POST** `/telegram/set-webhook` - Sets webhook URL
- **GET** `/telegram/bot-info` - Gets bot information

### Travel Agent
- **POST** `/travel-agent` - Run travel agent (existing)
- **POST** `/chat` - General AI chat (existing)

## Bot Commands

- `/start` or `/help` - Start a new conversation
- `/status` - Check current planning status

## Usage Examples

### Starting a Conversation

Send `/start` to the bot, then:

```
User: хочу спланировать поездку
Bot: Какую поездку вы планируете?
    1) Самостоятельная поездка
    2) Организованный туризм
    3) Деловая поездка
```

### Complete Flow

The bot will guide you through:

1. **Trip Type** - Choose type of travel
2. **Destination** - Where you want to go
3. **Group Size** - How many people
4. **Travel Dates** - When you want to travel
5. **Departure City** - Where you're leaving from
6. **Recommendations** - AI-generated travel advice
7. **Feedback** - Rate the recommendations
8. **Human Agent** - Connect with real travel agent

## Testing

### Test Bot Connection

```bash
python setup_telegram.py
```

### Manual Testing

1. Start the server: `python main.py`
2. Set webhook: Use the setup script or API
3. Send messages to your bot on Telegram
4. Check server logs for responses

### Test Webhook

```bash
curl -X POST "http://localhost:8001/telegram/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {"id": 123456789, "first_name": "Test"},
      "chat": {"id": 123456789, "type": "private"},
      "date": 1234567890,
      "text": "test"
    }
  }'
```

## Deployment

### Docker Deployment

```bash
# Build the image
docker build -t ai-travel-agent .

# Run with environment variables
docker run -p 8001:8001 \
  -e TELEGRAM_BOT_TOKEN=8197325061:AAFM8AEd5-ull-Xltqz6mFofPrfpGDhSlZ0 \
  -e PERPLEXITY_API_KEY=your_key \
  ai-travel-agent
```

### Production Deployment

1. Deploy to your server (AWS, DigitalOcean, etc.)
2. Set up HTTPS (Let's Encrypt recommended)
3. Configure webhook URL
4. Set up monitoring and logging

## Troubleshooting

### Common Issues

1. **Webhook not working**: Ensure HTTPS and public accessibility
2. **Bot not responding**: Check server logs and webhook status
3. **Session issues**: Bot maintains separate sessions per user

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Webhook Status

```bash
curl "https://api.telegram.org/bot8197325061:AAFM8AEd5-ull-Xltqz6mFofPrfpGDhSlZ0/getWebhookInfo"
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Webhook Security**: Consider implementing webhook signature verification
3. **Rate Limiting**: Implement rate limiting for production use
4. **User Data**: Be mindful of user privacy and data protection

## Monitoring

Monitor your bot with:

- Server logs
- Telegram Bot API logs
- Webhook delivery status
- User engagement metrics

## Support

For issues or questions:

1. Check the logs first
2. Test with the setup script
3. Verify webhook configuration
4. Check API key validity

## Next Steps

- Add more interactive features (buttons, inline keyboards)
- Implement user authentication
- Add analytics and monitoring
- Scale for multiple users
- Add more language support
