import os
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes, CallbackQueryHandler, ConversationHandler
)

# --- Configuración ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("No se encontró la variable de entorno BOT_TOKEN")

# Activar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados para conversaciones
NAME, AGE, COLOR = range(3)

# --- Funciones auxiliares ---
async def send_typing_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Indica que el bot está escribiendo"""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

# --- Comandos básicos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Mensaje de bienvenida"""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📊 Ver menú", callback_data='menu')],
        [InlineKeyboardButton("ℹ️ Ayuda", callback_data='help')],
        [InlineKeyboardButton("📞 Contacto", callback_data='contact')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎉 ¡Bienvenido {user.first_name}!\n\n"
        f"Soy un bot con TODAS las funciones de Telegram API.\n"
        f"Envié /help para ver todo lo que puedo hacer.\n"
        f"Selecciona una opción:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Lista de comandos disponibles"""
    help_text = """
🤖 *Comandos disponibles:*

📝 *Básicos:*
/start - Iniciar el bot
/help - Mostrar esta ayuda
/about - Información del bot

🖼️ *Multimedia:*
/photo - Enviar una foto
/video - Enviar un video
/document - Enviar un documento
/audio - Enviar un audio

🎮 *Interactivos:*
/poll - Crear una encuesta
/dice - Tirar un dado
/quiz - Crear un quiz

📊 *Utilidades:*
/echo [texto] - Repetir tu mensaje
/uppercase [texto] - Convertir a mayúsculas
/lowercase [texto] - Convertir a minúsculas
/length [texto] - Contar caracteres

🎯 *Juegos:*
/quiz - Juego de preguntas
/survey - Encuesta interactiva

👥 *Usuarios:*
/id - Obtener tu ID de usuario
/chatid - Obtener ID del chat

⚙️ *Administración:*
/weather [ciudad] - Clima actual
/time - Hora actual
/date - Fecha actual

📱 *Conversaciones:*
/start_form - Iniciar formulario interactivo

*Mensajes:* 
Envía cualquier tipo de mensaje (texto, foto, sticker, video, etc.)
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /about - Información del bot"""
    await update.message.reply_text(
        "🤖 *Bot Super Completo*\n\n"
        "Versión: 2.0\n"
        "Funciones: Todas las API de Telegram\n"
        "Lenguaje: Python\n"
        "Framework: python-telegram-bot\n\n"
        "¡Puedo hacer casi todo! 🚀",
        parse_mode='Markdown'
    )

# --- Comandos multimedia ---
async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /photo - Enviar una foto de ejemplo"""
    await send_typing_action(update, context)
    photo_url = "https://picsum.photos/800/600"
    caption = "📸 *Foto de ejemplo*\n\nEsta es una imagen aleatoria de [Lorem Picsum](https://picsum.photos)"
    await update.message.reply_photo(
        photo=photo_url, 
        caption=caption, 
        parse_mode='Markdown'
    )

async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /video - Enviar un video de ejemplo"""
    await send_typing_action(update, context)
    video_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    await update.message.reply_video(
        video=video_url,
        caption="🎬 *Video de ejemplo*\nVideo de muestra",
        parse_mode='Markdown'
    )

async def send_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /document - Enviar un documento"""
    await send_typing_action(update, context)
    await update.message.reply_document(
        document="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        caption="📄 *Documento de ejemplo*\nPDF de prueba",
        parse_mode='Markdown'
    )

async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /audio - Enviar un audio"""
    await send_typing_action(update, context)
    audio_url = "https://file-examples.com/storage/feab0d9c102ac86c46cff1b/2017/11/file_example_MP3_700KB.mp3"
    await update.message.reply_audio(
        audio=audio_url,
        caption="🎵 *Audio de ejemplo*\nCanción de prueba",
        parse_mode='Markdown'
    )

# --- Comandos interactivos ---
async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /poll - Crear una encuesta"""
    await update.message.reply_poll(
        question="¿Qué lenguaje de programación prefieres?",
        options=["Python 🐍", "JavaScript 🌐", "Java ☕", "Go 🚀"],
        is_anonymous=False,
        allows_multiple_answers=False
    )

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /dice - Tirar un dado"""
    await update.message.reply_dice()

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /quiz - Juego de preguntas"""
    await update.message.reply_poll(
        question="¿Cuál es la capital de Francia?",
        options=["Londres", "Berlín", "París", "Madrid"],
        type="quiz",
        correct_option_id=2,
        explanation="¡París es la capital de Francia! 🗼",
        is_anonymous=False
    )

# --- Utilidades ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Eco de mensajes"""
    user_message = update.message.text
    await update.message.reply_text(f"🔊 *Eco:* {user_message}", parse_mode='Markdown')

async def uppercase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convertir texto a mayúsculas"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔠 *Mayúsculas:* {text.upper()}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /uppercase [texto]")

async def lowercase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convertir texto a minúsculas"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔡 *Minúsculas:* {text.lower()}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /lowercase [texto]")

async def length_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contar caracteres"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"📏 *Longitud:* {len(text)} caracteres", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /length [texto]")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtener ID del usuario"""
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 *Tu ID:* `{user.id}`\n"
        f"👤 *Username:* @{user.username}\n"
        f"📛 *Nombre:* {user.first_name} {user.last_name or ''}",
        parse_mode='Markdown'
    )

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtener ID del chat"""
    chat = update.effective_chat
    await update.message.reply_text(f"💬 *ID del chat:* `{chat.id}`", parse_mode='Markdown')

