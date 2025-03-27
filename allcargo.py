import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, Filter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

TOKEN = "7995355432:AAGedPytKGfeXDVThQdJH6kx1pfLyJ7YjsQ"  # Bot tokeningizni almashtiring
ADMIN_CODE = "Q1w2e3r4+"
DATA_FILE = "bot_data.json"
CHANNEL_ID = "@crm_tekshiruv"

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

user_lang = {}
user_data = {}
users = set()
blocked_users = set()
daily_users = {}
admin_state = {}
logger = logging.getLogger(__name__)

# Ma’lumotlarni fayldan yuklash
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                users = set(data.get("users", []))
                blocked_users = set(data.get("blocked_users", []))
                daily_users_raw = data.get("daily_users", {})
                daily_users = {key: set(value) for key, value in daily_users_raw.items()}
                return users, blocked_users, daily_users
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error loading bot_data.json: {e}. Creating a new file.")
            os.remove(DATA_FILE)
    return set(), set(), {}

# Ma’lumotlarni faylga saqlash
def save_data(users, blocked_users, daily_users):
    daily_users_serializable = {key: list(value) for key, value in daily_users.items()}
    with open(DATA_FILE, "w") as f:
        json.dump({
            "users": list(users),
            "blocked_users": list(blocked_users),
            "daily_users": daily_users_serializable
        }, f, indent=4)

# Bot ishga tushganda ma’lumotlarni yuklash
users, blocked_users, daily_users = load_data()

