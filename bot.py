import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuración básica ---
# ⚠️ SOLO PARA PRUEBAS - No subas esto a GitHub ⚠️
TOKEN = "8677535685:AAEazDZUBWF6LcNMCYbMLk8rn4T3Q7coRKA"

# Comentar o eliminar esta verificación
# if not TOKEN:
#     raise ValueError("No se encontró la variable de entorno BOT_TOKEN")

# Activar logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Resto del código igual...
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hola {user.first_name}! 👋\n"
        "Soy un bot de prueba.\n"
        "Envíame cualquier mensaje y te lo devolveré."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"Me dijiste: '{user_message}'")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comandos disponibles:\n/start - Inicia el bot\n/help - Muestra esta ayuda")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    logger.info("El bot está iniciando...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()