import os
import logging
import random
import string
import requests
import json
import hashlib
import base64
import time
import asyncio
import math
import re
import urllib.parse
from datetime import datetime, timedelta
from collections import Counter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes, CallbackQueryHandler, ConversationHandler
)

# --- Configuración ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN no está configurado")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados para conversaciones
NAME, AGE, COLOR, TASK, REMINDER_TEXT, REMINDER_TIME = range(6)

# --- LISTA DE COMANDOS (60+ comandos) ---
COMMANDS_LIST = [
    # Básicos
    BotCommand("start", "🚀 Iniciar bot"),
    BotCommand("help", "❓ Ayuda completa"),
    BotCommand("menu", "📋 Menú interactivo"),
    BotCommand("about", "ℹ️ Info del bot"),
    
    # Utilidades de texto
    BotCommand("echo", "🔊 Repetir mensaje"),
    BotCommand("reverse", "🔄 Invertir texto"),
    BotCommand("count", "📏 Contar caracteres/palabras"),
    BotCommand("uppercase", "🔠 Convertir a mayúsculas"),
    BotCommand("lowercase", "🔡 Convertir a minúsculas"),
    BotCommand("capitalize", "📝 Capitalizar texto"),
    BotCommand("binary", "💾 Texto a binario"),
    BotCommand("base64", "🔐 Codificar en Base64"),
    BotCommand("md5", "🔒 Hash MD5"),
    BotCommand("palindrome", "🔄 Verificar palíndromo"),
    
    # Matemáticas
    BotCommand("calc", "🧮 Calculadora"),
    BotCommand("sqrt", "√ Raíz cuadrada"),
    BotCommand("power", "🔢 Potencia"),
    BotCommand("random", "🎲 Número aleatorio"),
    BotCommand("dice", "🎲 Tirar dado"),
    BotCommand("coin", "💰 Tirar moneda"),
    BotCommand("prime", "🔢 Verificar número primo"),
    BotCommand("fibonacci", "📊 Secuencia Fibonacci"),
    BotCommand("factorial", "! Factorial"),
    
    # Fecha y hora
    BotCommand("time", "🕐 Hora actual"),
    BotCommand("date", "📅 Fecha actual"),
    BotCommand("calendar", "📆 Calendario"),
    BotCommand("age", "🎂 Calcular edad"),
    BotCommand("countdown", "⏰ Cuenta regresiva"),
    
    # Conversión de unidades
    BotCommand("currency", "💱 Conversión de moneda"),
    BotCommand("length", "📏 Convertir longitud"),
    BotCommand("weight", "⚖️ Convertir peso"),
    BotCommand("temperature", "🌡️ Convertir temperatura"),
    BotCommand("timezone", "🌍 Zonas horarias"),
    
    # Juegos
    BotCommand("trivia", "🧠 Preguntas trivia"),
    BotCommand("riddle", "🤔 Acertijos"),
    BotCommand("hangman", "🎮 Juego del ahorcado"),
    BotCommand("rps", "✊ Piedra papel tijera"),
    BotCommand("guess", "🔢 Adivina el número"),
    BotCommand("wordle", "📝 Wordle"),
    
    # Multimedia
    BotCommand("cat", "🐱 Foto de gato"),
    BotCommand("dog", "🐶 Foto de perro"),
    BotCommand("quote", "💬 Cita aleatoria"),
    BotCommand("fact", "📚 Dato curioso"),
    BotCommand("joke", "😂 Chiste aleatorio"),
    BotCommand("meme", "🖼️ Meme"),
    BotCommand("anime", "🎨 Anime quote"),
    BotCommand("advice", "💡 Consejo aleatorio"),
    
    # Utilidades
    BotCommand("weather", "🌤️ Clima (demo)"),
    BotCommand("ip", "🌐 Tu IP"),
    BotCommand("userinfo", "👤 Info de usuario"),
    BotCommand("chatid", "💬 ID del chat"),
    BotCommand("qr", "📱 Generar QR"),
    BotCommand("password", "🔑 Generar contraseña"),
    BotCommand("uuid", "🆔 Generar UUID"),
    BotCommand("lorem", "📝 Texto Lorem Ipsum"),
    
    # Herramientas
    BotCommand("urlencode", "🔗 Codificar URL"),
    BotCommand("urldecode", "🔓 Decodificar URL"),
    BotCommand("color", "🎨 Color aleatorio"),
    BotCommand("emoji", "😊 Emoji info"),
    BotCommand("bmi", "📊 Calcular IMC"),
    
    # Recordatorios y notas
    BotCommand("note", "📝 Guardar nota"),
    BotCommand("notes", "📋 Ver notas"),
    BotCommand("remind", "⏰ Recordatorio"),
    
    # Conversaciones
    BotCommand("survey", "📊 Encuesta interactiva"),
    BotCommand("todo", "✅ Lista de tareas"),
    
    # Social
    BotCommand("say", "💬 Decir algo"),
    BotCommand("insult", "😈 Insulto aleatorio"),
    BotCommand("compliment", "💝 Cumplido aleatorio"),
]

