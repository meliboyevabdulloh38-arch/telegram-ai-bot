import os
import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from google import genai


# =========================
# API
# =========================

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

client = genai.Client(api_key=GEMINI_API_KEY)


# =========================
# XOTIRA
# =========================

xotira = {}
MAX_XOTIRA = 10


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.effective_chat:
        return

    await update.message.reply_text(
        "👋 Salom!\n\n"
        "Men AI suhbatdosh botman 🤖\n"
        "Menga yozing 😄"
    )


# =========================
# AI JAVOB
# =========================

async def javob_ber(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message or not update.message.text:
        return

    chat = update.effective_chat

    # =========================
    # GURUH TEKSHIRUVI
    # =========================

    if chat.type in ["group", "supergroup"]:

        try:

            bot_member = await context.bot.get_chat_member(
                chat.id,
                context.bot.id
            )

            # Bot admin bo'lmasa javob bermaydi
            if bot_member.status not in [
                "administrator",
                "creator"
            ]:
                return

        except Exception as e:

            print("ADMIN TEKSHIRISH XATOSI:", e)

            return

    # =========================
    # USER
    # =========================

    savol = update.message.text

    user_id = update.effective_user.id

    ism = (
        update.effective_user.first_name
        or "Do‘stim"
    )


    # =========================
    # XOTIRA
    # =========================

    if user_id not in xotira:
        xotira[user_id] = []

    xotira[user_id].append(
        f"{ism}: {savol}"
    )

    if len(xotira[user_id]) > MAX_XOTIRA:

        xotira[user_id] = (
            xotira[user_id][-MAX_XOTIRA:]
        )


    oldingi_suhbat = "\n".join(
        xotira[user_id]
    )


    # =========================
    # PROMPT
    # =========================

    prompt = f"""
Sen Telegramdagi samimiy va aqlli o‘zbekcha suhbatdosh botsan.

Qoidalar:

- Faqat o‘zbek tilida gaplash.
- Tabiiy gaplash.
- Juda rasmiy bo‘lma.
- Qisqa va qiziqarli javob ber.
- Hazil bo‘lsa hazil bilan javob ber.
- Jiddiy savol bo‘lsa jiddiy javob ber.
- Oldingi suhbatni hisobga ol.
- Bir xil javobni takrorlama.
- O‘zingni AI ekaningni har safar aytma.

Foydalanuvchi:
{ism}

Oldingi suhbat:
{oldingi_suhbat}

Hozirgi xabar:
{savol}

Tabiiy javob ber.
"""


    # =========================
    # GEMINI
    # =========================

    for urinish in range(3):

        try:

            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt
            )

            javob = response.text

            print("GEMINI JAVOB:", javob)

            if not javob:

                raise Exception(
                    "Gemini bo‘sh javob qaytardi"
                )


            # Xotiraga qo‘shish

            xotira[user_id].append(
                f"AI Bot: {javob}"
            )

            if len(xotira[user_id]) > MAX_XOTIRA:

                xotira[user_id] = (
                    xotira[user_id][-MAX_XOTIRA:]
                )


            # Telegramga yuborish

            await update.message.reply_text(
                javob
            )

            return


        except Exception as e:

            print(
                f"GEMINI XATOSI "
                f"({urinish + 1}/3): {repr(e)}"
            )

            if urinish < 2:

                await asyncio.sleep(2)


    # =========================
    # XATO
    # =========================

    await update.message.reply_text(
        "😅 AI hozir javob bera olmadi. "
        "Birozdan keyin yana yozing."
    )


# =========================
# PORT
# =========================

async def health_server():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    async def handle(
        reader,
        writer
    ):

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 13\r\n"
            "Connection: close\r\n"
            "\r\n"
            "Bot is alive!"
        )

        writer.write(
            response.encode()
        )

        await writer.drain()

        writer.close()

    server = await asyncio.start_server(
        handle,
        "0.0.0.0",
        port
    )

    print(
        f"🌐 PORT {port} ISHLAYAPTI"
    )

    return server


# =========================
# MAIN
# =========================

async def main():

    server = await health_server()

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .build()
    )


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            javob_ber
        )
    )


    await app.initialize()

    await app.start()

    await app.updater.start_polling()


    print(
        "🤖 BOT ISHLAYAPTI!"
    )


    try:

        while True:

            await asyncio.sleep(3600)

    except asyncio.CancelledError:

        pass

    finally:

        await app.updater.stop()

        await app.stop()

        await app.shutdown()

        server.close()

        await server.wait_closed()


asyncio.run(main())
