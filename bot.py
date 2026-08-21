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


GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

client = genai.Client(api_key=GEMINI_API_KEY)

xotira = {}
MAX_XOTIRA = 10


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👋 Salom!\nMen AI suhbatdosh botman 🤖\nMenga yozing 😄"
    )


async def javob_ber(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    savol = update.message.text
    user_id = update.effective_user.id
    ism = update.effective_user.first_name or "Do‘stim"

    if user_id not in xotira:
        xotira[user_id] = []

    xotira[user_id].append(f"{ism}: {savol}")

    if len(xotira[user_id]) > MAX_XOTIRA:
        xotira[user_id] = xotira[user_id][-MAX_XOTIRA:]

    oldingi_suhbat = "\n".join(xotira[user_id])

    prompt = f"""
Sen Telegram guruhidagi samimiy, kulgili va aqlli o‘zbekcha suhbatdosh botsan.

Qoidalar:
- Faqat o‘zbek tilida gaplash.
- Tabiiy va oddiy gaplash.
- Juda rasmiy gapirma.
- Javobni qisqa va qiziqarli qil.
- Odam hazillashsa, hazil bilan javob ber.
- Odam jiddiy gapirsa, jiddiy javob ber.
- Oldingi suhbatni hisobga ol.
- Bir xil javoblarni takrorlama.

Foydalanuvchi: {ism}

Oldingi suhbat:
{oldingi_suhbat}

Hozirgi xabar:
{savol}

Tabiiy javob ber.
"""

    for urinish in range(3):

        try:

            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-3.6-flash",
                contents=prompt
            )

            javob = response.text

            if javob:

                xotira[user_id].append(
                    f"AI Bot: {javob}"
                )

                if len(xotira[user_id]) > MAX_XOTIRA:
                    xotira[user_id] = xotira[user_id][-MAX_XOTIRA:]

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=javob
                )

            return

        except Exception as e:

            print(f"AI xatosi ({urinish + 1}/3):", e)

            if urinish < 2:
                await asyncio.sleep(3)

    try:

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="😅 Hozir AI biroz band. Yana yozib ko‘ring."
        )

    except Exception as e:

        print("Telegram xatosi:", e)


async def main():

    app = ApplicationBuilder().token(
        TELEGRAM_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            javob_ber
        )
    )

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print("🤖 BOT ISHLAYAPTI!")

    try:

        while True:
            await asyncio.sleep(3600)

    except asyncio.CancelledError:
        pass

    finally:

        await app.updater.stop()
        await app.stop()
        await app.shutdown()


asyncio.run(main())
