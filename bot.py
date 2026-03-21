import os
import logging
import asyncio
import time
import threading
import random
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

# --- LISTA COMPLETA DE COMANDOS (25 comandos) ---
COMMANDS_LIST = [
    BotCommand("start", "🚀 Iniciar el bot"),
    BotCommand("help", "❓ Mostrar ayuda"),
    BotCommand("about", "ℹ️ Información del bot"),
    BotCommand("menu", "📋 Ver menú interactivo"),
    BotCommand("photo", "🖼️ Enviar una foto"),
    BotCommand("video", "🎬 Enviar un video"),
    BotCommand("document", "📄 Enviar un documento"),
    BotCommand("audio", "🎵 Enviar un audio"),
    BotCommand("poll", "📊 Crear una encuesta"),
    BotCommand("dice", "🎲 Tirar un dado"),
    BotCommand("quiz", "🧠 Juego de preguntas"),
    BotCommand("echo", "🔊 Repetir mensaje"),
    BotCommand("uppercase", "🔠 Convertir a mayúsculas"),
    BotCommand("lowercase", "🔡 Convertir a minúsculas"),
    BotCommand("length", "📏 Contar caracteres"),
    BotCommand("reverse", "🔄 Invertir texto"),
    BotCommand("id", "🆔 Tu ID de usuario"),
    BotCommand("chatid", "💬 ID del chat"),
    BotCommand("weather", "🌤️ Consultar clima"),
    BotCommand("time", "🕐 Hora actual"),
    BotCommand("date", "📅 Fecha actual"),
    BotCommand("start_form", "📝 Formulario interactivo"),
    BotCommand("guess", "🎯 Juego de adivinanza"),
    BotCommand("rps", "✊ Piedra, papel o tijera"),
    BotCommand("calc", "🧮 Calculadora simple"),
    BotCommand("random", "🎲 Número aleatorio"),
]

# --- FUNCIÓN PARA KEEP-ALIVE ---
def start_keep_alive():
    """Mantiene el bot activo con pings periódicos"""
    def keep_alive():
        import requests
        while True:
            try:
                requests.get('https://api.telegram.org', timeout=5)
                logger.info("🔄 Keep-alive ping enviado")
            except Exception as e:
                logger.warning(f"⚠️ Ping falló: {e}")
            time.sleep(300)  # 5 minutos
    
    thread = threading.Thread(target=keep_alive, daemon=True)
    thread.start()
    logger.info("✅ Keep-alive thread iniciado")

# --- FUNCIÓN PARA REGISTRAR COMANDOS ---
async def register_commands(application: Application):
    """Registrar todos los comandos en Telegram"""
    try:
        await application.bot.set_my_commands(COMMANDS_LIST)
        logger.info(f"✅ {len(COMMANDS_LIST)} comandos registrados exitosamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al registrar comandos: {e}")
        return False

# --- Funciones auxiliares ---
async def send_typing_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

# --- Comandos básicos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📊 Ver comandos", callback_data='menu')],
        [InlineKeyboardButton("🎮 Juegos", callback_data='games')],
        [InlineKeyboardButton("❓ Ayuda", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎉 *¡Bienvenido {user.first_name}!*\n\n"
        f"Soy un bot con *TODOS* los comandos de Telegram API.\n"
        f"🔧 *Comandos disponibles:* {len(COMMANDS_LIST)}\n\n"
        f"📌 *Escribe / para ver todos los comandos*\n"
        f"✨ *O selecciona una opción:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Básicos", callback_data='basicos'),
         InlineKeyboardButton("🖼️ Multimedia", callback_data='multimedia')],
        [InlineKeyboardButton("🎮 Juegos", callback_data='juegos'),
         InlineKeyboardButton("🔧 Utilidades", callback_data='utilidades')],
        [InlineKeyboardButton("ℹ️ Información", callback_data='info'),
         InlineKeyboardButton("📊 Encuestas", callback_data='encuestas')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📋 *Menú de Comandos*\n\nSelecciona una categoría:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
🤖 *BOT CON TODOS LOS COMANDOS* 🚀

*📝 BÁSICOS:*
/start, /help, /about, /menu

*🖼️ MULTIMEDIA:*
/photo, /video, /document, /audio

*🎮 JUEGOS:*
/dice, /quiz, /guess, /rps

*📊 ENCUESTAS:*
/poll

*🔧 UTILIDADES:*
/echo, /uppercase, /lowercase, /length, /reverse, /calc, /random

*ℹ️ INFORMACIÓN:*
/id, /chatid, /time, /date, /weather

*📝 FORMULARIOS:*
/start_form

🎯 *Total: {len(COMMANDS_LIST)} comandos*

*Escribe / para ver la lista completa en Telegram*
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 *Bot Super Completo*\n\n"
        f"📌 *Versión:* 3.0\n"
        f"⚙️ *Comandos:* {len(COMMANDS_LIST)}\n"
        f"🎨 *Funciones:* Todas las API de Telegram\n"
        f"🚀 *Listo para usar!*\n\n"
        f"💡 *Escribe / para ver todos los comandos*",
        parse_mode='Markdown'
    )

