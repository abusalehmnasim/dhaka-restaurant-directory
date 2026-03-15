import pandas as pd
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ── Config ─────────────────────────────────────────────────────────────────────
BOT_TOKEN = "8610297684:AAGnh-jeiw9YjKfz5P1vPSdK48F4vme56x8"   
CSV_FILE  = "dhaka_restaurants.csv"

# ── Load data ──────────────────────────────────────────────────────────────────
print("Loading restaurant data...")
df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
text_cols = df.select_dtypes(include="str").columns
df[text_cols] = df[text_cols].fillna("N/A")
print(f"  {len(df)} places loaded.\n")

logging.basicConfig(level=logging.WARNING)

# ── Helper ─────────────────────────────────────────────────────────────────────
def format_result(row, index):
    """Format a single restaurant result for Telegram."""
    name    = row.get("Name", "Unknown")
    rtype   = row.get("Type", "N/A")
    cuisine = row.get("Cuisine", "N/A")
    area    = row.get("Area", "N/A")
    address = row.get("Address", "N/A")
    phone   = row.get("Phone", "N/A")
    hours   = row.get("Opening Hours", "N/A")
    gmaps   = row.get("Google Maps", "N/A")

    text = (
        f"*{index}. {name}*\n"
        f"🍽️ Type: {rtype}\n"
        f"🌍 Cuisine: {cuisine}\n"
        f"📍 Area: {area}\n"
        f"🏠 Address: {address}\n"
        f"📞 Phone: {phone}\n"
        f"🕐 Hours: {hours}\n"
    )

    if gmaps != "N/A":
        text += f"🗺️ [View on Google Maps]({gmaps})\n"

    return text


def search_data(query, field):
    """Search the dataframe by a given field."""
    return df[df[field].str.contains(query, case=False, na=False)]


# ── Command handlers ───────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    keyboard = [
        [InlineKeyboardButton("🔍 Search by Area",    callback_data="menu_area")],
        [InlineKeyboardButton("🍜 Search by Cuisine", callback_data="menu_cuisine")],
        [InlineKeyboardButton("🏪 Search by Name",    callback_data="menu_name")],
        [InlineKeyboardButton("📊 Show Stats",        callback_data="menu_stats")],
        [InlineKeyboardButton("📋 List All Areas",    callback_data="menu_areas_list")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🍽️ *Dhaka Restaurant Bot*\n\n"
        "I have data on *2,021 food places* across Dhaka.\n"
        "What would you like to do?",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "*Available Commands:*\n\n"
        "/start — Main menu\n"
        "/area <name> — Search by area (e.g. /area Gulshan)\n"
        "/cuisine <type> — Search by cuisine (e.g. /cuisine Chinese)\n"
        "/name <keyword> — Search by name (e.g. /name Pizza)\n"
        "/stats — Show statistics\n"
        "/areas — List all areas\n"
        "/help — Show this message",
        parse_mode="Markdown"
    )


async def area_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /area command."""
    if not context.args:
        await update.message.reply_text("Usage: /area Gulshan\nExample: /area Dhanmondi")
        return
    query = " ".join(context.args)
    results = search_data(query, "Area")
    await send_results(update, results, query)


async def cuisine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cuisine command."""
    if not context.args:
        await update.message.reply_text("Usage: /cuisine Chinese\nExample: /cuisine Bengali")
        return
    query = " ".join(context.args)
    results = search_data(query, "Cuisine")
    await send_results(update, results, query)


async def name_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /name command."""
    if not context.args:
        await update.message.reply_text("Usage: /name KFC\nExample: /name Pizza Hut")
        return
    query = " ".join(context.args)
    results = search_data(query, "Name")
    await send_results(update, results, query)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command."""
    total       = len(df)
    restaurants = len(df[df["Type"] == "Restaurant"])
    cafes       = len(df[df["Type"] == "Cafe"])
    fastfood    = len(df[df["Type"] == "Fast Food"])
    top_area    = df["Area"].value_counts().index[0]
    top_cuisine = df[df["Cuisine"] != "N/A"]["Cuisine"].value_counts().index[0]

    await update.message.reply_text(
        f"📊 *Dhaka Restaurant Stats*\n\n"
        f"🏙️ Total places: *{total}*\n"
        f"🍽️ Restaurants: *{restaurants}*\n"
        f"☕ Cafes: *{cafes}*\n"
        f"🍔 Fast Food: *{fastfood}*\n\n"
        f"📍 Busiest area: *{top_area}*\n"
        f"🌍 Top cuisine: *{top_cuisine}*",
        parse_mode="Markdown"
    )


async def areas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /areas command — list all areas."""
    area_counts = df["Area"].value_counts()
    text = "📋 *All Areas in Dhaka:*\n\n"
    for area, count in area_counts.items():
        text += f"• {area}: {count} places\n"
    await update.message.reply_text(text, parse_mode="Markdown")


# ── Inline button handler ──────────────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_area":
        await query.message.reply_text(
            "Send me an area name:\n"
            "Example: `/area Gulshan` or `/area Mirpur`",
            parse_mode="Markdown"
        )
    elif data == "menu_cuisine":
        await query.message.reply_text(
            "Send me a cuisine type:\n"
            "Example: `/cuisine Chinese` or `/cuisine Bengali`",
            parse_mode="Markdown"
        )
    elif data == "menu_name":
        await query.message.reply_text(
            "Send me a restaurant name:\n"
            "Example: `/name KFC` or `/name Pizza`",
            parse_mode="Markdown"
        )
    elif data == "menu_stats":
        await stats_command(query, context)
    elif data == "menu_areas_list":
        await areas_command(query, context)


# ── Send results helper ────────────────────────────────────────────────────────
async def send_results(update, results, query_label):
    """Send up to 5 results, with a count header."""
    if results.empty:
        await update.message.reply_text(
            f"❌ No results found for *'{query_label}'*\n"
            f"Try a different keyword.",
            parse_mode="Markdown"
        )
        return

    total = len(results)
    header = f"✅ Found *{total} place(s)* for '{query_label}'"
    if total > 5:
        header += f" — showing first 5:"
    await update.message.reply_text(header, parse_mode="Markdown")

    for i, (_, row) in enumerate(results.head(5).iterrows(), 1):
        text = format_result(row, i)
        await update.message.reply_text(text, parse_mode="Markdown",
                                         disable_web_page_preview=True)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("Starting Dhaka Restaurant Bot...")
    print("Press Ctrl+C to stop.\n")

    app = (
    Application.builder()
    .token(BOT_TOKEN)
    .connect_timeout(30)
    .read_timeout(30)
    .write_timeout(30)
    .pool_timeout(30)
    .build()
)

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("help",    help_command))
    app.add_handler(CommandHandler("area",    area_command))
    app.add_handler(CommandHandler("cuisine", cuisine_command))
    app.add_handler(CommandHandler("name",    name_command))
    app.add_handler(CommandHandler("stats",   stats_command))
    app.add_handler(CommandHandler("areas",   areas_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running!")
    app.run_polling()


if __name__ == "__main__":
    main()