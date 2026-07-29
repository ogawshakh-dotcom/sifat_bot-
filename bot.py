import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot status: OK"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
import telebot
from telebot import types

# ==========================================
# ⚙️ SOZLAMALAR
# ==========================================
TOKEN = "8865367397:AAHql5TbsmlPDBdWPkinjnIUrLr-rfiyVOQ"
ADMIN_ID = 6407236165

bot = telebot.TeleBot(TOKEN)

# Dynamic bo'limlar va ularning matnlari
custom_sections = {}

# Yangilangan doimiy aloqa matni
contact_info = (
    "📍Qarshi shahar\n"
    "      B.Sherqulov 2/2\n"
    "📌Mo’ljal:MEXANIZATOR bosh ko’chasida\n"
    "+998(93) 935-01-01\n"
    "⏰Ish tartibi 07:00 dan 00:00 gacha"
)

STORE_LOCATION_URL = "https://maps.app.goo.gl/fNSpqst86x8186g18"

user_data = {}

# Statistika uchun
stats = {
    "total": 0,
    "accepted": 0,
    "rejected": 0
}

def cancel_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("❌ Bekor qilish")
    return markup

def main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_apply = types.KeyboardButton("📝 Ariza topshirish")
    btn_phone = types.KeyboardButton("📞 Aloqa raqami")
    btn_location = types.KeyboardButton("📍 Do'kon lakatsiyasi")
    
    markup.add(btn_apply)
    markup.add(btn_phone, btn_location)
    
    # Qo'shilgan dinamik bo'lim tugmalari
    for section_name in custom_sections.keys():
        markup.add(types.KeyboardButton(section_name))
    
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("⚙️ Admin Panel"))
        
    return markup

# ==================== /START BUYRUG'I ====================
@bot.message_handler(commands=['start'])
def start(message):
    start_text = (
        "<b>Xush kelibsiz!</b> 👋\n\n"
        "Siz <b>«SIFAT SUPERMARKET»</b> ahil jamoasiga qo'shilish arafasidasiz! "
        "Biz bilan nafaqat daromad topasiz, balki o'z karyerangizni yangi bosqichga olib chiqasiz. 🚀\n\n"
        "🛒 <b>Bizda sizni nimalar kutmoqda?</b>\n"
        "• Ahil va do'stona jamoa\n"
        "• O'z vaqtida beriladigan maosh\n"
        "• Karyera o'sishi va qulay grafik\n\n"
        "👇 Pastdagi tugmalar orqali ariza topshirishingiz yoki ma'lumot olishingiz mumkin:"
    )
    bot.send_message(
        message.chat.id, 
        start_text, 
        parse_mode="HTML", 
        reply_markup=main_keyboard(message.from_user.id)
    )

@bot.message_handler(func=lambda m: m.text == "📞 Aloqa raqami")
def show_contact(message):
    bot.send_message(message.chat.id, contact_info)

@bot.message_handler(func=lambda m: m.text == "📍 Do'kon lakatsiyasi")
def send_store_location(message):
    markup = types.InlineKeyboardMarkup()
    btn_map = types.InlineKeyboardButton("🗺 Xaritada ko'rish (Google Maps)", url=STORE_LOCATION_URL)
    markup.add(btn_map)
    
    bot.send_message(
        message.chat.id, 
        "🏬 <b>SIFAT SUPERMARKET joylashgan manzil:</b>\n\nPastdagi tugmani bosing va xarita orqali yo'nalish oling 👇", 
        parse_mode="HTML",
        reply_markup=markup
    )

# Dynamic bo'limlar kontentini ko'rsatish
@bot.message_handler(func=lambda m: m.text in custom_sections)
def show_custom_section(message):
    text = custom_sections.get(message.text, "Ma'lumot topilmadi.")
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ==================== ANKETA BOSQICHLARI ====================