translations = {
    "uz": {
        "lang_name": "🇺🇿 O'zbekcha",
        "start": "🌐 Iltimos, tilni tanlang:",
        "welcome": "Assalomu alaykum! 👋\n\nSiz PBS IMPEX kompaniyasining rasmiy Telegram botidasiz. 🌍\n\nBiz yuk tashish va logistika xizmatlarini Markaziy Osiyo hamda xalqaro yo‘nalishlarda taqdim etamiz. ✈️🚛🚢🚂\n\n📦 Buyurtma berish yoki xizmatlar bilan tanishish uchun quyidagi menyudan foydalaning. 👇",
        "menu": ["📦 Buyurtma berish", "📞 Operator", "🛠 Xizmatlar", "🌍 Tilni o‘zgartirish", "👨‍💼 Admin paneli"],
        "services": "🛠 Xizmatlar",
        "admin_menu": ["📊 Statistika", "📢 Post", "🏠 Bosh sahifa"],
        "order_text": "📋 Buyurtma uchun quyidagi ma'lumotlarni kiriting:",
        "questions": [
            "1️⃣ Ismingiz yoki kompaniya nomi?",
            "2️⃣ Telefon raqamingiz?",
            "3️⃣ Yuk nomi?",
            "4️⃣ Tashish usuli?",
            "5️⃣ TIF TN kodi?",
            "6️⃣ Yuk qaysi bojxona postiga keladi?",
            "7️⃣ Yuk jo‘natish manzili?",
            "8️⃣ Yukni qabul qilish manzili?",
            "9️⃣ Yuk og‘irligi (kg)?",
            "10️⃣ Yuk hajmi (kub)?"
        ],
        "transport_options": ["Avto", "Avia", "Temir yo‘l", "Dengiz", "Multimodal"],
        "customs_posts": ["Toshkent", "Andijon", "Farg‘ona", "Samarqand", "Boshqa"],
        "confirm": "✅ Tasdiqlash",
        "retry": "🔄 Qayta yozish",
        "home": "🏠 Bosh sahifa",
        "back": "🔙 Orqaga",
        "received": "✅ Buyurtmangiz qabul qilindi. Tez orada bog‘lanamiz!",
        "error_phone": "❌ Telefon raqami noto‘g‘ri! Faqat raqamlar kiritilishi kerak. Qaytadan kiriting:",
        "error_phone_length": "❌ Telefon raqami 9 yoki 12 ta raqamdan iborat bo‘lishi kerak! Qaytadan kiriting:",
        "error_no_digits": "❌ Bu maydonda raqamlar ishlatilmasligi kerak! Qaytadan kiriting:",
        "error_only_digits": "❌ Bu maydonda faqat raqamlar bo‘lishi kerak! Qaytadan kiriting:",
        "admin_code_prompt": "🔑 Admin paneliga kirish uchun kodni kiriting:",
        "admin_welcome": "👨‍💼 Admin paneliga xush kelibsiz! Quyidagi menyudan foydalaning:",
        "not_admin": "❌ Siz admin emassiz!",
        "stats": "📊 Statistika:\n1. Umumiy foydalanuvchilar soni: {total}\n2. Botni bloklaganlar soni: {blocked}\n3. Kunlik foydalanuvchilar soni: {daily}",
        "post_prompt": "📢 Post yozing (matn, rasm yoki video):",
        "post_confirm": "📢 Yuboriladigan post:\n\n{post}\n\nTasdiqlaysizmi?",
        "post_sent": "✅ Post {count} foydalanuvchiga yuborildi!"
    },
    "ru": {
        "lang_name": "🇷🇺 Русский",
        "start": "🌐 Пожалуйста, выберите язык:",
        "welcome": "Здравствуйте! 👋\n\nВы находитесь в официальном Telegram-боте компании PBS IMPEX. 🌍\n\nМы предоставляем услуги по перевозке и логистике в Центральной Азии и по всему миру. ✈️🚛🚢🚂\n\n📦 Для оформления заказа или получения информации воспользуйтесь меню ниже. 👇",
        "menu": ["📦 Сделать заказ", "📞 Оператор", "🛠 Услуги", "🌍 Сменить язык", "👨‍💼 Админ-панель"],
        "services": "🛠 Услуги",
        "admin_menu": ["📊 Статистика", "📢 Пост", "🏠 Главное меню"],
        "order_text": "📋 Пожалуйста, введите данные для заказа:",
        "questions": [
            "1️⃣ Ваше имя или название компании?",
            "2️⃣ Ваш номер телефона?",
            "3️⃣ Название груза?",
            "4️⃣ Способ доставки?",
            "5️⃣ Код ТН ВЭД?",
            "6️⃣ На какой таможенный пост прибудет груз?",
            "7️⃣ Адрес отправления?",
            "8️⃣ Адрес получения?",
            "9️⃣ Вес груза (кг)?",
            "10️⃣ Объем груза (м³)?"
        ],
        "transport_options": ["Авто", "Авиа", "Ж/д", "Морской", "Мультимодальный"],
        "customs_posts": ["Ташкент", "Андижан", "Фергана", "Самарканд", "Другое"],
        "confirm": "✅ Подтвердить",
        "retry": "🔄 Повторить ввод",
        "home": "🏠 Главное меню",
        "back": "🔙 Назад",
        "received": "✅ Ваш заказ принят. Мы скоро с вами свяжемся!",
        "error_phone": "❌ Номер телефона неверный! Вводите только цифры. Повторите ввод:",
        "error_phone_length": "❌ Номер телефона должен содержать 9 или 12 цифр! Повторите ввод:",
        "error_no_digits": "❌ В этом поле нельзя использовать цифры! Повторите ввод:",
        "error_only_digits": "❌ В этом поле должны быть только цифры! Повторите ввод:",
        "admin_code_prompt": "🔑 Введите код для входа в админ-панель:",
        "admin_welcome": "👨‍💼 Добро пожаловать в админ-панель! Используйте меню ниже:",
        "not_admin": "❌ Вы не администратор!",
        "stats": "📊 Статистика:\n1. Общее число пользователей: {total}\n2. Число заблокировавших бота: {blocked}\n3. Число пользователей за день: {daily}",
        "post_prompt": "📢 Напишите пост (текст, фото или видео):",
        "post_confirm": "📢 Пост для отправки:\n\n{post}\n\nПодтверждаете?",
        "post_sent": "✅ Пост отправлен {count} пользователям!"
    },
    "en": {
        "lang_name": "🇬🇧 English",
        "start": "🌐 Please select a language:",
        "welcome": "Hello! 👋\n\nYou are in the official Telegram bot of PBS IMPEX. 🌍\n\nWe provide freight and logistics services in Central Asia and internationally. ✈️🚛🚢🚂\n\n📦 To place an order or view services, use the menu below. 👇",
        "menu": ["📦 New Order", "📞 Contact Operator", "🛠 Services", "🌍 Change Language", "👨‍💼 Admin Panel"],
        "services": "🛠 Services",
        "admin_menu": ["📊 Statistics", "📢 Post", "🏠 Home"],
        "order_text": "📋 Please enter the order details:",
        "questions": [
            "1️⃣ Your name or company name?",
            "2️⃣ Your phone number?",
            "3️⃣ Cargo name?",
            "4️⃣ Shipping method?",
            "5️⃣ HS Code?",
            "6️⃣ Which customs post will receive the cargo?",
            "7️⃣ Pickup address?",
            "8️⃣ Delivery address?",
            "9️⃣ Cargo weight (kg)?",
            "10️⃣ Cargo volume (m³)?"
        ],
        "transport_options": ["Auto", "Air", "Rail", "Sea", "Multimodal"],
        "customs_posts": ["Tashkent", "Andijan", "Fergana", "Samarkand", "Other"],
        "confirm": "✅ Confirm",
        "retry": "🔄 Rewrite",
        "home": "🏠 Home",
        "back": "🔙 Back",
        "received": "✅ Your order has been received. We will contact you soon!",
        "error_phone": "❌ Invalid phone number! Only digits are allowed. Please try again:",
        "error_phone_length": "❌ Phone number must be 9 or 12 digits long! Please try again:",
        "error_no_digits": "❌ Digits are not allowed in this field! Please try again:",
        "error_only_digits": "❌ Only digits are allowed in this field! Please try again:",
        "admin_code_prompt": "🔑 Enter the code to access the Admin Panel:",
        "admin_welcome": "👨‍💼 Welcome to the Admin Panel! Use the menu below:",
        "not_admin": "❌ You are not an admin!",
        "stats": "📊 Statistics:\n1. Total users: {total}\n2. Users who blocked the bot: {blocked}\n3. Daily users: {daily}",
        "post_prompt": "📢 Write a post (text, photo, or video):",
        "post_confirm": "📢 Post to send:\n\n{post}\n\nConfirm?",
        "post_sent": "✅ Post sent to {count} users!"
    }
}