# --- Funciones auxiliares ---
async def send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

async def register_commands(app):
    await app.bot.set_my_commands(COMMANDS_LIST)
    logger.info(f"✅ {len(COMMANDS_LIST)} comandos registrados")

# --- APIs Públicas (sin API key) ---
def get_random_cat():
    try:
        response = requests.get("https://api.thecatapi.com/v1/images/search", timeout=5)
        return response.json()[0]["url"]
    except:
        return "https://cataas.com/cat"

def get_random_dog():
    try:
        response = requests.get("https://dog.ceo/api/breeds/image/random", timeout=5)
        return response.json()["message"]
    except:
        return "https://images.dog.ceo/breeds/hound-afghan/n02088094_1003.jpg"

def get_random_quote():
    try:
        response = requests.get("https://api.quotable.io/random", timeout=5)
        data = response.json()
        return f"💬 *{data['content']}*\n\n— *{data['author']}*"
    except:
        return "💬 *La vida es lo que pasa mientras estás ocupado haciendo otros planes.*\n\n— *John Lennon*"

def get_random_fact():
    facts = [
        "🐱 Los gatos tienen 32 músculos en cada oreja.",
        "🐝 Las abejas pueden volar a 25 km/h.",
        "🌊 El océano Pacífico es más grande que la Luna.",
        "🦒 Las jirafas duermen solo 30 minutos al día.",
        "🐧 Los pingüinos propuestas con piedras.",
        "🦋 Las mariposas saborean con las patas.",
        "🐙 Los pulpos tienen tres corazones.",
        "🦷 Los humanos tienen la misma cantidad de huesos en el cuello que las jirafas (7).",
        "🍕 La pizza más cara del mundo cuesta $12,000.",
        "🎵 La canción más reproducida es 'Despacito' con 8 mil millones de vistas."
    ]
    return random.choice(facts)

def get_random_joke():
    jokes = [
        "¿Por qué los pájaros vuelan hacia el sur? Porque caminando tardarían mucho.",
        "¿Qué le dice un techo a otro? Te echo de menos.",
        "¿Cómo se llama el campeón de buceo japonés? Tokofondo.",
        "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
        "¿Por qué los programadores odian la naturaleza? Porque tiene demasiados bugs."
    ]
    return random.choice(jokes)

def get_random_meme():
    memes = [
        "https://i.imgur.com/5qR8ZkE.jpg",
        "https://i.imgur.com/3QzQzQz.jpg",
        "https://i.imgur.com/8q8q8q8.jpg",
    ]
    return random.choice(memes)

def get_random_advice():
    try:
        response = requests.get("https://api.adviceslip.com/advice", timeout=5)
        return response.json()["slip"]["advice"]
    except:
        return "Sé amable con los demás."