# --- Comandos multimedia ---
async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing_action(update, context)
    photo_url = "https://picsum.photos/800/600"
    await update.message.reply_photo(
        photo=photo_url, 
        caption="📸 *Foto aleatoria*",
        parse_mode='Markdown'
    )

async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing_action(update, context)
    video_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    await update.message.reply_video(
        video=video_url,
        caption="🎬 *Video de muestra*",
        parse_mode='Markdown'
    )

async def send_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing_action(update, context)
    await update.message.reply_document(
        document="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        caption="📄 *Documento PDF*",
        parse_mode='Markdown'
    )

async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing_action(update, context)
    audio_url = "https://file-examples.com/storage/feab0d9c102ac86c46cff1b/2017/11/file_example_MP3_700KB.mp3"
    await update.message.reply_audio(
        audio=audio_url,
        caption="🎵 *Audio de muestra*",
        parse_mode='Markdown'
    )

# --- Juegos ---
async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice()

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_poll(
        question="¿Cuál es la capital de Francia?",
        options=["Londres", "Berlín", "París", "Madrid"],
        type="quiz",
        correct_option_id=2,
        explanation="¡París es la capital de Francia! 🗼"
    )

async def guess_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'secret_number' not in context.user_data:
        context.user_data['secret_number'] = random.randint(1, 100)
        await update.message.reply_text(
            "🎯 *Juego de Adivinanza*\n\n"
            "He pensado un número entre 1 y 100.\n"
            "Envía un número para adivinarlo!\n\n"
            "Usa /guess para reiniciar.",
            parse_mode='Markdown'
        )
    else:
        context.user_data['secret_number'] = random.randint(1, 100)
        await update.message.reply_text("🎯 ¡Juego reiniciado! Adivina el nuevo número.")

async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("✊ Piedra", callback_data='rps_piedra'),
        InlineKeyboardButton("✋ Papel", callback_data='rps_papel'),
        InlineKeyboardButton("✌️ Tijera", callback_data='rps_tijera')
    ]]
    await update.message.reply_text(
        "🎮 *Piedra, Papel o Tijera*\n\n¡Elige tu movimiento!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# --- Encuestas ---
async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_poll(
        question="¿Qué lenguaje prefieres?",
        options=["Python 🐍", "JavaScript 🌐", "Java ☕", "Go 🚀"],
        is_anonymous=False
    )

# --- Utilidades de texto ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔊 *Eco:* {text}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /echo [texto]")

async def uppercase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔠 *Mayúsculas:* {text.upper()}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /uppercase [texto]")

async def lowercase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔡 *Minúsculas:* {text.lower()}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /lowercase [texto]")

async def length_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"📏 *Longitud:* {len(text)}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /length [texto]")

async def reverse_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔄 *Invertido:* {text[::-1]}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /reverse [texto]")