# Klaviaturalar
def get_language_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=translations[lang]["lang_name"]) for lang in translations]],
        resize_keyboard=True
    )

def get_main_menu(lang):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn)] for btn in translations[lang]["menu"]], resize_keyboard=True
    )

def get_order_nav(lang):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=translations[lang]["back"]), KeyboardButton(text=translations[lang]["home"])]], resize_keyboard=True
    )

def get_admin_menu(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=translations[lang]["admin_menu"][0])],
            [KeyboardButton(text=translations[lang]["admin_menu"][1])],
            [KeyboardButton(text=translations[lang]["admin_menu"][2])],
            [KeyboardButton(text=translations[lang]["back"])]
        ],
        resize_keyboard=True
    )

def get_transport_buttons(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=opt, callback_data=f"transport:{opt}")] for opt in translations[lang]["transport_options"]]
    )

def get_customs_post_buttons(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=opt, callback_data=f"customs:{opt}")] for opt in translations[lang]["customs_posts"]]
    )

@dp.callback_query(F.data.startswith("customs:"))
async def handle_customs_post_choice(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = user_lang.get(user_id, "uz")
    customs_post = callback.data.split(":")[1]
    question = translations[lang]["questions"][5]  # 6-savol
    user_data[user_id]["answers"][question] = customs_post
    user_data[user_id]["step"] += 1
    await callback.message.delete()
    await ask_question(user_id)

def get_confirm_buttons(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=translations[lang]["confirm"], callback_data="confirm_order"),
            InlineKeyboardButton(text=translations[lang]["retry"], callback_data="retry_order")
        ]]
    )

def get_post_confirm_buttons(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=translations[lang]["confirm"], callback_data="confirm_post"),
            InlineKeyboardButton(text=translations[lang]["retry"], callback_data="retry_post")
        ]]
    )

