# Discord Member Counter Bot

A Discord bot that creates and updates a voice channel displaying the current member count of your server.

## Features

- Creates a voice channel showing member count
- Auto-updates when members join/leave
- Custom channel name format
- Welcome image generator
- Admin-only setup command

## Setup

1. Clone this repository
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `config2.json` file with your bot token:
   ```json
   {
       "DISCORD_TOKEN": "your-bot-token-here",
       "CHANNEL_NAME": "Members: {count}"
   }
   ```
4. Run the bot:
   ```bash
   python member_counter.py
   ```

## Commands

- `/setup` - Creates the member counter channel (Admin only)

## Deployment

This bot is ready to be deployed on Railway.app:

1. Fork this repository
2. Connect your GitHub to Railway
3. Create a new project from the repository
4. Add your Discord token as an environment variable:
   - Variable name: `DISCORD_TOKEN`
   - Value: Your bot token
5. Deploy!
