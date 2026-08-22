import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

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
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Men Gemini AI botman. Savolingizni yozing!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # Barcha mavjud modellarni olish
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Aniq bepul va ruxsat berilgan modelni tanlash
        target_model = None
        for m in all_models:
            if "gemini-1.5-flash" in m and "2.5" not in m:
                target_model = m
                break
        
        # Agar topilmasa, ro'yxatdagi istalgan 1.5 versiyani olish
        if not target_model:
            for m in all_models:
                if "1.5" in m:
                    target_model = m
                    break
        
        # Yakuniy model
        final_model_name = target_model if target_model else "models/gemini-1.5-flash"
        
        model = genai.GenerativeModel(final_model_name)
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Xato: {e}")
        await update.message.reply_text(f"API Xatoligi: {str(e)[:100]}")

def main():
    Thread(target=run_health_check_server, daemon=True).start()
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()
