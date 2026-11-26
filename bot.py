import asyncio
import logging
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes

# Token-uን ከ Render Environment Variable ይወስዳል
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DELETE_AFTER_SECONDS = 60

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# --- ለ Render Free Web Service የሚያገለግል ትንሽ ሰርቨር ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()
# ----------------------------------------------------

async def delete_after_delay(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = DELETE_AFTER_SECONDS):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.warning(f"መልእክቱን ማጥፋት አልተቻለም: {e}")

async def greet_approved_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user = result.new_chat_member.user

    if user.is_bot:
        return

    was_outside = old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED)
    is_now_member = new_status == ChatMemberStatus.MEMBER

    if was_outside and is_now_member:
        mention = user.mention_html()

        welcome_text = (
            f"ሰላም {mention}! 🙏❤️\n\n"
            "ይህ <b>እነሆኝ የጸሎት ሕብረት</b> ነው፤ ስለተቀላቀሉን እጅግ በጣም ደስተኞች ነን!\n\n"
            "ይህ ሕብረት (<b>ኢሳ 6/8</b>) መሪ ቃል ያደረገ ልዩ የጸሎት ሕብረት ነው። "
            "በዚህ ሕብረት ላይ የምናደርጋቸው ነገሮች እንዳለ ወጣቱን ያማከለ እና ህልውናውን ተኮር ያደረገ፣ "
            "ልክ እንደ ባሪያው <i>«እነሆኝ»</i> የሚል ትውልድን ማፍራት ነው። ስለሆነም አብራችሁን በጸሎት ለመትጋት "
            "ከጎናችን ስለሆናችሁ እና የዚህ ሕብረት አካል ስለሆናችሁ እጅግ በጣም ደስተኞች 🔥❤️ ነን!\n\n"
            "የምንገናኝባቸው እና አንድ ላይ በጌታ ፊት የምናሳልፍባቸው ጊዜ 🔥🔥 "
            "<b>ወር በገባ የመጀመሪያውን ቅዳሜ</b> ይሆናል! 🔥🔥\n"
            "ስለሆነም በእነዚህ በወር አንዴ እየተገናኘን በጌታ ፊት እናሳልፍ።\n\n"
            "📍 <b>ቦታ፦</b> በለኩ ኩሌ ቃለ ሕይወት ቤተ ክርስቲያን\n"
            "📞 <b>ለበለጠ መረጃ፦</b> 0944443319 ይደውሉ\n\n"
            "እንዲሁም ደግሞ የራሳችሁን ትክክለኛ መረጃ ከዚህ በታች ባለው ሊንክ ይላኩልን፦\n"
            "https://majestic-otter-eb8ae7.netlify.app\n\n"
            "ተባረኩልን! ጥያቄ ካሎት inbox: @yabuti10\n\n"
            "<i>⏳ ይህ መልእክት ከ 1 ደቂቃ በኋላ በራሱ ይጠፋል።</i>"
        )

        sent_msg = await context.bot.send_message(
            chat_id=result.chat.id,
            text=welcome_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        context.application.create_task(
            delete_after_delay(context, chat_id=sent_msg.chat_id, message_id=sent_msg.message_id)
        )

def main():
    # Render እንዳይዘጋው ሰርቨሩን ከበስተጀርባ እናስነሳለን
    Thread(target=run_dummy_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatMemberHandler(greet_approved_member, ChatMemberHandler.CHAT_MEMBER))

    print("ቦቱ በ Render ላይ መስራት ጀምሯል...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()