def get_services_menu(lang):
    services_menu = {
        "uz": [
            [KeyboardButton(text="🚛 Logistika")],
            [KeyboardButton(text="🧾 Ruxsatnomalar va bojxona xizmatlari")],
            [KeyboardButton(text="🏢 Ma’muriyatchilik ishlari")],
            [KeyboardButton(text="📄 Sertifikatsiya")],
            [KeyboardButton(text=translations[lang]["home"])]
        ],
        "ru": [
            [KeyboardButton(text="🚛 Логистика")],
            [KeyboardButton(text="🧾 Разрешения и таможенные услуги")],
            [KeyboardButton(text="🏢 Административные услуги")],
            [KeyboardButton(text="📄 Сертификация")],
            [KeyboardButton(text=translations[lang]["home"])]
        ],
        "en": [
            [KeyboardButton(text="🚛 Logistics")],
            [KeyboardButton(text="🧾 Permits and Customs Services")],
            [KeyboardButton(text="🏢 Administrative Services")],
            [KeyboardButton(text="📄 Certification")],
            [KeyboardButton(text=translations[lang]["home"])]
        ]
    }
    return ReplyKeyboardMarkup(keyboard=services_menu[lang], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    today = datetime.now().date().isoformat()

    users.add(user_id)
    if today not in daily_users:
        daily_users[today] = set()
    daily_users[today].add(user_id)
    save_data(users, blocked_users, daily_users)

    logger.info(f"Foydalanuvchi {user_id} botni boshladi. Umumiy foydalanuvchilar: {len(users)}, Kunlik: {len(daily_users[today])}")
    await message.answer(translations["uz"]["start"], reply_markup=get_language_menu())

# Admin post filtiri
class IsAwaitingPost(Filter):
    async def __call__(self, message: types.Message) -> bool:
        user_id = message.from_user.id
        return admin_state.get(user_id, {}).get("awaiting_post", False)

@dp.message(IsAwaitingPost(), F.text)
async def handle_admin_post_text(message: types.Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "uz")
    logger.info(f"Admin post yozmoqda: {message.text}")

    if message.text == translations[lang]["back"]:
        admin_state[user_id] = {"in_admin": True}
        await message.answer(translations[lang]["admin_welcome"], reply_markup=get_admin_menu(lang))
    else:
        admin_state[user_id]["post_content"]["text"] = message.text
        logger.info(f"Post mazmuni yangilandi: {admin_state[user_id]['post_content']}")
        await show_post_preview(user_id, message)

# Til tanlash va dastlabki savollar
async def ask_initial_question(user_id):
    lang = user_lang.get(user_id, "uz")
    step = user_data[user_id]["initial_step"]
    initial_questions = [
        "Ismingiz yoki familiyangiz?",
        "Telefon raqamingiz?"
    ]
    if lang == "ru":
        initial_questions = ["Ваше имя или фамилия?", "Ваш номер телефона?"]
    elif lang == "en":
        initial_questions = ["Your name or surname?", "Your phone number?"]

    if step < len(initial_questions):
        await bot.send_message(user_id, initial_questions[step], reply_markup=get_order_nav(lang))
    else:
        await bot.send_message(user_id, translations[lang]["welcome"], reply_markup=get_main_menu(lang))
        user_data.pop(user_id)

async def handle_initial_answer(message: types.Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "uz")
    text = message.text

    if text == translations[lang]["back"]:
        if user_data[user_id]["initial_step"] > 0:
            user_data[user_id]["initial_step"] -= 1
            await ask_initial_question(user_id)
        else:
            user_data.pop(user_id, None)
            await message.answer(translations[lang]["start"], reply_markup=get_language_menu())
        return

    if text == translations[lang]["home"]:
        user_data.pop(user_id, None)
        await message.answer(translations[lang]["welcome"], reply_markup=get_main_menu(lang))
        return

    step = user_data[user_id]["initial_step"]
    initial_questions = ["Ismingiz yoki familiyangiz?", "Telefon raqamingiz?"] if lang == "uz" else \
                       ["Ваше имя или фамилия?", "Ваш номер телефона?"] if lang == "ru" else \
                       ["Your name or surname?", "Your phone number?"]

    if step == 1:  # Telefon raqami
        cleaned_text = text.replace("+", "").replace(" ", "")
        if not cleaned_text.isdigit():
            await message.answer(translations[lang]["error_phone"])
            return
        if len(cleaned_text) not in [9, 12]:
            await message.answer(translations[lang]["error_phone_length"])
            return

    user_data[user_id]["initial_answers"][initial_questions[step]] = text
    user_data[user_id]["initial_step"] += 1
    await ask_initial_question(user_id)

@dp.message(F.text)
async def handle_language_and_menu(message: types.Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "uz")
    logger.info(f"Foydalanuvchi {user_id} yubordi: {message.text}")

    # Har qanday muloqotda foydalanuvchini bugungi faollar ro‘yxatiga qo‘shish
    today = datetime.now().date().isoformat()
    if today not in daily_users:
        daily_users[today] = set()
    daily_users[today].add(user_id)
    save_data(users, blocked_users, daily_users)

    if admin_state.get(user_id, {}).get("awaiting_post", False):
        return

    # Til tanlash
    for lang_code, data in translations.items():
        if message.text == data["lang_name"]:
            user_lang[user_id] = lang_code
            user_data[user_id] = {"initial_step": 0, "initial_answers": {}}
            await message.answer("Iltimos, ma'lumotlarni kiriting:", reply_markup=get_order_nav(lang_code))
            await ask_initial_question(user_id)
            return

    # Dastlabki savollar
    if user_id in user_data and "initial_step" in user_data[user_id]:
        await handle_initial_answer(message)
        return

    # Asosiy menyu logikasi
    if message.text == translations[lang]["menu"][3]:
        await message.answer(translations[lang]["start"], reply_markup=get_language_menu())
        return

    if message.text == translations[lang]["home"]:
        admin_state.pop(user_id, None)
        user_data.pop(user_id, None)
        await message.answer(translations[lang]["welcome"], reply_markup=get_main_menu(lang))
        return

    if message.text == translations[lang]["menu"][0]:
        user_data[user_id] = {"step": 0, "answers": {}}
        await message.answer(translations[lang]["order_text"], reply_markup=get_order_nav(lang))
        await ask_question(user_id)
        return

    elif message.text == translations[lang]["menu"][1]:
        operator_info_translations = {
            "uz": """<b>«PBS IMPEX» XK</b>
🏢 Manzil: Toshkent shahri, Nukus ko’chasi, 3 uy
📞 Telefon: +99871 2155638
👨‍💼 Sale menedjer: Mohirjon Rustamov
📱 +99891 166-75-36
✉️ E-mail: office@pbs-impex.uz
🌐 Web: https://pbs-impex.uz/""",
            "ru": """<b>«PBS IMPEX» ЧП</b>
🏢 Адрес: г. Ташкент, улица Нукус, дом 3
📞 Телефон: +99871 2155638
👨‍💼 Менеджер по продажам: Мохиржон Рустамов
📱 +99891 166-75-36
✉️ E-mail: office@pbs-impex.uz
🌐 Сайт: https://pbs-impex.uz/""",
            "en": """<b>«PBS IMPEX» LLC</b>
🏢 Address: Nukus street 3, Tashkent
📞 Phone: +99871 2155638
👨‍💼 Sales Manager: Mohirjon Rustamov
📱 +99891 166-75-36
✉️ E-mail: office@pbs-impex.uz
🌐 Website: https://pbs-impex.uz/"""
        }
        await message.answer(operator_info_translations[lang], reply_markup=get_main_menu(lang), parse_mode="HTML")
        return

    elif message.text == translations[lang]["menu"][2]:
        await message.answer(translations[lang]["services"], reply_markup=get_services_menu(lang))
        return

    elif message.text == translations[lang]["menu"][4]:
        admin_state[user_id] = {"awaiting_code": True}
        await message.answer(translations[lang]["admin_code_prompt"], reply_markup=get_order_nav(lang))
        return

    elif user_id in admin_state and admin_state[user_id].get("awaiting_code"):
        if message.text == ADMIN_CODE:
            admin_state[user_id] = {"in_admin": True}
            await message.answer(translations[lang]["admin_welcome"], reply_markup=get_admin_menu(lang))
        else:
            admin_state.pop(user_id, None)
            await message.answer(translations[lang]["not_admin"], reply_markup=get_main_menu(lang))
        return

    elif user_id in admin_state and admin_state[user_id].get("in_admin"):
        if message.text == translations[lang]["admin_menu"][0]:
            today = datetime.now().date().isoformat()
            stats_text = translations[lang]["stats"].format(
                total=len(users),
                blocked=len(blocked_users),
                daily=len(daily_users.get(today, set()))
            )
            await message.answer(stats_text, reply_markup=get_admin_menu(lang))
        elif message.text == translations[lang]["admin_menu"][1]:  # 455-qator shu yerda bo‘lishi kerak
            admin_state[user_id] = {
                "in_admin": True,
                "awaiting_post": True,
                "post_content": {"text": None, "photo": None, "video": None}
            }
            await message.answer(translations[lang]["post_prompt"], reply_markup=get_order_nav(lang))
        elif message.text == translations[lang]["admin_menu"][2]:
            admin_state.pop(user_id, None)
            await message.answer(translations[lang]["welcome"], reply_markup=get_main_menu(lang))
        elif message.text == translations[lang]["back"]:
            admin_state[user_id] = {"in_admin": True}
            await message.answer(translations[lang]["admin_welcome"], reply_markup=get_admin_menu(lang))
        return

    # Qolgan logika o‘zgarmaydi
    # ...

    elif message.text in ["🚛 Logistika", "🚛 Логистика", "🚛 Logistics"]:
        logistics_text = {
            "uz": """✅ <b>Logistika xizmati</b>
• Malakali maslahat berish
• Transport vositalarining qulay kombinatsiyasi (avia, avto, temir yo‘l, suv) asosida optimal yo‘nalish ishlab chiqish
• Xarajatlarni hisoblash
• Kerakli hujjatlarni rasmiylashtirish
• Sug‘urta shartlarini qulaylashtirish
• Yuk tashish bosqichlari bo‘yicha hisobot berish
• Hilma-hil mamlakatlardan kelgan yuklarni reeksport mamlakatida to‘plash
• \"Eshikdan eshikgacha\" xizmati
• Toshkent va O‘zbekiston bo‘ylab shaxsiy transportda yuk tashish (5 tonna/20 kub; 1.5 tonna/14 kub)
• Texnik Iqtisodiy Asos shartlariga asosan yuk tashishni tashkil etish""",
            "ru": """✅ <b>Логистические услуги</b>
• Консультации от специалистов
• Оптимальный маршрут с учетом различных видов транспорта (авиа, авто, жд, морской)
• Расчет затрат
• Оформление всех необходимых документов
• Упрощение условий страхования
• Отчетность по каждому этапу перевозки
• Консолидация грузов из разных стран в стране реэкспорта
• Услуга \"от двери до двери\"
• Перевозки по Ташкенту и всей Узбекистану (5 тонн/20 куб; 1.5 тонн/14 куб)
• Организация перевозок на основе ТЭО""",
            "en": """✅ <b>Logistics Service</b>
• Professional consulting
• Optimal route planning using air, road, rail, and sea transport
• Cost calculation
• Document processing
• Simplified insurance terms
• Reporting for each transport stage
• Consolidation of goods from different countries in re-export country
• Door-to-door service
• Local transport across Tashkent and Uzbekistan (5 ton/20 m³; 1.5 ton/14 m³)
• Full logistics based on feasibility studies"""
        }
        await message.answer(logistics_text[lang], parse_mode="HTML", reply_markup=get_order_nav(lang))
        return

    elif message.text in ["🧾 Ruxsatnomalar va bojxona xizmatlari", "🧾 Разрешения и таможенные услуги", "🧾 Permits and Customs Services"]:
        customs_text = {
            "uz": """✅ <b>Ruxsatnomalar va bojxona xizmatlari</b>
• Tashqi savdo shartnomalarini tuzishda maslahat va ularni ro‘yxatdan o‘tkazish
• TIF TN kodi asosida ekspert xulosasi va bojxona moslashtirish
• Import/eksportdagi xarajatlar bo‘yicha ma’lumot
• Yuk hujjatlarini olish, raskreditovka qilish, bojxonada ro‘yxatga olish
• Bojxona xizmatlarini bojxona skladigacha yoki kerakli manzilgacha yetkazish
• Skladga qo‘yish va nazorat qilish
• Bojxona deklaratsiyasini tayyorlash""",
            "ru": """✅ <b>Разрешения и таможенные услуги</b>
• Консультации по внешнеторговым контрактам и их регистрация
• Экспертное заключение по ТН ВЭД и согласование с таможней
• Информация по затратам на импорт/экспорт
• Получение документов, раскредитовка, регистрация, сопровождение
• Таможенные услуги до склада или по нужному адресу
• Хранение и контроль на складе
• Подготовка таможенной декларации""",
            "en": """✅ <b>Permits and Customs Services</b>
• Consulting on foreign trade contracts and registration
• Expert opinion based on HS Code and customs approval
• Info on import/export costs
• Document handling, clearance, customs registration
• Customs service delivery to warehouse or specified address
• Storage and monitoring
• Preparation of customs declaration"""
        }
        await message.answer(customs_text[lang], parse_mode="HTML", reply_markup=get_order_nav(lang))
        return

    elif message.text in ["🏢 Ma’muriyatchilik ishlari", "🏢 Административные услуги", "🏢 Administrative Services"]:
        admin_text = {
            "uz": """✅ <b>Ma’muriyatchilik ishlari</b>
• Mijozlarimiz tovariga buyurtma va talabnomalarni joylashtirish
• Tovarni sotib olish shartnomalarini muvofiqlashtirish
• Yetkazib berish muddati, narxi va xarakteristikasini moslashtirish
• Tovar va transport hujjatlarini muvofiqlashtirish
• Invoyslarni olish va tekshirish
• \"Back orders\" holatini nazorat qilish
• Buyurtmalarni yig‘ish va jo‘natish""",
            "ru": """✅ <b>Административные услуги</b>
• Размещение заказов и заявок на товары клиентов
• Согласование контрактов на закупку
• Согласование сроков, цены и характеристик поставки
• Согласование товарных и транспортных документов
• Получение и проверка инвойсов
• Контроль \"Back orders\"
• Сбор и отправка заказов""",
            "en": """✅ <b>Administrative Services</b>
• Placing orders and requests for client goods
• Coordinating purchase contracts
• Adjusting delivery time, price, and specifications
• Coordinating goods and transport documents
• Receiving and verifying invoices
• Controlling \"Back orders\"
• Collecting and dispatching orders"""
        }
        await message.answer(admin_text[lang], parse_mode="HTML", reply_markup=get_order_nav(lang))
        return

    elif message.text in ["📄 Sertifikatsiya", "📄 Сертификация", "📄 Certification"]:
        cert_text = {
            "uz": """✅ <b>Sertifikatsiya</b>
• Tovar uchun har xil sertifikatlarni olish (kerak bo‘lganda)
• Akkreditatsiyaga ega laboratoriyalardan sinov protokollarini va xulosalarni olish
• Yukni olib kirish yoki olib chiqish uchun kerakli ruxsat xatlarini olish
• O‘lchash vositalarini metrologik attestatsiyadan o‘tkazish
• Tovarning soni va sifati uchun ekspertiza va inspeksiya
• Sertifikatsiya uchun namunalarni tanlab olishni tashkillashtirish""",
            "ru": """✅ <b>Сертификация</b>
• Получение различных сертификатов для товаров (при необходимости)
• Получение протоколов испытаний и заключений из аккредитованных лабораторий
• Получение разрешений на ввоз или вывоз груза
• Метрологическая аттестация измерительных средств
• Экспертиза и инспекция количества и качества товара
• Организация отбора образцов для сертификации""",
            "en": """✅ <b>Certification</b>
• Obtaining various product certificates (if needed)
• Getting test reports and conclusions from accredited laboratories
• Obtaining permits for cargo import or export
• Metrological certification of measuring instruments
• Product quantity and quality inspection
• Organizing sample selection for certification"""
        }
        await message.answer(cert_text[lang], parse_mode="HTML", reply_markup=get_order_nav(lang))
        return

    if user_id in user_data:
        await handle_order_answer(message)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "uz")
    if user_id in admin_state and admin_state[user_id].get("awaiting_post"):
        admin_state[user_id]["post_content"]["photo"] = message.photo[-1].file_id
        logger.info(f"Rasm qo‘shildi: {admin_state[user_id]['post_content']['photo']}")
        await show_post_preview(user_id, message)
    else:
        await message.answer(translations[lang]["welcome"], reply_markup=get_main_menu(lang))