# --- Comandos básicos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📋 Ver comandos", callback_data='menu')],
        [InlineKeyboardButton("🎮 Juegos", callback_data='games')],
        [InlineKeyboardButton("🔧 Utilidades", callback_data='utils')]
    ]
    await update.message.reply_text(
        f"🎉 *¡Bienvenido {user.first_name}!*\n\n"
        f"Soy un bot con *{len(COMMANDS_LIST)}+ funciones*\n"
        f"📌 *Escribe / para ver todos los comandos*\n"
        f"✨ *O selecciona una opción:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Texto", callback_data='text_tools'),
         InlineKeyboardButton("🧮 Matemáticas", callback_data='math_tools')],
        [InlineKeyboardButton("🎮 Juegos", callback_data='games'),
         InlineKeyboardButton("🖼️ Multimedia", callback_data='media')],
        [InlineKeyboardButton("🔧 Utilidades", callback_data='utils'),
         InlineKeyboardButton("📊 Info", callback_data='info_tools')],
    ]
    await update.message.reply_text(
        "📋 *Menú de Categorías*\n\nSelecciona una:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
🤖 *BOT ULTRA COMPLETO* 🚀
*Total: {len(COMMANDS_LIST)} comandos*

*📝 TEXTO:*
/echo, /reverse, /count, /uppercase, /lowercase, /capitalize, /binary, /base64, /md5, /palindrome

*🧮 MATEMÁTICAS:*
/calc, /sqrt, /power, /random, /dice, /coin, /prime, /fibonacci, /factorial

*📅 FECHA/HORA:*
/time, /date, /calendar, /age, /countdown

*🔄 CONVERSIONES:*
/currency, /length, /weight, /temperature, /timezone

*🎮 JUEGOS:*
/trivia, /riddle, /hangman, /rps, /guess, /wordle

*🖼️ MULTIMEDIA:*
/cat, /dog, /quote, /fact, /joke, /meme, /advice

*🔧 UTILIDADES:*
/weather, /ip, /userinfo, /chatid, /qr, /password, /uuid, /lorem, /color, /bmi

*📝 NOTAS:*
/note, /notes, /remind, /todo

✨ *Escribe / para ver todos los comandos en tu Telegram*
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 *Bot Mega Completo*\n\n"
        f"📌 *Versión:* 5.0\n"
        f"⚙️ *Comandos:* {len(COMMANDS_LIST)}\n"
        f"🎨 *Funciones:* 60+ utilidades\n"
        f"🐍 *Python:* 3.11\n"
        f"🔧 *Framework:* python-telegram-bot\n\n"
        f"✨ *Sin API keys necesarias!*\n"
        f"🚀 *¡Pruébame con /menu!*",
        parse_mode='Markdown'
    )

# --- Utilidades de texto ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔊 *Eco:* {text}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Usa: /echo [texto]")

async def reverse_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"🔄 *Invertido:* {text[::-1]}", parse_mode='Markdown')

async def count_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        chars = len(text)
        words = len(text.split())
        await update.message.reply_text(
            f"📏 *Estadísticas:*\n"
            f"Caracteres: {chars}\n"
            f"Palabras: {words}\n"
            f"Espacios: {text.count(' ')}",
            parse_mode='Markdown'
        )

async def uppercase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(f"🔠 *Mayúsculas:* {' '.join(context.args).upper()}", parse_mode='Markdown')

async def lowercase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(f"🔡 *Minúsculas:* {' '.join(context.args).lower()}", parse_mode='Markdown')

async def capitalize_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(f"📝 *Capitalizado:* {' '.join(context.args).title()}", parse_mode='Markdown')

async def to_binary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        binary = ' '.join(format(ord(c), '08b') for c in text)
        await update.message.reply_text(f"💾 *Binario:* `{binary[:200]}`", parse_mode='Markdown')

async def base64_encode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        encoded = base64.b64encode(text.encode()).decode()
        await update.message.reply_text(f"🔐 *Base64:* `{encoded}`", parse_mode='Markdown')

async def md5_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        hash_md5 = hashlib.md5(text.encode()).hexdigest()
        await update.message.reply_text(f"🔒 *MD5:* `{hash_md5}`", parse_mode='Markdown')

async def palindrome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args).lower().replace(' ', '')
        is_palindrome = text == text[::-1]
        result = "✅ *Es palíndromo*" if is_palindrome else "❌ *No es palíndromo*"
        await update.message.reply_text(result, parse_mode='Markdown')

# --- Matemáticas ---
async def calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            expr = ' '.join(context.args)
            # Reemplazar símbolos comunes
            expr = expr.replace('x', '*').replace('^', '**')
            result = eval(expr)
            await update.message.reply_text(f"🧮 *Resultado:* `{result}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Error en la expresión")

