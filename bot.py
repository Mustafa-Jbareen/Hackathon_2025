# from telegram import Update
# from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
# import json
# import asyncio
# import textwrap

import textwrap
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)

from debate_simulation import DebateSimulator
from my_secrets import OPENROUTER_API_KEY, OPENROUTER_API_BASE

# Handler for /start command
async def start_handler(update: Update, context):
    """
    What to do when the command /start is sent - just a sample text
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello I'm your 🤖 How can I assist you today?",
    )

# Handler for /help command
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 Debatify Bot Help\n\n"
        "Supported commands:\n"
        "/debate <your_text> — Start a debate about a given topic.\n"
        "/help — Show this help message.\n\n"
    )
    await update.message.reply_markdown(help_text)

#-----------------------------------------------------------------------------

# # Step 1: Simulate response to "func"
# def func(input_json):
#     return {
#         "text": "Article received. Preparing arguments..."
#     }

# # Step 2: Simulate response with 6 debate items
# def func1(input_json):
#     return {
#         "0": "Climate change is real and affects global temperatures.",
#         "1": "However, some argue the effects are exaggerated.",
#         "2": "Data shows increased storm frequency and intensity.",
#         "3": "Critics say such events also occurred naturally.",
#         "4": "Scientific consensus supports human impact.",
#         "5": "But policy responses remain politically divisive."
#     }

# # Helper: Format a 2-line block, left or right aligned
# def format_zigzag_block(text: str, align: str = "left") -> str:
#     wrap_width = 30 if align == "left" else 35
#     indent = 0 if align == "left" else 55

#     lines = textwrap.wrap(text, width=wrap_width)
#     if len(lines) == 1:
#         lines.append("")  # Ensure two lines always

#     return "\n".join(" " * indent + line for line in lines)

# # Handler for /debate command
# async def debate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not context.args:
#         await update.message.reply_text("Usage: /debate <your_text>")
#         return

#     user_input = " ".join(context.args)

#     # Step 1: Simulate call to func
#     result1 = func({"text": "Please provide the article text you want to discuss for the debate."})
    
#     # Step 2: Simulate call to func1
#     result2 = func1(result1)

#     # Step 3: Format into zigzag blocks
#     blocks = []
#     for i in range(6):
#         align = "left" if i % 2 == 0 else "right"
#         block = format_zigzag_block(result2[str(i)], align)
#         blocks.append(block)

#     # Step 4: Send initial message
#     sent_msg = await update.message.reply_text("💬 Starting debate...")

#     # Step 5: Reveal blocks one at a time
#     text_so_far = ""
#     for block in blocks:
#         text_so_far += block + "\n\n"
#         await asyncio.sleep(1.5)
#         await sent_msg.edit_text(text_so_far)


ASK_CONTINUE = range(1)
user_data_store = {}
debate_simulator = None  # Global variable to hold the DebateSimulator instance
counter = 0


# Simulated func
def func(input_json):
    if input_json.get("text") == "finish":
        return {
            "text": "Debate concluded. Thank you for participating."
        }
    else:
        return {
            "text": "Article received. Preparing arguments..."
        }

def func1(input_json):
    global debate_simulator  # Use the global variable
    global counter  # Use the global variable
    # Initialize only if debate_simulator is None
    if debate_simulator is None:
        debate_simulator = DebateSimulator(input_json)
    if input_json.get("text") == "continue":
        result = debate_simulator.simulate_debate()
        return result
    elif input_json.get("text") == "finish":
        result = debate_simulator.summarize_debate()
        counter = 0  # Reset counter for next debate
        return result
    else:
        result = debate_simulator.simulate_debate()
        return result

# Format one zigzag block
def format_zigzag_block(text: str, align: str = "left") -> str:
    wrap_width = 30 if align == "left" else 35
    indent = 0 if align == "left" else 55
    lines = textwrap.wrap(text, width=wrap_width)
    if len(lines) == 1:
        lines.append("")
    return "\n".join(" " * indent + line for line in lines)

# Show one zigzag block and append to single message
async def print_zigzag_append(lines_json, prev_text, sent_message):
    global counter  # Use the global variable
    for i in range(2):
        align = "left" if i % 2 == 0 else "right"
        block = format_zigzag_block(lines_json[str(i + counter)], align)
        prev_text += block + "\n\n"
        await asyncio.sleep(0.4)
        await sent_message.edit_text(prev_text)
    counter += 2  # Increment the counter for the next round
    return prev_text

# Build yes/no inline keyboard
def yes_no_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes", callback_data="yes"),
         InlineKeyboardButton("❌ No", callback_data="no")]
    ])

# /debate handler
async def start_debate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data_store[chat_id] = {"counter": 0}

    await update.message.reply_text("💬 Starting debate...")

    result1 = func({"text": "Please provide the article text you want to discuss for the debate."})
    result1 = {
        "claim": "Climate change is primarily driven by human activity.",
        "groups": {
            "Group A": {
                "name": "Climate Scientists",
                "sources": [
                    "https://www.ipcc.ch/report/ar6/",
                    "https://www.nature.com/articles/s41586-019-1711-1"
                ]
            },
            "Group B": {
                "name": "Climate Skeptics",
                "sources": [
                    "https://www.heritage.org/environment/report/the-dubious-science-climate-alarmism",
                    "https://wattsupwiththat.com/"
                ]
            }
        }
    }
    result2 = func1(result1)

    sent_msg = await update.message.reply_text("🧠 Generating...")
    updated_text = await print_zigzag_append(result2, "", sent_msg)

    context.user_data["message"] = sent_msg
    context.user_data["text"] = updated_text

    await update.message.reply_text("Do you want to continue?", reply_markup=yes_no_keyboard())
    return ASK_CONTINUE

# Handle button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return ConversationHandler.END  # safety fallback
    await query.answer()
    user_input = query.data
    chat_id = query.message.chat.id
    user_state = user_data_store.get(chat_id, {"counter": 0})
    counter = user_state["counter"]

    sent_msg = context.user_data["message"]

    if user_input == "yes" and counter < 4:
        user_state["counter"] += 1
        result2 = func1({"text": "continue"})
        updated_text = await print_zigzag_append(result2, context.user_data["text"], sent_msg)
        context.user_data["text"] = updated_text
        await query.message.reply_text("Continue again?", reply_markup=yes_no_keyboard())
        return ASK_CONTINUE
    else:
        result2 = func1({"text": "finish"})
        plain_text = ""
        # Since result2 has only one key ("Summary"), just extract and format that
        summary_text = result2.get("summary", "No summary found.")
        plain_text += summary_text + "\n\n"
        # Combine with previously saved content
        full_text = context.user_data["text"] + plain_text
        # Edit the original sent message with the full updated content
        await sent_msg.edit_text(full_text)
        # Remove the inline button message
        await query.message.delete()
        return ConversationHandler.END

# Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Debate canceled.")
    return ConversationHandler.END

#-----------------------------------------------------------------------------

# Main bot setup
def main():
    token = "7312111338:AAFuiXEItN102Q0NQJVSL87rkZVSi9HZytQ"

    app = ApplicationBuilder().token(token).build()


    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    #app.add_handler(CommandHandler("debate", debate_handler)) 
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("debate", start_debate)],
        states={ASK_CONTINUE: [CallbackQueryHandler(button_handler)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    app.add_handler(conv_handler)

    # Start the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()