#from telegram import Update
#from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json

import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)


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
        "🤖 *Debatify Bot Help*\n\n"
        "*Supported commands:*\n"
        "/debate `<your_text>` — Start a debate about a given topic.\n"
        "/help — Show this help message.\n\n"
    )
    await update.message.reply_markdown(help_text)

#-----------------------------------------------------------------------------
# worked withuot option of continue or not
# import asyncio

# # # Your debate function 
# # # Simulate AI generator that yields JSONs with text parts
# # # Simulated async AI text generator
# # async def func(text):
# #     for i in range(5):
# #         await asyncio.sleep(1)
# #         yield {"text": f"Generated line {i+1} for: {text}"}

# # # Handler for /debate (zigzag display)
# # async def debate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     if not context.args:
# #         await update.message.reply_text("Usage: /printtt <your_text>")
# #         return

# #     input_text = " ".join(context.args)

# #     # Initial reply
# #     sent_msg = await update.message.reply_text("Generating response...")

# #     all_lines = []

# #     # Zigzag indentation width
# #     indent_space = " " * 47  # Adjust for visual effect (Telegram uses proportional font)

# #     # Collect and show lines
# #     async for result in func(input_text):
# #         text_piece = result.get("text", "")
# #         line_number = len(all_lines)

# #         if line_number % 2 == 0:
# #             formatted = f"> {text_piece}"
# #         else:
# #             formatted = f"{indent_space}> {text_piece}"

# #         all_lines.append(formatted)
# #         try:
# #             await sent_msg.edit_text("\n".join(all_lines))
# #         except:
# #             pass  # Ignore edit rate errors

#-----------------------------------------------------------------------------------

# States
ASK_CONTINUE = 1

# Fake async generator
async def func(text):
    for i in range(16):
        await asyncio.sleep(0.5)
        if i > 0 and i % 4 == 0:
            yield {"text": "limit"}
        else:
            yield {"text": f"Generated line {i+1} for: {text}"}

# Per-user session store
user_data_store = {}

# Entry point
async def debate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /printtt <your_text>")
        return ConversationHandler.END

    chat_id = update.effective_chat.id
    input_text = " ".join(context.args)

    sent_msg = await update.message.reply_text("Generating...")

    user_data_store[chat_id] = {
        "input_text": input_text,
        "counter": 0,
        "all_lines": [],
        "sent_msg": sent_msg,
        "func_iter": func(input_text).__aiter__()
    }

    return await process_next(chat_id, context)

# Helper to get next chunk or ask user to continue
async def process_next(chat_id, context: ContextTypes.DEFAULT_TYPE):
    data = user_data_store[chat_id]
    indent_space = " " * 47

    try:
        while True:
            result = await anext(data["func_iter"])
            if result["text"] == "limit":
                # Ask to continue
                keyboard = [["yes"], ["no"]]
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="➡️ Do you want to continue ? (yes/no)",
                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                )
                return ASK_CONTINUE
            else:
                line_number = len(data["all_lines"])
                formatted = (
                    f"> {result['text']}"
                    if line_number % 2 == 0
                    else f"{indent_space}> {result['text']}"
                )
                data["all_lines"].append(formatted)
                await data["sent_msg"].edit_text("\n".join(data["all_lines"]))
    except StopAsyncIteration:
        return ConversationHandler.END

# Handle yes/no response
async def handle_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip().lower()
    data = user_data_store[chat_id]

    if text == "yes" and data["counter"] < 4:
        data["counter"] += 1
        await update.message.reply_text("✅ Continuing...", reply_markup=ReplyKeyboardRemove())
        return await process_next(chat_id, context)
    else:
        await update.message.reply_text("🛑 Stopping... Generating summary...", reply_markup=ReplyKeyboardRemove())

        summary_lines = []
        async for result in func("summary"):
            if result["text"] != "limit":
                summary_lines.append(result["text"])

        await update.message.reply_text("📝 Summary:\n" + "\n".join(summary_lines))
        return ConversationHandler.END

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Support async anext() in Python < 3.10
async def anext(ait):
    return await ait.__anext__()

#-----------------------------------------------------------------------------

# Main bot setup
def main():
    token = "7312111338:AAFuiXEItN102Q0NQJVSL87rkZVSi9HZytQ"

    app = ApplicationBuilder().token(token).build()

    # Register the /debate command handler
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    #app.add_handler(CommandHandler("debate", debate_handler)) 
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("debate", debate_handler)],
        states={
            ASK_CONTINUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_continue)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    # Start the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