# --- API externas ---
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /weather - Obtener clima (simulado)"""
    if context.args:
        city = ' '.join(context.args)
        await send_typing_action(update, context)
        # Simulación de API de clima
        await update.message.reply_text(
            f"🌤️ *Clima en {city}*\n\n"
            f"Temperatura: 22°C\n"
            f"Humedad: 65%\n"
            f"Viento: 12 km/h\n\n"
            f"*Estado:* Parcialmente nublado ☁️",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Usa: /weather [ciudad]")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /time - Hora actual"""
    from datetime import datetime
    now = datetime.now()
    await update.message.reply_text(f"🕐 *Hora actual:* {now.strftime('%H:%M:%S')}", parse_mode='Markdown')

async def date_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /date - Fecha actual"""
    from datetime import datetime
    now = datetime.now()
    await update.message.reply_text(f"📅 *Fecha actual:* {now.strftime('%d/%m/%Y')}", parse_mode='Markdown')

# --- Conversaciones ---
async def start_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar formulario interactivo"""
    await update.message.reply_text("¡Vamos a conocerte! ¿Cuál es tu nombre?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtener nombre"""
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"Encantado, {context.user_data['name']}. ¿Cuántos años tienes?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtener edad"""
    context.user_data['age'] = update.message.text
    await update.message.reply_text("¿Cuál es tu color favorito?")
    return COLOR

async def get_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtener color y finalizar"""
    context.user_data['color'] = update.message.text
    
    summary = (
        f"✅ *Formulario completado!*\n\n"
        f"📛 *Nombre:* {context.user_data['name']}\n"
        f"🎂 *Edad:* {context.user_data['age']}\n"
        f"🎨 *Color favorito:* {context.user_data['color']}"
    )
    
    await update.message.reply_text(summary, parse_mode='Markdown')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancelar conversación"""
    await update.message.reply_text("❌ Formulario cancelado.")
    return ConversationHandler.END

# --- Manejo de callbacks (botones) ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar los botones inline"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'menu':
        await query.edit_message_text(
            "📊 *Menú Principal*\n\n"
            "Usa /help para ver todos los comandos disponibles.\n"
            "¿Qué te gustaría hacer?",
            parse_mode='Markdown'
        )
    elif query.data == 'help':
        await query.edit_message_text(
            "ℹ️ *Ayuda*\n\n"
            "Envíame cualquier mensaje o usa /help para ver todos los comandos.\n"
            "¡Estoy aquí para ayudarte! 🤖",
            parse_mode='Markdown'
        )
    elif query.data == 'contact':
        await query.edit_message_text(
            "📞 *Contacto*\n\n"
            "Desarrollador: @tu_usuario\n"
            "GitHub: github.com/tu_usuario\n"
            "¿Necesitas ayuda? Envía un mensaje!",
            parse_mode='Markdown'
        )

# --- Manejo de mensajes multimedia ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar fotos recibidas"""
    photo = update.message.photo[-1]  # Obtener la foto de mayor calidad
    await update.message.reply_text(f"📸 ¡Bonita foto! Tamaño: {photo.file_size} bytes")

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar stickers recibidos"""
    sticker = update.message.sticker
    await update.message.reply_text(f"🎨 ¡Qué sticker tan cool! Emoji: {sticker.emoji}")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar videos recibidos"""
    video = update.message.video
    await update.message.reply_text(f"🎬 ¡Buen video! Duración: {video.duration} segundos")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar mensajes de voz"""
    await update.message.reply_text("🎙️ ¡Mensaje de voz recibido!")

# --- Función principal ---
async def post_init(application: Application):
    """Configurar comandos después de iniciar"""
    await application.bot.set_my_commands([
        BotCommand("start", "Iniciar el bot"),
        BotCommand("help", "Mostrar ayuda"),
        BotCommand("about", "Información del bot"),
        BotCommand("photo", "Enviar una foto"),
        BotCommand("video", "Enviar un video"),
        BotCommand("document", "Enviar un documento"),
        BotCommand("audio", "Enviar un audio"),
        BotCommand("poll", "Crear una encuesta"),
        BotCommand("dice", "Tirar un dado"),
        BotCommand("quiz", "Juego de preguntas"),
        BotCommand("weather", "Consultar clima"),
        BotCommand("time", "Hora actual"),
        BotCommand("date", "Fecha actual"),
        BotCommand("id", "Tu ID de usuario"),
        BotCommand("start_form", "Formulario interactivo"),
    ])

def main():
    """Función principal"""
    # Crear aplicación
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # --- Comandos ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("photo", send_photo))
    application.add_handler(CommandHandler("video", send_video))
    application.add_handler(CommandHandler("document", send_document))
    application.add_handler(CommandHandler("audio", send_audio))
    application.add_handler(CommandHandler("poll", poll_command))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CommandHandler("uppercase", uppercase))
    application.add_handler(CommandHandler("lowercase", lowercase))
    application.add_handler(CommandHandler("length", length_command))
    application.add_handler(CommandHandler("id", get_id))
    application.add_handler(CommandHandler("chatid", get_chat_id))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("date", date_command))
    application.add_handler(CommandHandler("start_form", start_form))
    
    # --- Conversación ---
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start_form", start_form)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_color)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    
    # --- Callbacks (botones) ---
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # --- Manejo de mensajes multimedia ---
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # --- Manejo de texto (para respuestas) ---
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Iniciar bot
    logger.info("🚀 Bot iniciado con TODAS las funciones de Telegram API")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()