@bot.message_handler(func=lambda m: m.text == "📝 Ariza topshirish")
def start_anketa(message):
    user_data[message.chat.id] = {}
    msg = bot.send_message(
        message.chat.id, 
        "👤 Pasport bo'yicha familiyangizni kiriting\n(Masalan: Karimov):", 
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, get_lastname)

def check_cancel(message):
    if message.text == "❌ Bekor qilish":
        bot.send_message(message.chat.id, "❌ Anketa to'ldirish bekor qilindi.", reply_markup=main_keyboard(message.from_user.id))
        return True
    return False

def get_lastname(message):
    if check_cancel(message): return
    user_data[message.chat.id]['lastname'] = message.text
    msg = bot.send_message(message.chat.id, "👤 Pasport bo'yicha ismingizni kiriting\n(Masalan: Abdulaziz):", reply_markup=cancel_keyboard(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_firstname)

def get_firstname(message):
    if check_cancel(message): return
    user_data[message.chat.id]['firstname'] = message.text
    msg = bot.send_message(message.chat.id, "📅 Tug'ilgan sanangizni kiriting\n(misol: 18.03.1995):", reply_markup=cancel_keyboard(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_birthdate)

def get_birthdate(message):
    if check_cancel(message): return
    user_data[message.chat.id]['birthdate'] = message.text
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))
    markup.add("❌ Bekor qilish")
    
    msg = bot.send_message(message.chat.id, "📱 Telefon raqamingizni kiriting\n(Misol: +998XXXXXXXXX):", reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_phone)

def get_phone(message):
    if check_cancel(message): return
    if message.contact:
        user_data[message.chat.id]['phone'] = message.contact.phone_number
    else:
        user_data[message.chat.id]['phone'] = message.text

    msg = bot.send_message(
        message.chat.id, 
        "🏡 Yashash manzilingizni kiriting\n(tuman, ko'cha/mavze, uy, kvartira):", 
        reply_markup=cancel_keyboard(), 
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, get_address)

def get_address(message):
    if check_cancel(message): return
    user_data[message.chat.id]['address'] = message.text
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("👨 Erkak", "👩 Ayol")
    markup.add("❌ Bekor qilish")
    
    msg = bot.send_message(message.chat.id, "👨‍🦱/👩‍🦰 Jinsni tanlang:", reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_gender)

def get_gender(message):
    if check_cancel(message): return
    user_data[message.chat.id]['gender'] = message.text
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("👍 Ha", "👎 Yo'q")
    markup.add("❌ Bekor qilish")
    
    msg = bot.send_message(message.chat.id, "👨‍🎓 Hozirda o'quvchi yoki talabamisiz?", reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_student)

def get_student(message):
    if check_cancel(message): return
    user_data[message.chat.id]['student'] = message.text
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("⚡ 1 yildan kam", "⭐ 1 yildan 3 yilgacha", "🌟 3 yildan ko'p", "🚫 Tajribasi yo'q")
    markup.add("❌ Bekor qilish")
    
    msg = bot.send_message(message.chat.id, "💥 Ish tajribangiz qanday?", reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_experience)

# ISH TAJRIBASIDAN KEYIN SMENA SO'RALADI
def get_experience(message):
    if check_cancel(message): return
    user_data[message.chat.id]['experience'] = message.text
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("✅ 07:00-15:00", "✅ 15:00-00:00")
    markup.row("❌ Bekor qilish")
    
    msg = bot.send_message(
        message.chat.id, 
        "⏰ Qaysi smenada ishlay olasiz?", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, get_smena)

# YANGI SMENA BOSQICHI
def get_smena(message):
    if check_cancel(message): return
    user_data[message.chat.id]['smena'] = message.text

    msg = bot.send_message(
        message.chat.id, 
        "💡 Rasmingizni yuklang:\n(Nomzodni aniqlash uchun kerak)", 
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, get_photo)

