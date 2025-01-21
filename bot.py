import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import WebAppInfo
import json
import os

# إعداد البوت
TOKEN = '7625980357:AAGEZoFutDtNdMsmXj2UnWLlhuoXF3l1-6o'
bot = telebot.TeleBot(TOKEN)

# قائمة معرفات المشرفين
ADMIN_IDS = [5039505670, 7134153280]  # ضع هنا معرفات المشرفين

# مسار ملف قاعدة البيانات
USER_DB_FILE = 'users.json'

# دالة للتحقق مما إذا كان المستخدم مشرفًا
def is_admin(user_id):
    return user_id in ADMIN_IDS

# دالة لإنشاء لوحة الأزرار السريعة
def create_markup(buttons):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for btn in buttons:
        markup.add(btn)
    return markup

# دالة لقراءة قاعدة بيانات المستخدمين
def read_user_db():
    if not os.path.exists(USER_DB_FILE):
        return []
    with open(USER_DB_FILE, 'r') as file:
        return json.load(file)

# دالة لكتابة قاعدة بيانات المستخدمين
def write_user_db(users):
    with open(USER_DB_FILE, 'w') as file:
        json.dump(users, file)

# دالة لتحديث قاعدة البيانات عند انضمام مستخدم جديد
def update_user_db(user_id):
    users = read_user_db()
    if user_id not in users:
        users.append(user_id)
        write_user_db(users)

# دالة لبدء البوت وإظهار الأزرار السريعة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    update_user_db(message.from_user.id)  # تحديث قاعدة البيانات
    # إعداد الأزرار السريعة الرئيسية
    buttons = [
        KeyboardButton("نشرة الطقس", web_app=WebAppInfo(url="https://www.arabiaweather.com/")),
        KeyboardButton("سعر الصرف الآن", web_app=WebAppInfo(url="https://sp-today.com/en/currency/us_dollar")),
        KeyboardButton("تواصل عبر الواتساب"),
        KeyboardButton("شحن الألعاب"),
        KeyboardButton("شحن التطبيقات"),
        KeyboardButton("حوالات رقمية"),
        KeyboardButton("دفع الفواتير")
    ]
    markup = create_markup(buttons)
    bot.send_message(
        message.chat.id,
        "مرحبًا بك في بوت الخدمات! اختر من القائمة أدناه\n"
        "للإعلان على البوت : التواصل على الرقم\n"
        "https://wa.me/963960078178",
        reply_markup=markup
    )

# دالة لمعالجة نصوص الأوامر للمشرفين
@bot.message_handler(commands=['announce'])
def announce(message):
    if is_admin(message.from_user.id):
        msg = bot.send_message(message.chat.id, "أدخل النص للإعلان:")
        bot.register_next_step_handler(msg, get_announcement_text)
    else:
        bot.send_message(message.chat.id, "عذرًا، هذا الأمر مخصص للمشرفين فقط.")

# دالة لاستلام نص الإعلان
def get_announcement_text(message):
    announcement_text = message.text
    msg = bot.send_message(message.chat.id, "أرسل الصورة (اختياريًا) أو اكتب /skip للتخطي:")
    bot.register_next_step_handler(msg, get_announcement_image, announcement_text)

# دالة لاستلام صورة الإعلان
def get_announcement_image(message, announcement_text):
    if message.content_type == 'photo':
        photo_id = message.photo[-1].file_id
        send_announcement_to_all(announcement_text, photo_id)
    else:
        send_announcement_to_all(announcement_text)

# دالة لإرسال الإعلان لجميع المستخدمين
def send_announcement_to_all(text, photo_id=None):
    user_ids = read_user_db()
    for user_id in user_ids:
        try:
            if photo_id:
                bot.send_photo(user_id, photo_id, caption=text)
            else:
                bot.send_message(user_id, text)
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

# دالة لمعالجة النصوص المدخلة
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "تواصل عبر الواتساب":
        url = "https://wa.me/963997270403"
        bot.send_message(message.chat.id, f"افتح الرابط للتواصل عبر الواتساب: {url}")

    elif message.text == "أخبار السويداء ٢٤":
        url = "https://www.facebook.com/Suwayda24/"
        bot.send_message(message.chat.id, f"افتح الرابط للوصول إلى الصفحة: {url}")

    elif message.text == "شحن الألعاب":
        buttons = [
            KeyboardButton("ببجي"),
            KeyboardButton("فري فاير"),
            KeyboardButton("رجوع")
        ]
        markup = create_markup(buttons)
        bot.send_message(message.chat.id, "اختر اللعبة التي تريد شحنها:", reply_markup=markup)
    
    elif message.text == "شحن التطبيقات":
        buttons = [
            KeyboardButton("بيجو"),
            KeyboardButton("سول شيل"),
            KeyboardButton("جوجل بلاي"),
            KeyboardButton("رجوع")
        ]
        markup = create_markup(buttons)
        bot.send_message(message.chat.id, "اختر التطبيق الذي تريد شحنه:", reply_markup=markup)

    elif message.text == "حوالات رقمية":
        bot.send_message(message.chat.id, "التواصل على الرقم\nhttps://wa.me/963960078178")

    elif message.text == "دفع الفواتير":
        buttons = [
            KeyboardButton("الكهرباء"),
            KeyboardButton("الهاتف والإنترنت"),
            KeyboardButton("أقساط جامعية"),
            KeyboardButton("رجوع")
        ]
        markup = create_markup(buttons)
        bot.send_message(message.chat.id, "اختر الفاتورة التي تريد دفعها:", reply_markup=markup)

    elif message.text == "رجوع":
        send_welcome(message)

    else:
        bot.send_message(message.chat.id, "عذرًا، لم أفهم الطلب. حاول مرة أخرى أو اختر من القائمة.")

# بدء البوت
bot.polling()
