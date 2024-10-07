import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import re

# TODO: Title is not stored properly, resets
# TODO: Add a command to reset the scores
# TODO: Allow multiple counters in the same chat
# TODO: Persist the scores over restarts

# Load the BOT_TOKEN from the .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Start command to initialize the counter message in the group
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Initialize an empty score for the chat if it doesn't exist in chat_data
    if 'user_scores' not in context.chat_data:
        context.chat_data['user_scores'] = {}

    # Reset anyway
    context.chat_data['user_scores'] = {}

    # Create a message with buttons
    keyboard = [
        [InlineKeyboardButton("➕", callback_data='increment'), InlineKeyboardButton("➖", callback_data='decrement')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send scoreboard message and store the message ID
    message = await update.message.reply_text("Scoreboard: \n(Interact to add yourself!)", reply_markup=reply_markup, do_quote=False)
    
    # Save the message ID in chat_data to reference later
    context.chat_data['scoreboard_message_id'] = message.message_id
    
    # Delete the command message
    await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)

# Helper function to format the score message
def format_score_message(user_scores, title="Scoreboard"):
    if len(user_scores) == 0:
        return f"{title}\nNo scores yet. Interact to start!"

    # Display each score with minimal decimal points
    scores = [f"{user['name']}: {user['score']:.10g}" for user in user_scores.values()]
    return f"{title}:\n" + "\n".join(scores)

# Helper function to update a user's score
def update_score(context, user_id, user_name, value, set_score=False):
    if 'user_scores' not in context.chat_data:
        context.chat_data['user_scores'] = {}

    user_scores = context.chat_data['user_scores']

    if user_id not in user_scores:
        user_scores[user_id] = {'name': user_name, 'score': 0.0}
    else:
        user_scores[user_id]['name'] = user_name

    if set_score:
        user_scores[user_id]['score'] = value
    else:
        user_scores[user_id]['score'] += value

    context.chat_data['user_scores'] = user_scores

# Function to edit the original scoreboard message
async def edit_scoreboard_message(update: Update, context: ContextTypes.DEFAULT_TYPE, title="Scoreboard"):
    chat_id = update.message.chat_id

    # Get the message ID of the scoreboard
    scoreboard_message_id = context.chat_data.get('scoreboard_message_id')
    
    if scoreboard_message_id:
        updated_message = format_score_message(context.chat_data['user_scores'], title)
        keyboard = [
            [InlineKeyboardButton("➕", callback_data='increment'), InlineKeyboardButton("➖", callback_data='decrement')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Edit the original scoreboard message
        await context.bot.edit_message_text(
            text=updated_message, 
            chat_id=chat_id, 
            message_id=scoreboard_message_id, 
            reply_markup=reply_markup, 
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("Scoreboard message not found.", do_quote=False)

# Handle button press (callback queries)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_name = update.effective_user.mention_html()

    if query.data == 'increment':
        update_score(context, user_id, user_name, 1.0)
    elif query.data == 'decrement':
        update_score(context, user_id, user_name, -1.0)

    # Edit the scoreboard message with updated scores
    await edit_scoreboard_message(query, context)

# Command to increment a user's score
async def increment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_inc_dec(update, context, increment=True)

# Command to decrement a user's score
async def decrement_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_inc_dec(update, context, increment=False)

# Helper function to handle increment and decrement commands
async def handle_inc_dec(update: Update, context: ContextTypes.DEFAULT_TYPE, increment=True):
    message = update.message.text
    chat_id = update.message.chat_id
    user_mention_pattern = r"@(\w+)"
    value_pattern = r"([-+]?\d*\.\d+|\d+)"  # Supports both floating-point and integer values

    mentioned_user = None
    increment_value = 1.0

    # Check for user mention in the message
    mention_match = re.search(user_mention_pattern, message)
    if mention_match:
        mentioned_user = mention_match.group(1)

    # Check for a value in the message
    value_match = re.search(value_pattern, message)
    if value_match:
        increment_value = float(value_match.group(1))

    # If it's a decrement command, make the value negative
    if not increment:
        increment_value = -increment_value

    # Get the user to modify (either the mentioned user or the command sender)
    if mentioned_user:
        # Find the user by their mention
        for user_id, user_data in context.chat_data.get('user_scores', {}).items():
            if mentioned_user in user_data['name']:
                user_id_to_update = user_id
                user_name = user_data['name']
                break
        else:
            await update.message.reply_text(f"User {mentioned_user} not found.", do_quote=False)
            return
    else:
        user_id_to_update = update.effective_user.id
        user_name = update.effective_user.mention_html()

    # Update the user's score
    update_score(context, user_id_to_update, user_name, increment_value)

    # Edit the scoreboard message with updated scores
    await edit_scoreboard_message(update, context)

    # Delete the command message
    await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)

# Command to set a user's score
async def set_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    user_mention_pattern = r"@(\w+)"
    value_pattern = r"([-+]?\d*\.\d+|\d+)"  # Supports both floating-point and integer values

    mentioned_user = None
    set_value = 0.0

    # Check for user mention in the message
    mention_match = re.search(user_mention_pattern, message)
    if mention_match:
        mentioned_user = mention_match.group(1)

    # Check for a value in the message
    value_match = re.search(value_pattern, message)
    if value_match:
        set_value = float(value_match.group(1))
    else:
        await update.message.reply_text("Please provide a value to set.", do_quote=False)
        return

    # Get the user to modify (either the mentioned user or the command sender)
    if mentioned_user:
        for user_id, user_data in context.chat_data.get('user_scores', {}).items():
            if mentioned_user in user_data['name']:
                user_id_to_update = user_id
                user_name = user_data['name']
                break
        else:
            await update.message.reply_text(f"User {mentioned_user} not found.", do_quote=False)
            return
    else:
        user_id_to_update = update.effective_user.id
        user_name = update.effective_user.mention_html()

    # Set the user's score
    update_score(context, user_id_to_update, user_name, set_value, set_score=True)

    # Edit the scoreboard message with updated scores
    await edit_scoreboard_message(update, context)

    # Delete the command message
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

# Command to set the scoreboard title
async def title_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title_pattern = r"^/title (.+)$"  # Matches title command with a title argument
    message = update.message.text

    title_match = re.match(title_pattern, message)
    if not title_match:
        await update.message.reply_text("Usage: /title <new title>", do_quote=False)
        return

    new_title = title_match.group(1)

    # Update the scoreboard message with the new title
    await edit_scoreboard_message(update, context, title=new_title)

    # Delete the command message
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

# Main function to set up the bot application
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handler for /start
    application.add_handler(CommandHandler('start', start))

    # Command handlers for /inc, /dec, /set, and /title
    application.add_handler(CommandHandler('inc', increment_command))
    application.add_handler(CommandHandler('dec', decrement_command))
    application.add_handler(CommandHandler('set', set_command))
    application.add_handler(CommandHandler('title', title_command))

    # Callback handler for button presses
    application.add_handler(CallbackQueryHandler(button_handler))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