def get_photo(message):
    if check_cancel(message): return
    
    if message.content_type == 'photo':
        user_data[message.chat.id]['photo'] = message.photo[-1].file_id
    else:
        user_data[message.chat.id]['photo'] = None

    d = user_data[message.chat.id]
    
    summary_text = (
        f"🔍 MA'LUMOTLARINGIZNI TEKSHIRING:\n\n"
        f"👤 F.I.SH: {d.get('lastname')} {d.get('firstname')}\n"
        f"📅 Tug'ilgan sana: {d.get('birthdate')}\n"
        f"📞 Tel: {d.get('phone')}\n"
        f"🏡 Manzil: {d.get('address')}\n"
        f"👨/👩 Jinsi: {d.get('gender')}\n"
        f"👨‍🎓 Talabami: {d.get('student')}\n"
        f"💥 Tajriba: {d.get('experience')}\n"
        f"⏰ Smena: {d.get('smena')}\n\n"
        f"Barcha ma'lumotlar to'g'rimi?"
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("✅ Ha, yuborilsin!", "🔄 Qaytadan to'ldirish")
    
    msg = bot.send_message(message.chat.id, summary_text, reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(msg, confirm_and_send)

def confirm_and_send(message):
    if message.text == "✅ Ha, yuborilsin!":
        applicant_id = message.chat.id
        data = user_data.get(applicant_id, {})
        photo_id = data.get('photo')

        stats["total"] += 1

        bot.send_message(
            applicant_id, 
            "🎉 Rahmat! Arizangiz SIFAT SUPERMARKET HR jamoasiga muvaffaqiyatli yuborildi.", 
            reply_markup=main_keyboard(applicant_id),
            parse_mode="Markdown"
        )
        
        username_val = f"@{message.from_user.username}" if message.from_user.username else "Yo'q"
        
        admin_text = (
            f"📥 YANGI ISHCHI ARIZASI (SIFAT SUPERMARKET)\n\n"
            f"👤 F.I.SH: {data.get('lastname', '')} {data.get('firstname', '')}\n"
            f"📅 Tug'ilgan sana: {data.get('birthdate', '')}\n"
            f"📞 Tel: {data.get('phone', '')}\n"
            f"🏡 Manzil: {data.get('address', '')}\n"
            f"👨/👩 Jinsi: {data.get('gender', '')}\n"
            f"👨‍🎓 Talabami: {data.get('student', '')}\n"
            f"💥 Tajriba: {data.get('experience', '')}\n"
            f"⏰ Smena: {data.get('smena', '')}\n"
            f"🔗 Profil: {username_val}\n"
            f"🆔 ID: {applicant_id}"
        )
        
        inline_markup = types.InlineKeyboardMarkup()
        btn_accept = types.InlineKeyboardButton("✅ Suhbatga chaqirish", callback_data=f"accept_{applicant_id}")
        btn_reject = types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{applicant_id}")
        inline_markup.add(btn_accept, btn_reject)
        
        if photo_id:
            bot.send_photo(ADMIN_ID, photo_id, caption=admin_text, parse_mode="Markdown", reply_markup=inline_markup)
        else:
            bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown", reply_markup=inline_markup)

    else:
        bot.send_message(message.chat.id, "🔄 Anketa bekor qilindi. Qaytadan boshlash uchun bosing:", reply_markup=main_keyboard(message.chat.id))

# Admin javobi va callback handling
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        user_id = call.data.split("_")[1]
        
        if call.data.startswith("accept"):
            stats["accepted"] += 1
            bot.send_message(
                user_id, 
                "🎉 Xushxabar! Arizangiz SIFAT SUPERMARKET HR bo'limi tomonidan ma'qullandi.\nSizni suhbatga taklif etamiz! Tez orada bog'lanamiz."
            )
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            bot.send_message(ADMIN_ID, f"🟢 ID: {user_id} nomzod suhbatga chaqirildi.")
            
        elif call.data.startswith("reject"):
            stats["rejected"] += 1
            bot.send_message(
                user_id, 
                "Afsuski, arizangiz hozircha qabul qilinmadi.\nSIFAT SUPERMARKET jamoasiga qiziqish bildirganingiz uchun rahmat!"
            )
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            bot.send_message(ADMIN_ID, f"🔴 ID: {user_id} nomzod rad etildi.")

# ==================== ADMIN PANEL ====================

@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel" and m.from_user.id == ADMIN_ID)
def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Yangi bo'lim qo'shish", "🗑 Bo'limni o'chirish")
    markup.add("✏️ Aloqa matnini o'zgartirish", "📊 Statistika")
    markup.add("🔙 Asosiy menyu")
    bot.send_message(message.chat.id, "🛠 SIFAT SUPERMARKET — Admin Panel", reply_markup=markup)

# Yangi bo'lim qo'shish
@bot.message_handler(func=lambda m: m.text == "➕ Yangi bo'lim qo'shish" and m.from_user.id == ADMIN_ID)
def add_section_start(message):
    msg = bot.send_message(message.chat.id, "📌 Yangi bo'lim nomini kiriting:\n(Masalan: ℹ️ Biz haqimizda)", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_section_title)

def process_section_title(message):
    section_title = message.text
    msg = bot.send_message(message.chat.id, f"📝 '{section_title}' bo'limi bosilganda ko'rinadigan matnni kiriting:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_section_content, section_title)

def process_section_content(message, section_title):
    section_content = message.text
    custom_sections[section_title] = section_content
    bot.send_message(message.chat.id, f"✅ '{section_title}' bo'limi muvaffaqiyatli qo'shildi!", parse_mode="Markdown", reply_markup=main_keyboard(message.from_user.id))

# Bo'limni o'chirish
@bot.message_handler(func=lambda m: m.text == "🗑 Bo'limni o'chirish" and m.from_user.id == ADMIN_ID)
def delete_section_start(message):
    if not custom_sections:
        bot.send_message(message.chat.id, "O'chirish uchun bo'lim mavjud emas.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for sec in custom_sections.keys():
        markup.add(sec)
    msg = bot.send_message(message.chat.id, "O'chirmoqchi bo'lgan bo'limingizni tanlang:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_section_delete)

def process_section_delete(message):
    sec_title = message.text
    if sec_title in custom_sections:
        del custom_sections[sec_title]
        bot.send_message(message.chat.id, f"🗑 '{sec_title}' bo'limi muvaffaqiyatli o'chirildi!", reply_markup=main_keyboard(message.from_user.id))
    else:
        bot.send_message(message.chat.id, "Bunday bo'lim topilmadi.", reply_markup=main_keyboard(message.from_user.id))

# Aloqa bo'limini tahrirlash
@bot.message_handler(func=lambda m: m.text == "✏️ Aloqa matnini o'zgartirish" and m.from_user.id == ADMIN_ID)
def edit_contact_start(message):
    msg = bot.send_message(
        message.chat.id, 
        f"Hozirgi aloqa matni:\n\n{contact_info}\n\nYangi aloqa matnini kiriting:"
    )
    bot.register_next_step_handler(msg, process_contact_edit)

def process_contact_edit(message):
    global contact_info
    contact_info = message.text
    bot.send_message(
        message.chat.id, 
        "✅ Aloqa ma'lumotlari muvaffaqiyatli yangilandi!", 
        reply_markup=main_keyboard(message.from_user.id)
    )

@bot.message_handler(func=lambda m: m.text == "📊 Statistika" and m.from_user.id == ADMIN_ID)
def show_stats(message):
    text = (
        f"📊 BOT STATISTIKASI:\n\n"
        f"📥 Jami kelgan arizalar: {stats['total']}\n"
        f"✅ Chaqirilganlar: {stats['accepted']}\n"
        f"❌ Rad etilganlar: {stats['rejected']}"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 Asosiy menyu")
def back_main(message):
    bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_keyboard(message.from_user.id))

if __name__ == '__main__':
    print("SIFAT SUPERMARKET HR Bot tayyor va ishlamoqda...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
    