@dp.message(F.video)
async def handle_video(message: types.Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "uz")
    if user_id in admin_state and admin_state[user_id].get("awaiting_post"):
        admin_state[user_id]["post_content"]["video"] = message.video.file_id
        logger.info(f"Video qo‘shildi: {admin_state[user_id]['post_content']['video']}")
        await show_post_preview(user_id, message)
    else:
        await message.answer(translations[lang]["welcome"], reply_markup=get_main_menu(lang))

async def handle_order_answer(message: types.Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "uz")
    if user_id not in user_data or "step" not in user_data[user_id]:
        return

    text = message.text
    if text == translations[lang]["back"]:
        if user_data[user_id]["step"] > 0:
            user_data[user_id]["step"] -= 1
            await ask_question(user_id)
        else:
            user_data.pop(user_id, None)
            await message.answer(translations[lang]["welcome"], reply_markup=get_main_menu(lang))
        return

    if text == translations[lang]["home"]:
        user_data.pop(user_id, None)
        await message.answer(translations[lang]["welcome"], reply_markup=get_main_menu(lang))
        return

    step = user_data[user_id]["step"]
    if step != 3 and step < len(translations[lang]["questions"]):  # Faqat 3-savol (Tashish usuli) inline
        question = translations[lang]["questions"][step]

        if step == 1:  # Telefon raqami
            cleaned_text = text.replace("+", "").replace(" ", "")
            if not cleaned_text.isdigit():
                await message.answer(translations[lang]["error_phone"])
                return
            if len(cleaned_text) not in [9, 12]:
                await message.answer(translations[lang]["error_phone_length"])
                return

        elif step in [4, 8, 9]:  # TIF TN kodi, Yuk og‘irligi, Yuk hajmi
            if step in [8, 9]:  # Og‘irlik va hajmda nuqta ruxsat etiladi
                if not text.replace(".", "").isdigit():
                    await message.answer(translations[lang]["error_only_digits"])
                    return
            elif step == 4:  # TIF TN kodi faqat raqam
                if not text.isdigit():
                    await message.answer(translations[lang]["error_only_digits"])
                    return

        elif step in [2, 6, 7]:  # Yuk nomi, Yuk jo‘natish manzili, Yuk qabul qilish manzili
            if any(char.isdigit() for char in text):
                await message.answer(translations[lang]["error_no_digits"])
                return

        user_data[user_id]["answers"][question] = text
        user_data[user_id]["step"] += 1
        await ask_question(user_id)

