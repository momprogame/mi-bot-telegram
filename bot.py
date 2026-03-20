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

# --- Lista completa de comandos organizada ---
COMMANDS = [
    # Básicos
    BotCommand("start", "🚀 Iniciar el bot"),
    BotCommand("help", "❓ Mostrar ayuda"),
    BotCommand("about", "ℹ️ Información del bot"),
    BotCommand("menu", "📋 Ver menú interactivo"),
    
    # Multimedia
    BotCommand("photo", "🖼️ Enviar una foto"),
    BotCommand("video", "🎬 Enviar un video"),
    BotCommand("document", "📄 Enviar un documento"),
    BotCommand("audio", "🎵 Enviar un audio"),
    
    # Interactivos
    BotCommand("poll", "📊 Crear una encuesta"),
    BotCommand("dice", "🎲 Tirar un dado"),
    BotCommand("quiz", "🧠 Juego de preguntas"),
    
    # Utilidades de texto
    BotCommand("echo", "🔊 Repetir tu mensaje"),
    BotCommand("uppercase", "🔠 Convertir a mayúsculas"),
    BotCommand("lowercase", "🔡 Convertir a minúsculas"),
    BotCommand("length", "📏 Contar caracteres"),
    BotCommand("reverse", "🔄 Invertir texto"),
    
    # Información
    BotCommand("id", "🆔 Tu ID de usuario"),
    BotCommand("chatid", "💬 ID del chat"),
    
    # Utilidades
    BotCommand("weather", "🌤️ Consultar clima"),
    BotCommand("time", "🕐 Hora actual"),
    BotCommand("date", "📅 Fecha actual"),
    
    # Conversaciones
    BotCommand("start_form", "📝 Formulario interactivo"),
    
    # Juegos
    BotCommand("guess", "🎯 Juego de adivinanza"),
    BotCommand("rps", "✊ Piedra, papel o tijera"),
    
    # Utilidades avanzadas
    BotCommand("calc", "🧮 Calculadora simple"),
    BotCommand("random", "🎲 Número aleatorio"),
]

