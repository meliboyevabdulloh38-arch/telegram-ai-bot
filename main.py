import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Web Server (Render faol turishi uchun)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Men AI botman. Savolingizni yozing!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # Ishlaydigan aniq model nomi: llama3-8b-8192
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama3-8b-8192",
        )
        reply = chat_completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        print(f"Xato: {e}")
        await update.message.reply_text("Xatolik yuz berdi. Qaytadan urinib ko'ring.")

def main():
    Thread(target=run_health_check_server, daemon=True).start()
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()