async def ask_question(user_id):
    lang = user_lang.get(user_id, "uz")
    step = user_data[user_id]["step"]
    if step == 3:  # Tashish usuli
        await bot.send_message(user_id, translations[lang]["questions"][step], reply_markup=get_transport_buttons(lang))
    elif step < len(translations[lang]["questions"]):
        await bot.send_message(user_id, translations[lang]["questions"][step], reply_markup=get_order_nav(lang))
    else:
        await show_summary(user_id)

async def show_summary(user_id):
    lang = user_lang.get(user_id, "uz")
    summary = f"📋 {translations[lang]['order_text']}\n\n"
    for q, a in user_data[user_id]["answers"].items():
        summary += f"🔹 {q}: {a}\n"
    await bot.send_message(user_id, summary, reply_markup=get_confirm_buttons(lang))

async def show_post_preview(user_id, message: types.Message):
    lang = user_lang.get(user_id, "uz")
    post_content = admin_state[user_id]["post_content"]
    preview_text = translations[lang]["post_confirm"].format(post=post_content["text"] or "Matn yo‘q")

    try:
        if post_content["photo"]:
            await bot.send_photo(user_id, post_content["photo"], caption=post_content["text"] or "", reply_markup=get_post_confirm_buttons(lang))
        elif post_content["video"]:
            await bot.send_video(user_id, post_content["video"], caption=post_content["text"] or "", reply_markup=get_post_confirm_buttons(lang))
        elif post_content["text"]:
            await bot.send_message(user_id, preview_text, reply_markup=get_post_confirm_buttons(lang))
        else:
            await bot.send_message(user_id, "❌ Hech qanday kontent kiritilmadi!", reply_markup=get_order_nav(lang))
    except Exception as e:
        logger.error(f"Post oldindan ko‘rishda xatolik: {e}")
        await bot.send_message(user_id, "❌ Xatolik yuz berdi!", reply_markup=get_order_nav(lang))

