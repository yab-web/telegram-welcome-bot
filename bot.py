import asyncio
import logging
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, User
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, ChatMemberHandler, MessageHandler, filters, ContextTypes
from telegram.error import Forbidden

BOT_TOKEN = os.environ.get("BOT_TOKEN")

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

async def send_private_welcome(user: User, context: ContextTypes.DEFAULT_TYPE):
    if user.is_bot:
        return

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
        "ተባረኩልን! ጥያቄ ካሎት inbox: @yabuti10"
    )

    try:
        # ለገባው ሰው በግል (DM / PM) ብቻ ይልካል፤ በግሩፑ ውስጥ አይጽፍም
        await context.bot.send_message(
            chat_id=user.id,
            text=welcome_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Forbidden:
        logging.info(f"ተጠቃሚው ({user.id}) ገና ቦቱን ስላልከፈተ በግል መላክ አልተቻለም።")
    except Exception as e:
        logging.warning(f"መልእክት ሲላክ ስህተት ተፈጥሯል: {e}")

async def greet_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user = result.new_chat_member.user

    was_outside = old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED)
    is_now_member = new_status == ChatMemberStatus.MEMBER

    if was_outside and is_now_member:
        await send_private_welcome(user=user, context=context)

async def greet_new_chat_members_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.new_chat_members:
        return

    for member in msg.new_chat_members:
        await send_private_welcome(user=member, context=context)

def main():
    Thread(target=run_dummy_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatMemberHandler(greet_chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_chat_members_message))

    print("ቦቱ በ Render ላይ መስራት ጀምሯል...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
