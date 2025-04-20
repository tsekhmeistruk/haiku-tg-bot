# 🥷 Samurai Haiku Bot

A minimalist Telegram bot that sends poetic haikus from the soul of a wandering samurai.

## Features
- Responds to `/хоку` command with a new AI-generated haiku
- Uses OpenAI GPT-4 for poetic style
- Works in private chats or groups

## How to Run

1. Set environment variables:
    - `TELEGRAM_TOKEN`
    - `OPENAI_API_KEY`

2. Build and run with Docker:
```bash
docker build -t samurai-bot .
docker run -e TELEGRAM_TOKEN=xxx -e OPENAI_API_KEY=yyy samurai-bot