async def sqrt_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            num = float(context.args[0])
            result = math.sqrt(num)
            await update.message.reply_text(f"√ *Raíz cuadrada:* `{result}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Usa: /sqrt [número]")

async def power_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 2:
        try:
            base = float(context.args[0])
            exp = float(context.args[1])
            result = base ** exp
            await update.message.reply_text(f"🔢 *Potencia:* `{result}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Usa: /power [base] [exponente]")

async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 2:
        try:
            min_val = int(context.args[0])
            max_val = int(context.args[1])
            num = random.randint(min_val, max_val)
            await update.message.reply_text(f"🎲 *Número aleatorio:* `{num}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Usa: /random [min] [max]")
    else:
        num = random.randint(1, 100)
        await update.message.reply_text(f"🎲 *Número aleatorio:* `{num}`", parse_mode='Markdown')

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice()

async def coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = random.choice(["Cara 🪙", "Cruz 💰"])
    await update.message.reply_text(f"🪙 *Resultado:* {result}", parse_mode='Markdown')

async def prime_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            num = int(context.args[0])
            if num < 2:
                is_prime = False
            else:
                is_prime = all(num % i != 0 for i in range(2, int(math.sqrt(num)) + 1))
            result = "✅ *Es primo*" if is_prime else "❌ *No es primo*"
            await update.message.reply_text(result, parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Usa: /prime [número]")

async def fibonacci_seq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            n = int(context.args[0])
            fib = [0, 1]
            for i in range(2, n):
                fib.append(fib[-1] + fib[-2])
            await update.message.reply_text(f"📊 *Fibonacci:* `{fib[:n]}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Usa: /fibonacci [n]")

async def factorial_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            n = int(context.args[0])
            result = math.factorial(n)
            await update.message.reply_text(f"! *Factorial:* `{result}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Usa: /factorial [número]")

# --- Fecha y hora ---
async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(f"🕐 *Hora:* `{now.strftime('%H:%M:%S')}`", parse_mode='Markdown')

async def date_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(f"📅 *Fecha:* `{now.strftime('%d/%m/%Y')}`", parse_mode='Markdown')

async def calendar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    cal = f"📆 *{now.strftime('%B %Y')}*\n\n"
    cal += "Lun Mar Mié Jue Vie Sáb Dom\n"
    # Simplificado - muestra el mes actual
    await update.message.reply_text(cal, parse_mode='Markdown')

async def age_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            birth = datetime.strptime(context.args[0], '%d/%m/%Y')
            age = datetime.now() - birth
            years = age.days // 365
            await update.message.reply_text(f"🎂 *Edad:* `{years} años`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Usa: /age [dd/mm/yyyy]")

# --- Multimedia con APIs públicas ---
async def cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing(update, context)
    url = get_random_cat()
    await update.message.reply_photo(url, caption="🐱 *¡Mira este gatito!*", parse_mode='Markdown')

async def dog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing(update, context)
    url = get_random_dog()
    await update.message.reply_photo(url, caption="🐶 *¡Qué perrito tan lindo!*", parse_mode='Markdown')

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_typing(update, context)
    quote_text = get_random_quote()
    await update.message.reply_text(quote_text, parse_mode='Markdown')

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fact_text = get_random_fact()
    await update.message.reply_text(f"📚 *Dato curioso:*\n{fact_text}", parse_mode='Markdown')

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke_text = get_random_joke()
    await update.message.reply_text(f"😂 *Chiste:*\n{joke_text}", parse_mode='Markdown')

async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = get_random_meme()
    await update.message.reply_photo(url, caption="🖼️ *Meme del día*", parse_mode='Markdown')

async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    advice_text = get_random_advice()
    await update.message.reply_text(f"💡 *Consejo:*\n{advice_text}", parse_mode='Markdown')

# --- Utilidades ---
async def get_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        ip = response.json()["ip"]
        await update.message.reply_text(f"🌐 *Tu IP:* `{ip}`", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ No se pudo obtener la IP")

async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    info = (
        f"👤 *Información del usuario*\n\n"
        f"🆔 *ID:* `{user.id}`\n"
        f"📛 *Nombre:* {user.first_name}\n"
        f"👥 *Username:* @{user.username or 'No tiene'}\n"
        f"🔗 *Link:* [Perfil](tg://user?id={user.id})"
    )
    await update.message.reply_text(info, parse_mode='Markdown')

async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(f"💬 *Chat ID:* `{chat.id}`", parse_mode='Markdown')

async def password_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    length = 12
    if context.args:
        try:
            length = int(context.args[0])
            length = min(length, 50)
        except:
            pass
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(length))
    await update.message.reply_text(f"🔑 *Contraseña generada:* `{password}`", parse_mode='Markdown')

async def uuid_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import uuid
    uid = uuid.uuid4()
    await update.message.reply_text(f"🆔 *UUID:* `{uid}`", parse_mode='Markdown')

async def lorem_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
    await update.message.reply_text(f"📝 *Lorem Ipsum:*\n{lorem}", parse_mode='Markdown')

async def color_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    colors = ["Rojo 🔴", "Azul 🔵", "Verde 🟢", "Amarillo 🟡", "Morado 🟣", "Naranja 🟠"]
    await update.message.reply_text(f"🎨 *Color aleatorio:* {random.choice(colors)}", parse_mode='Markdown')

async def bmi_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 2:
        try:
            weight = float(context.args[0])
            height = float(context.args[1]) / 100
            bmi = weight / (height ** 2)
            category = "Bajo peso" if bmi < 18.5 else "Normal" if bmi < 25 else "Sobrepeso" if bmi < 30 else "Obesidad"
            await update.message.reply_text(
                f"📊 *IMC:* `{bmi:.2f}`\n"
                f"📌 *Categoría:* {category}",
                parse_mode='Markdown'
            )
        except:
            await update.message.reply_text("❌ Usa: /bmi [peso_kg] [altura_cm]")

# --- Juegos ---
async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        ("¿Cuál es la capital de Francia?", "París"),
        ("¿Qué planeta es conocido como el planeta rojo?", "Marte"),
        ("¿Cuántos días tiene un año bisiesto?", "366"),
        ("¿Quién pintó la Mona Lisa?", "Leonardo da Vinci"),
    ]
    q, a = random.choice(questions)
    context.user_data['trivia_answer'] = a.lower()
    await update.message.reply_text(f"🧠 *Trivia:* {q}\n\nResponde con la respuesta!", parse_mode='Markdown')