@dp.callback_query(F.data.startswith("transport:"))
async def handle_transport_choice(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = user_lang.get(user_id, "uz")
    transport = callback.data.split(":")[1]
    question = translations[lang]["questions"][3]
    user_data[user_id]["answers"][question] = transport
    user_data[user_id]["step"] += 1
    await callback.message.delete()
    await ask_question(user_id)

@dp.callback_query(F.data == "retry_order")
async def retry_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = user_lang.get(user_id, "uz")
    user_data[user_id] = {"step": 0, "answers": {}}
    await callback.message.delete()
    await bot.send_message(user_id, translations[lang]["order_text"], reply_markup=get_order_nav(lang))
    await ask_question(user_id)

@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = user_lang.get(user_id, "uz")

    logger.info(f"Buyurtma tasdiqlash boshlandi: Foydalanuvchi ID {user_id}")

    if user_id not in user_data or "answers" not in user_data[user_id]:
        logger.warning(f"Foydalanuvchi ma'lumotlari topilmadi: {user_id}")
        await callback.message.delete()
        await callback.message.answer(translations[lang]["error"], reply_markup=get_main_menu(lang))
        return

    answers = user_data[user_id]["answers"]
    order_text = translations[lang]["received"] + "\n\n"
    for question, answer in answers.items():
        order_text += f"{question}: {answer}\n"

    await callback.message.delete()
    await callback.message.answer(order_text, reply_markup=get_main_menu(lang))

    logger.info(f"Kanalga xabar yuborishga urinish: CHANNEL_ID={CHANNEL_ID}")
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"🔔 Yangi Buyurtma!\n\nFoydalanuvchi ID: {user_id}\n{order_text}",
            parse_mode="HTML"
        )
        logger.info(f"Kanalga xabar muvaffaqiyatli yuborildi: Foydalanuvchi ID {user_id}")
    except Exception as e:
        logger.error(f"Kanalga xabar yuborishda xatolik: {e}")

    user_data.pop(user_id, None)
    logger.info(f"Buyurtma tasdiqlash tugadi: Foydalanuvchi ID {user_id}")