# --- Funciones auxiliares ---
async def send_typing_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Indica que el bot está escribiendo"""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

async def set_all_commands(application: Application):
    """Registra todos los comandos en Telegram automáticamente"""
    await application.bot.set_my_commands(COMMANDS)
    logger.info(f"✅ {len(COMMANDS)} comandos registrados en el menú del bot")

# --- Comandos básicos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Mensaje de bienvenida"""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📊 Ver menú", callback_data='menu')],
        [InlineKeyboardButton("🎮 Juegos", callback_data='games')],
        [InlineKeyboardButton("ℹ️ Ayuda", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎉 *¡Bienvenido {user.first_name}!*\n\n"
        f"Soy un bot con *TODAS* las funciones de Telegram API.\n"
        f"Usa /help para ver todos los comandos disponibles.\n\n"
        f"📌 *Comandos disponibles:* {len(COMMANDS)}\n"
        f"🎨 *Categorías:* Multimedia, Juegos, Utilidades, y más!\n\n"
        f"Selecciona una opción:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /menu - Mostrar menú interactivo"""
    keyboard = [
        [InlineKeyboardButton("📝 Básicos", callback_data='basicos'),
         InlineKeyboardButton("🖼️ Multimedia", callback_data='multimedia')],
        [InlineKeyboardButton("🎮 Juegos", callback_data='juegos'),
         InlineKeyboardButton("🔧 Utilidades", callback_data='utilidades')],
        [InlineKeyboardButton("ℹ️ Información", callback_data='info'),
         InlineKeyboardButton("📊 Encuestas", callback_data='encuestas')],
        [InlineKeyboardButton("❓ Ayuda", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📋 *Menú Principal*\n\n"
        "Selecciona una categoría para ver los comandos disponibles:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Lista completa de comandos"""
    help_text = """
🤖 *BOT CON TODOS LOS COMANDOS* 🚀

*📝 COMANDOS BÁSICOS:*
/start - Iniciar el bot
/help - Mostrar esta ayuda
/about - Información del bot
/menu - Ver menú interactivo

*🖼️ MULTIMEDIA:*
/photo - Enviar una foto
/video - Enviar un video
/document - Enviar un documento
/audio - Enviar un audio

*🎮 JUEGOS:*
/dice - Tirar un dado
/quiz - Juego de preguntas
/guess - Adivinar número
/rps - Piedra, papel o tijera

*📊 ENCUESTAS:*
/poll - Crear una encuesta

*🔧 UTILIDADES DE TEXTO:*
/echo [texto] - Repetir mensaje
/uppercase [texto] - Convertir a MAYÚSCULAS
/lowercase [texto] - Convertir a minúsculas
/length [texto] - Contar caracteres
/reverse [texto] - Invertir texto
/calc [operación] - Calculadora

*ℹ️ INFORMACIÓN:*
/id - Tu ID de usuario
/chatid - ID del chat
/time - Hora actual
/date - Fecha actual

*🌤️ UTILIDADES EXTERNAS:*
/weather [ciudad] - Consultar clima
/random [min] [max] - Número aleatorio

*📝 FORMULARIOS:*
/start_form - Formulario interactivo

🎯 *Total de comandos:* {total}

*Envía cualquier mensaje o multimedia para interactuar!*
"""
    await update.message.reply_text(
        help_text.format(total=len(COMMANDS)), 
        parse_mode='Markdown'
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /about - Información del bot"""
    await update.message.reply_text(
        "🤖 *Bot Super Completo*\n\n"
        f"📌 *Versión:* 3.0\n"
        f"⚙️ *Comandos:* {len(COMMANDS)}\n"
        f"🎨 *Funciones:* Todas las API de Telegram\n"
        f"🐍 *Lenguaje:* Python\n"
        f"🔧 *Framework:* python-telegram-bot\n\n"
        f"✨ *Características:*\n"
        f"• Menú interactivo con botones\n"
        f"• Soporte multimedia completo\n"
        f"• Juegos y encuestas\n"
        f"• Formularios conversacionales\n"
        f"• API externas integradas\n\n"
        f"🚀 *¡Pruébame con /help!*",
        parse_mode='Markdown'
    )

# --- Comandos multimedia ---
async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /photo - Enviar una foto"""
    await send_typing_action(update, context)
    photo_url = "https://picsum.photos/800/600"
    await update.message.reply_photo(
        photo=photo_url, 
        caption="📸 *Foto aleatoria*\n\nFuente: Lorem Picsum",
        parse_mode='Markdown'
    )

async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /video - Enviar un video"""
    await send_typing_action(update, context)
    video_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    await update.message.reply_video(
        video=video_url,
        caption="🎬 *Video de muestra*\n\nVideo en formato MP4",
        parse_mode='Markdown'
    )

async def send_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /document - Enviar un documento"""
    await send_typing_action(update, context)
    await update.message.reply_document(
        document="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        caption="📄 *Documento PDF*\n\nArchivo de ejemplo",
        parse_mode='Markdown'
    )

async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /audio - Enviar un audio"""
    await send_typing_action(update, context)
    audio_url = "https://file-examples.com/storage/feab0d9c102ac86c46cff1b/2017/11/file_example_MP3_700KB.mp3"
    await update.message.reply_audio(
        audio=audio_url,
        caption="🎵 *Audio de muestra*\n\nCanción de ejemplo",
        parse_mode='Markdown'
    )

# --- Juegos ---
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
        explanation="¡París es la capital de Francia! 🗼"
    )

async def guess_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /guess - Juego de adivinanza"""
    import random
    if 'secret_number' not in context.user_data:
        context.user_data['secret_number'] = random.randint(1, 100)
        await update.message.reply_text(
            "🎯 *Juego de Adivinanza*\n\n"
            "He pensado un número entre 1 y 100.\n"
            "Envía un número para adivinarlo!\n\n"
            "Usa /guess para reiniciar el juego.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"🔢 *Número secreto:* {context.user_data['secret_number']}\n"
            "¡Juego reiniciado! Adivina el nuevo número.",
            parse_mode='Markdown'
        )
        context.user_data['secret_number'] = random.randint(1, 100)

async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /rps - Piedra, papel o tijera"""
    keyboard = [
        [
            InlineKeyboardButton("✊ Piedra", callback_data='rps_piedra'),
            InlineKeyboardButton("✋ Papel", callback_data='rps_papel'),
            InlineKeyboardButton("✌️ Tijera", callback_data='rps_tijera')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎮 *Piedra, Papel o Tijera*\n\n"
        "¡Elige tu movimiento!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# --- Encuestas ---
async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /poll - Crear encuesta"""
    await update.message.reply_poll(
        question="¿Qué lenguaje de programación prefieres?",
        options=["Python 🐍", "JavaScript 🌐", "Java ☕", "Go 🚀", "Rust 🦀"],
        is_anonymous=False
    )

# --- Utilidades de texto ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /echo - Repetir mensaje"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔊 *Eco:* {text}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /echo [texto]")

async def uppercase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convertir a mayúsculas"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔠 *Mayúsculas:* {text.upper()}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /uppercase [texto]")

async def lowercase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convertir a minúsculas"""
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

async def reverse_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invertir texto"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔄 *Texto invertido:* {text[::-1]}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /reverse [texto]")

async def calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculadora simple"""
    if context.args:
        try:
            expression = ' '.join(context.args)
            result = eval(expression)
            await update.message.reply_text(f"🧮 *Resultado:* {result}", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Error en la expresión. Usa: /calc 2+2")
    else:
        await update.message.reply_text("❌ Usa: /calc [expresión]")

# --- Información ---
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtener ID del usuario"""
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 *Tu ID:* `{user.id}`\n"
        f"👤 *Username:* @{user.username or 'No tiene'}\n"
        f"📛 *Nombre:* {user.first_name} {user.last_name or ''}",
        parse_mode='Markdown'
    )

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtener ID del chat"""
    chat = update.effective_chat
    await update.message.reply_text(f"💬 *ID del chat:* `{chat.id}`", parse_mode='Markdown')

# --- Utilidades externas ---
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consultar clima"""
    if context.args:
        city = ' '.join(context.args)
        await send_typing_action(update, context)
        await update.message.reply_text(
            f"🌤️ *Clima en {city}*\n\n"
            f"🌡️ Temperatura: 22°C\n"
            f"💧 Humedad: 65%\n"
            f"🌬️ Viento: 12 km/h\n"
            f"☁️ Estado: Parcialmente nublado\n\n"
            f"*Nota:* Datos de ejemplo (API no configurada)",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Usa: /weather [ciudad]")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hora actual"""
    now = datetime.now()
    await update.message.reply_text(f"🕐 *Hora actual:* {now.strftime('%H:%M:%S')}", parse_mode='Markdown')

async def date_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fecha actual"""
    now = datetime.now()
    await update.message.reply_text(f"📅 *Fecha actual:* {now.strftime('%d/%m/%Y')}", parse_mode='Markdown')

async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Número aleatorio"""
    import random
    if len(context.args) == 2:
        try:
            min_val = int(context.args[0])
            max_val = int(context.args[1])
            num = random.randint(min_val, max_val)
            await update.message.reply_text(f"🎲 *Número aleatorio:* {num}", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Usa: /random [min] [max]")
    else:
        num = random.randint(1, 100)
        await update.message.reply_text(f"🎲 *Número aleatorio:* {num}", parse_mode='Markdown')

# --- Conversaciones ---
async def start_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Iniciar formulario"""
    await update.message.reply_text("📝 *Formulario Interactivo*\n\n¿Cuál es tu nombre?", parse_mode='Markdown')
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"Encantado, {context.user_data['name']}. ¿Cuántos años tienes?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    await update.message.reply_text("¿Cuál es tu color favorito?")
    return COLOR

async def get_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['color'] = update.message.text
    await update.message.reply_text(
        f"✅ *Formulario completado!*\n\n"
        f"📛 *Nombre:* {context.user_data['name']}\n"
        f"🎂 *Edad:* {context.user_data['age']}\n"
        f"🎨 *Color:* {context.user_data['color']}",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Formulario cancelado.")
    return ConversationHandler.END

# --- Callbacks ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar botones"""
    query = update.callback_query
    await query.answer()
    
    # Juego RPS
    if query.data.startswith('rps_'):
        move = query.data.split('_')[1]
        import random
        options = {'piedra': '✊', 'papel': '✋', 'tijera': '✌️'}
        bot_move = random.choice(list(options.keys()))
        
        result = ""
        if move == bot_move:
            result = "¡Empate! 🤝"
        elif (move == 'piedra' and bot_move == 'tijera') or \
             (move == 'papel' and bot_move == 'piedra') or \
             (move == 'tijera' and bot_move == 'papel'):
            result = "¡Ganaste! 🎉"
        else:
            result = "Perdiste 😢"
        
        await query.edit_message_text(
            f"🎮 *Piedra, Papel o Tijera*\n\n"
            f"Tú: {options[move]}\n"
            f"Bot: {options[bot_move]}\n\n"
            f"*Resultado:* {result}",
            parse_mode='Markdown'
        )
        return
    
    # Menú principal
    categories = {
        'basicos': "📝 *Comandos Básicos:*\n/start, /help, /about, /menu",
        'multimedia': "🖼️ *Comandos Multimedia:*\n/photo, /video, /document, /audio",
        'juegos': "🎮 *Juegos:*\n/dice, /quiz, /guess, /rps",
        'utilidades': "🔧 *Utilidades:*\n/echo, /uppercase, /lowercase, /length, /reverse, /calc",
        'info': "ℹ️ *Información:*\n/id, /chatid, /time, /date",
        'encuestas': "📊 *Encuestas:*\n/poll"
    }
    
    if query.data in categories:
        await query.edit_message_text(
            f"{categories[query.data]}\n\nUsa /help para ver todos los comandos.",
            parse_mode='Markdown'
        )
    elif query.data == 'menu':
        await query.edit_message_text(
            "📋 *Menú Principal*\n\n"
            "Selecciona una categoría:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Básicos", callback_data='basicos'),
                 InlineKeyboardButton("🖼️ Multimedia", callback_data='multimedia')],
                [InlineKeyboardButton("🎮 Juegos", callback_data='juegos'),
                 InlineKeyboardButton("🔧 Utilidades", callback_data='utilidades')],
                [InlineKeyboardButton("ℹ️ Información", callback_data='info'),
                 InlineKeyboardButton("📊 Encuestas", callback_data='encuestas')],
            ]),
            parse_mode='Markdown'
        )
    elif query.data == 'games':
        await query.edit_message_text(
            "🎮 *Juegos Disponibles:*\n\n"
            "🎲 /dice - Lanza un dado\n"
            "🧠 /quiz - Preguntas y respuestas\n"
            "🎯 /guess - Adivina el número\n"
            "✊ /rps - Piedra, papel o tijera",
            parse_mode='Markdown'
        )
    elif query.data == 'help':
        await help_command(update, context)
        await query.delete()

# --- Manejo de mensajes multimedia ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    await update.message.reply_text(f"📸 ¡Foto recibida! Tamaño: {photo.file_size} bytes")

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = update.message.sticker
    await update.message.reply_text(f"🎨 ¡Sticker! Emoji: {sticker.emoji}")

# --- Función principal ---
async def post_init(application: Application):
    """Configurar comandos después de iniciar"""
    await set_all_commands(application)
    logger.info(f"✅ Bot iniciado con {len(COMMANDS)} comandos registrados")

def main():
    """Función principal"""
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Registrar todos los comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("menu", menu_command))
    
    # Multimedia
    application.add_handler(CommandHandler("photo", send_photo))
    application.add_handler(CommandHandler("video", send_video))
    application.add_handler(CommandHandler("document", send_document))
    application.add_handler(CommandHandler("audio", send_audio))
    
    # Juegos
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("guess", guess_game))
    application.add_handler(CommandHandler("rps", rps_game))
    
    # Encuestas
    application.add_handler(CommandHandler("poll", poll_command))
    
    # Utilidades texto
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CommandHandler("uppercase", uppercase))
    application.add_handler(CommandHandler("lowercase", lowercase))
    application.add_handler(CommandHandler("length", length_command))
    application.add_handler(CommandHandler("reverse", reverse_text))
    application.add_handler(CommandHandler("calc", calculator))
    
    # Información
    application.add_handler(CommandHandler("id", get_id))
    application.add_handler(CommandHandler("chatid", get_chat_id))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("date", date_command))
    
    # Utilidades externas
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("random", random_number))
    
    # Formulario conversacional
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
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Manejo multimedia
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    
    # Mensajes de texto (para el juego de adivinanza)
    async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'secret_number' in context.user_data:
            try:
                guess = int(update.message.text)
                secret = context.user_data['secret_number']
                if guess < secret:
                    await update.message.reply_text("📈 ¡Más alto!")
                elif guess > secret:
                    await update.message.reply_text("📉 ¡Más bajo!")
                else:
                    await update.message.reply_text("🎉 ¡Correcto! ¡Ganaste! 🎉")
                    del context.user_data['secret_number']
            except ValueError:
                pass
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guess))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Iniciar bot
    logger.info("🚀 Bot iniciado con TODOS los comandos registrados")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()