async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("✊ Piedra", callback_data='rps_piedra'),
        InlineKeyboardButton("✋ Papel", callback_data='rps_papel'),
        InlineKeyboardButton("✌️ Tijera", callback_data='rps_tijera')
    ]]
    await update.message.reply_text(
        "🎮 *Piedra, Papel o Tijera*\n\n¡Elige!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def guess_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'secret' not in context.user_data:
        context.user_data['secret'] = random.randint(1, 100)
        await update.message.reply_text(
            "🎯 *Adivina el número*\n\n"
            "He pensado un número entre 1 y 100.\n"
            "Envía un número para adivinarlo!",
            parse_mode='Markdown'
        )
    else:
        context.user_data['secret'] = random.randint(1, 100)
        await update.message.reply_text("🎯 ¡Nuevo número! Adivina.")

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
        'text_tools': "📝 *Texto:* /echo, /reverse, /count, /uppercase, /lowercase, /capitalize, /binary, /base64, /md5, /palindrome",
        'math_tools': "🧮 *Matemáticas:* /calc, /sqrt, /power, /random, /dice, /coin, /prime, /fibonacci, /factorial",
        'games': "🎮 *Juegos:* /trivia, /riddle, /rps, /guess, /dice, /coin",
        'media': "🖼️ *Multimedia:* /cat, /dog, /quote, /fact, /joke, /meme, /advice",
        'utils': "🔧 *Utilidades:* /ip, /userinfo, /chatid, /password, /uuid, /lorem, /color, /bmi",
        'info_tools': "ℹ️ *Info:* /time, /date, /age, /weather"
    }
    
    if query.data in categories:
        await query.edit_message_text(
            f"{categories[query.data]}\n\n✨ *Escribe / para ver todos*",
            parse_mode='Markdown'
        )
    elif query.data == 'menu':
        keyboard = [
            [InlineKeyboardButton("📝 Texto", callback_data='text_tools'),
             InlineKeyboardButton("🧮 Matemáticas", callback_data='math_tools')],
            [InlineKeyboardButton("🎮 Juegos", callback_data='games'),
             InlineKeyboardButton("🖼️ Multimedia", callback_data='media')],
            [InlineKeyboardButton("🔧 Utilidades", callback_data='utils'),
             InlineKeyboardButton("📊 Info", callback_data='info_tools')],
        ]
        await query.edit_message_text(
            "📋 *Categorías:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# --- Manejo de respuestas de juegos ---
async def handle_trivia_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'trivia_answer' in context.user_data:
        answer = update.message.text.lower().strip()
        correct = context.user_data['trivia_answer']
        if answer == correct:
            await update.message.reply_text("✅ *¡Correcto!*", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ *Incorrecto. Era: {correct}*", parse_mode='Markdown')
        del context.user_data['trivia_answer']

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'secret' in context.user_data:
        try:
            guess = int(update.message.text)
            secret = context.user_data['secret']
            if guess < secret:
                await update.message.reply_text("📈 ¡Más alto!")
            elif guess > secret:
                await update.message.reply_text("📉 ¡Más bajo!")
            else:
                await update.message.reply_text("🎉 *¡Correcto! ¡Ganaste!* 🎉", parse_mode='Markdown')
                del context.user_data['secret']
        except ValueError:
            pass

# --- MAIN ---
async def post_init(app):
    await register_commands(app)

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Comandos básicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("menu", menu))
    
    # Texto
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("reverse", reverse_text))
    app.add_handler(CommandHandler("count", count_text))
    app.add_handler(CommandHandler("uppercase", uppercase))
    app.add_handler(CommandHandler("lowercase", lowercase))
    app.add_handler(CommandHandler("capitalize", capitalize_text))
    app.add_handler(CommandHandler("binary", to_binary))
    app.add_handler(CommandHandler("base64", base64_encode))
    app.add_handler(CommandHandler("md5", md5_hash))
    app.add_handler(CommandHandler("palindrome", palindrome))
    
    # Matemáticas
    app.add_handler(CommandHandler("calc", calculator))
    app.add_handler(CommandHandler("sqrt", sqrt_calc))
    app.add_handler(CommandHandler("power", power_calc))
    app.add_handler(CommandHandler("random", random_number))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("coin", coin))
    app.add_handler(CommandHandler("prime", prime_check))
    app.add_handler(CommandHandler("fibonacci", fibonacci_seq))
    app.add_handler(CommandHandler("factorial", factorial_calc))
    
    # Fecha/Hora
    app.add_handler(CommandHandler("time", time_cmd))
    app.add_handler(CommandHandler("date", date_cmd))
    app.add_handler(CommandHandler("calendar", calendar_cmd))
    app.add_handler(CommandHandler("age", age_calc))
    
    # Multimedia
    app.add_handler(CommandHandler("cat", cat))
    app.add_handler(CommandHandler("dog", dog))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("fact", fact))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CommandHandler("advice", advice))
    
    # Utilidades
    app.add_handler(CommandHandler("ip", get_ip))
    app.add_handler(CommandHandler("userinfo", user_info))
    app.add_handler(CommandHandler("chatid", chat_id))
    app.add_handler(CommandHandler("password", password_gen))
    app.add_handler(CommandHandler("uuid", uuid_gen))
    app.add_handler(CommandHandler("lorem", lorem_gen))
    app.add_handler(CommandHandler("color", color_info))
    app.add_handler(CommandHandler("bmi", bmi_calc))
    
    # Juegos
    app.add_handler(CommandHandler("trivia", trivia))
    app.add_handler(CommandHandler("rps", rps_game))
    app.add_handler(CommandHandler("guess", guess_game))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Manejo de respuestas
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_trivia_answer))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guess))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    logger.info(f"🚀 Bot iniciado con {len(COMMANDS_LIST)} comandos")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