@dp.callback_query(F.data == "confirm_post")
async def confirm_post(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = user_lang.get(user_id, "uz")
    post_content = admin_state[user_id]["post_content"]
    sent_count = 0

    for uid in users:
        if uid not in blocked_users:
            try:
                if post_content["photo"]:
                    await bot.send_photo(uid, post_content["photo"], caption=post_content["text"] or "")
                elif post_content["video"]:
                    await bot.send_video(uid, post_content["video"], caption=post_content["text"] or "")
                elif post_content["text"]:
                    await bot.send_message(uid, post_content["text"])
                sent_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Post yuborishda xatolik: {e}")
                blocked_users.add(uid)
                save_data(users, blocked_users, daily_users)

    await callback.message.delete()
    await bot.send_message(user_id, translations[lang]["post_sent"].format(count=sent_count), reply_markup=get_admin_menu(lang))
    admin_state[user_id] = {"in_admin": True}

@dp.callback_query(F.data == "retry_post")
async def retry_post(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = user_lang.get(user_id, "uz")
    admin_state[user_id] = {
        "in_admin": True,
        "awaiting_post": True,
        "post_content": {"text": None, "photo": None, "video": None}
    }
    await callback.message.delete()
    await bot.send_message(user_id, translations[lang]["post_prompt"], reply_markup=get_order_nav(lang))

async def reset_daily_users():
    while True:
        now = datetime.now()
        next_midnight = (now.replace(hour=23, minute=59, second=59, microsecond=999999) + timedelta(seconds=1))
        await asyncio.sleep((next_midnight - now).total_seconds())
        today = datetime.now().date().isoformat()
        daily_users[today] = set()  # Yangi kun uchun bo‘sh ro‘yxat
        save_data(users, blocked_users, daily_users)
        logger.info(f"Kunlik foydalanuvchilar {today} uchun yangilandi.")

# Yangilangan `main` funksiyasi (777-779-qatorlar o‘rniga)
async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(reset_daily_users())  # Har kuni 00:00 da yangilash
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())