async def calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            expression = ' '.join(context.args)
            result = eval(expression)
            await update.message.reply_text(f"🧮 *Resultado:* {result}", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Error en la expresión. Usa: /calc 2+2")
    else:
        await update.message.reply_text("❌ Usa: /calc [expresión]")

async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 2:
        try:
            min_val, max_val = map(int, context.args[:2])
            num = random.randint(min_val, max_val)
            await update.message.reply_text(f"🎲 *Aleatorio:* {num}", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Usa: /random [min] [max]")
    else:
        await update.message.reply_text(f"🎲 *Aleatorio:* {random.randint(1, 100)}", parse_mode='Markdown')

# --- Información ---
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🆔 *ID:* `{user.id}`", parse_mode='Markdown')

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(f"💬 *Chat ID:* `{chat.id}`", parse_mode='Markdown')

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(f"🕐 *Hora:* {now.strftime('%H:%M:%S')}", parse_mode='Markdown')

async def date_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(f"📅 *Fecha:* {now.strftime('%d/%m/%Y')}", parse_mode='Markdown')

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        city = ' '.join(context.args)
        await update.message.reply_text(
            f"🌤️ *Clima en {city}:*\n"
            f"🌡️ Temperatura: 22°C\n"
            f"💧 Humedad: 65%\n"
            f"☁️ Estado: Parcialmente nublado",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Usa: /weather [ciudad]")

# --- Formulario ---
async def start_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 *¿Cuál es tu nombre?*", parse_mode='Markdown')
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("🎂 *¿Cuántos años tienes?*", parse_mode='Markdown')
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    await update.message.reply_text("🎨 *¿Cuál es tu color favorito?*", parse_mode='Markdown')
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
    await update.message.reply_text("❌ Cancelado.")
    return ConversationHandler.END

# --- Callbacks ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('rps_'):
        move = query.data.split('_')[1]
        options = {'piedra': '✊', 'papel': '✋', 'tijera': '✌️'}
        bot_move = random.choice(list(options.keys()))
        
        if move == bot_move:
            result = "Empate 🤝"
        elif (move == 'piedra' and bot_move == 'tijera') or \
             (move == 'papel' and bot_move == 'piedra') or \
             (move == 'tijera' and bot_move == 'papel'):
            result = "Ganaste 🎉"
        else:
            result = "Perdiste 😢"
        
        await query.edit_message_text(
            f"🎮 *RPS*\nTú: {options[move]}\nBot: {options[bot_move]}\n\n*Resultado:* {result}",
            parse_mode='Markdown'
        )
        return
    
    categories = {
        'basicos': "📝 */start, /help, /about, /menu*",
        'multimedia': "🖼️ */photo, /video, /document, /audio*",
        'juegos': "🎮 */dice, /quiz, /guess, /rps*",
        'utilidades': "🔧 */echo, /uppercase, /lowercase, /length, /reverse, /calc, /random*",
        'info': "ℹ️ */id, /chatid, /time, /date, /weather*",
        'encuestas': "📊 */poll*"
    }
    
    if query.data in categories:
        await query.edit_message_text(
            f"{categories[query.data]}\n\n✨ *Escribe / para ver todos*",
            parse_mode='Markdown'
        )
    elif query.data == 'menu':
        keyboard = [
            [InlineKeyboardButton("📝 Básicos", callback_data='basicos'),
             InlineKeyboardButton("🖼️ Multimedia", callback_data='multimedia')],
            [InlineKeyboardButton("🎮 Juegos", callback_data='juegos'),
             InlineKeyboardButton("🔧 Utilidades", callback_data='utilidades')],
            [InlineKeyboardButton("ℹ️ Información", callback_data='info'),
             InlineKeyboardButton("📊 Encuestas", callback_data='encuestas')],
        ]
        await query.edit_message_text(
            "📋 *Categorías:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    elif query.data == 'games':
        await query.edit_message_text(
            "🎮 */dice, /quiz, /guess, /rps*\n\n✨ *Escribe / para ver todos*",
            parse_mode='Markdown'
        )
    elif query.data == 'help':
        await help_command(update, context)
        await query.delete()

# --- Manejo de mensajes ---
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

# --- MAIN ---
def main():
    # Iniciar keep-alive
    start_keep_alive()
    
    # Crear aplicación
    application = Application.builder().token(TOKEN).build()
    
    # Registrar comandos
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(register_commands(application))
    loop.close()
    
    # Comandos básicos
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
    
    # Utilidades
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CommandHandler("uppercase", uppercase))
    application.add_handler(CommandHandler("lowercase", lowercase))
    application.add_handler(CommandHandler("length", length_command))
    application.add_handler(CommandHandler("reverse", reverse_text))
    application.add_handler(CommandHandler("calc", calculator))
    application.add_handler(CommandHandler("random", random_number))
    
    # Información
    application.add_handler(CommandHandler("id", get_id))
    application.add_handler(CommandHandler("chatid", get_chat_id))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("date", date_command))
    application.add_handler(CommandHandler("weather", weather_command))
    
    # Formulario
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
    
    # Mensajes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guess))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Iniciar bot
    logger.info("🚀 Bot iniciando con keep-alive activo...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()