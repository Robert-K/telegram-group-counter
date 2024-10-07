# Telegram Group Counter Bot

This is a simple Telegram that provides a scoreboard for a group chat. Each user may enter and increment, decrement or set their score. The bot will keep track of the scores and display them in a message.

I supports multiple groups, each with their own scoreboard.

It's pretty simple and should be easily extendable to suit your needs.

## Usage

1. [Create a bot and take note of the token](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)
2. Install the required packages with `pip install -r requirements.txt`
3. Make sure to put the token in your enviroment variables or `.env` file as `BOT_TOKEN`

| Command | Description |
| --- | --- |
| `/start` | Starts the bot in your group chat and initializes the scoreboard |
| `/set` | Sets your score to a specific value. Usage: `/set 10` |
| `/inc` | Increments your score by 1 or a specified value. Usage: `/inc 5` |
| `/dec` | Decrements your score by 1 or a specified value. Usage: `/dec 5` |
| `/title` | Sets the title of the scoreboard. Usage: `/title New Title` (Currently broken) |

## Backstory

Reword this:
(we were eating a lot of pastel de nata and wanted to keep track of who ate the most)

This bot was created on the fly during a vacation in Porto with some friends. We were eating a lot of [Pastel de nata](https://en.wikipedia.org/wiki/Pastel_de_nata) and wanted to keep track of who ate the most.

Shoutout to Vlada for absolutely destroying us in the pastel de nata eating competition. 🫶

[![forthebadge](https://forthebadge.com/images/featured/featured-made-with-crayons.svg)](https://forthebadge.com)