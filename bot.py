import telebot
from telebot import types
import json
import os
from datetime import datetime

# Bot tokenini environment variable dan olish (xavfsizlik uchun)
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8408382660:AAGNIEyASvHfQvEZ4Aera3fKTDEgSDXZsHU")
ADMIN_IDS = [1077804816, 1336425233]  # Admin ID larini kiriting

bot = telebot.TeleBot(BOT_TOKEN)

# Foydalanuvchi ma'lumotlarini saqlash uchun
user_data = {}
pending_requests = {}
approved_requests = {}  # Added to track approved requests

def is_admin(user_id):
    return user_id in ADMIN_IDS

# Ma'lumotlarni faylga saqlash
def save_data():
    data_dir = '/app/data' if os.path.exists('/app/data') else '.'
    file_path = os.path.join(data_dir, 'user_data.json')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'user_data': user_data,
            'approved_requests': approved_requests
        }, f, ensure_ascii=False, indent=2)

def load_data():
    global user_data, approved_requests
    try:
        data_dir = '/app/data' if os.path.exists('/app/data') else '.'
        file_path = os.path.join(data_dir, 'user_data.json')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            user_data = data.get('user_data', {})
            approved_requests = data.get('approved_requests', {})
    except FileNotFoundError:
        user_data = {}
        approved_requests = {}

def show_terms_agreement(message):
    terms_text = (
        "📋 Foydalanish shartlari:\n\n"
        "Sizga taqdim etilgan login parol orqali siz internet tarmog'idan cheksiz foydalanishingiz mumkun, "
        "lekin sizga asosiy cheklov sifatida taqiqlangan ma'lumotlarni tarqatish, keraksiz manbalardan foydalanish, "
        "noqonuniy saytlarga kirish taqiqlanadi.\n\n"
        "Agar sizda shubhali harakat sezsak sizning ma'lumotlaringizni biz IIBga topshirishga majbur bo'lamiz "
        "bu qonun buzilishi hisoblanib sizga qonuniy chora ko'rishga olib keladi.\n\n"
        "Siz shuni inobatga olib rozilik berib davom etishingiz yoki bekor qilishingiz mumkun."
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_agree = types.InlineKeyboardButton("✅ Roziman", callback_data="agree_terms")
    btn_cancel = types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_terms")
    markup.add(btn_agree, btn_cancel)
    
    bot.send_message(message.chat.id, terms_text, reply_markup=markup)

def show_admin_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("👥 Foydalanuvchilar ro'yxati")
    btn2 = types.KeyboardButton("📊 Statistika")
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id,
        "Admin paneli:",
        reply_markup=markup
    )

def show_user_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("🔐 Login parol olish")
    btn2 = types.KeyboardButton("🔄 Login parol tiklash")
    btn3 = types.KeyboardButton("📖 Foydalanish yo'riqnomasi")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(
        message.chat.id,
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=markup
    )

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = str(message.from_user.id)
    
    if is_admin(message.from_user.id):
        bot.send_message(
            message.chat.id,
            f"Salom Admin {message.from_user.first_name}! 👨‍💼\n\n"
            "Siz admin panelidasiz. Foydalanuvchi so'rovlari avtomatik ravishda sizga yuboriladi."
        )
        show_admin_menu(message)
        return
    
    # Foydalanuvchi ma'lumotlarini boshlang'ich holatga keltirish
    if user_id not in user_data:
        user_data[user_id] = {}
    
    bot.send_message(
        message.chat.id,
        f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\n"
        "Ro'yxatdan o'tish botiga xush kelibsiz!\n"
        "Iltimos, siz foydalanish shartlariga rozilik berishingiz kerak."
    )
    
    show_terms_agreement(message)

@bot.message_handler(commands=['foydalanish'])
def usage_instructions(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Bu buyruq foydalanuvchilar uchun mo'ljallangan.")
        return
        
    usage_text = (
        "📖 Foydalanish yo'riqnomasi:\n\n"
        "Foydalanish uchun institut hududidagi wi-fi tarmoqlariga ulanishingiz kerak va sizga habar keladi "
        "ulanish kerak degan shuni bosasiz internetda ochilgan oynaga login parolingizni kiritasiz internet "
        "ishlashni boshlaydi.\n\n"
        "Agar siz habarnomani ko'rmagan bo'lsangiz yoki kelmagan bo'lsa internet brauzerdan "
        "https://172.17.0.22:4080/login sahifasiga kirishingiz kerak.\n\n"
        "📞 Yordam kerak bo'lsa admin bilan bog'laning."
    )
    
    bot.send_message(message.chat.id, usage_text)

@bot.message_handler(func=lambda message: message.text == "👥 Foydalanuvchilar ro'yxati")
def admin_users_list(message):
    if not is_admin(message.from_user.id):
        return
    admin_panel(message)

@bot.message_handler(func=lambda message: message.text == "📊 Statistika")
def admin_statistics(message):
    if not is_admin(message.from_user.id):
        return
    
    total_users = len([u for u in user_data.values() if u.get('step') == 'completed'])
    pending_count = len(pending_requests)
    approved_count = len(approved_requests)
    
    stats_text = (
        f"📊 Statistika:\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"⏳ Kutilayotgan so'rovlar: {pending_count}\n"
        f"✅ Tasdiqlangan so'rovlar: {approved_count}"
    )
    
    bot.send_message(message.chat.id, stats_text)

@bot.message_handler(func=lambda message: message.text == "📖 Foydalanish yo'riqnomasi")
def usage_button_handler(message):
    usage_instructions(message)

# Login parol olish jarayoni
@bot.message_handler(func=lambda message: message.text == "🔐 Login parol olish")
def get_login_start(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Admin sifatida siz foydalanuvchi funksiyalaridan foydalana olmaysiz.")
        return
        
    user_id = str(message.from_user.id)
    user_data[user_id] = {
        'step': 'get_name',
        'type': 'olish',
        'timestamp': datetime.now().isoformat()
    }
    
    markup = types.ReplyKeyboardRemove()
    bot.send_message(
        message.chat.id,
        "Ism va familyangizni kiriting:",
        reply_markup=markup
    )

# Login parol tiklash jarayoni
@bot.message_handler(func=lambda message: message.text == "🔄 Login parol tiklash")
def reset_login_start(message):
    if is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Admin sifatida siz foydalanuvchi funksiyalaridan foydalana olmaysiz.")
        return
        
    user_id = str(message.from_user.id)
    user_data[user_id] = {
        'step': 'reset_name',
        'type': 'tiklash',
        'timestamp': datetime.now().isoformat()
    }
    
    markup = types.ReplyKeyboardRemove()
    bot.send_message(
        message.chat.id,
        "Ism va familyangizni kiriting:",
        reply_markup=markup
    )

# Matn xabarlarini qayta ishlash
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if is_admin(message.from_user.id):
        return
        
    user_id = str(message.from_user.id)
    
    if user_id not in user_data:
        start_message(message)
        return
    
    step = user_data[user_id].get('step', '')
    
    # Login parol olish jarayoni
    if step == 'get_name':
        user_data[user_id]['name'] = message.text
        user_data[user_id]['step'] = 'get_group'
        bot.send_message(message.chat.id, "Guruhingizni kiriting:")
        
    elif step == 'get_group':
        user_data[user_id]['group'] = message.text
        user_data[user_id]['step'] = 'get_phone'
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn = types.KeyboardButton("📱 Telefon raqamni ulashish", request_contact=True)
        markup.add(btn)
        
        bot.send_message(
            message.chat.id,
            "Telefon raqamingizni ulashing:",
            reply_markup=markup
        )
        
    elif step == 'get_passport':
        bot.send_message(message.chat.id, "Iltimos, pasport rasmingizni yuboring!")
        
    elif step == 'create_login':
        user_data[user_id]['login'] = message.text
        user_data[user_id]['step'] = 'create_password'
        bot.send_message(message.chat.id, "Endi parolni kiriting:")
        
    elif step == 'create_password':
        user_data[user_id]['password'] = message.text
        user_data[user_id]['step'] = 'completed'
        
        # Adminга yuborish uchun tayyorlash
        send_to_admin(user_id)
        
        show_user_menu(message)
        
    # Login parol tiklash jarayoni
    elif step == 'reset_name':
        user_data[user_id]['name'] = message.text
        user_data[user_id]['step'] = 'reset_group'
        bot.send_message(message.chat.id, "Guruhingizni kiriting:")
        
    elif step == 'reset_group':
        user_data[user_id]['group'] = message.text
        user_data[user_id]['step'] = 'new_login'
        bot.send_message(message.chat.id, "Yangi loginni kiriting:")
        
    elif step == 'new_login':
        user_data[user_id]['login'] = message.text
        user_data[user_id]['step'] = 'new_password'
        bot.send_message(message.chat.id, "Yangi parolni kiriting:")
        
    elif step == 'new_password':
        user_data[user_id]['password'] = message.text
        user_data[user_id]['step'] = 'completed'
        
        # Adminга yuborish uchun tayyorlash
        send_to_admin(user_id)
        
        show_user_menu(message)

# Telefon raqam va pasport rasmi
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if is_admin(message.from_user.id):
        return
        
    user_id = str(message.from_user.id)
    
    if user_id in user_data and user_data[user_id].get('step') == 'get_phone':
        user_data[user_id]['phone'] = message.contact.phone_number
        user_data[user_id]['step'] = 'get_passport'
        
        markup = types.ReplyKeyboardRemove()
        bot.send_message(
            message.chat.id,
            "Pasport rasmingizni yuboring:",
            reply_markup=markup
        )

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if is_admin(message.from_user.id):
        return
        
    user_id = str(message.from_user.id)
    
    if user_id in user_data and user_data[user_id].get('step') == 'get_passport':
        # Rasmni saqlash
        file_info = bot.get_file(message.photo[-1].file_id)
        user_data[user_id]['passport_photo'] = message.photo[-1].file_id
        user_data[user_id]['step'] = 'create_login'
        
        bot.send_message(message.chat.id, "Loginni kiriting:")

def send_to_admin(user_id):
    if user_id not in user_data:
        return
    
    data = user_data[user_id]
    request_id = f"{user_id}_{int(datetime.now().timestamp())}"
    pending_requests[request_id] = user_id
    
    # Ma'lumotlarni tayyorlash
    info_text = f"📋 Yangi so'rov:\n\n"
    info_text += f"👤 Ism: {data.get('name', 'N/A')}\n"
    info_text += f"👥 Guruh: {data.get('group', 'N/A')}\n"
    
    if data.get('phone'):
        info_text += f"📱 Telefon: {data.get('phone')}\n"
    
    info_text += f"🔑 Login: {data.get('login', 'N/A')}\n"
    info_text += f"🔐 Parol: {data.get('password', 'N/A')}\n"
    info_text += f"📅 Vaqt: {data.get('timestamp', 'N/A')}\n"
    info_text += f"🔄 Tur: {data.get('type', 'N/A')}\n"
    
    # Inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_approve = types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{request_id}")
    btn_reject = types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"reject_{request_id}")
    markup.add(btn_approve, btn_reject)
    
    for admin_id in ADMIN_IDS:
        try:
            if data.get('passport_photo'):
                bot.send_photo(
                    admin_id,
                    data['passport_photo'],
                    caption=info_text,
                    reply_markup=markup
                )
            else:
                bot.send_message(
                    admin_id,
                    info_text,
                    reply_markup=markup
                )
        except Exception as e:
            print(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")
    
    save_data()

# Admin javoblari
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "agree_terms":
        user_id = str(call.from_user.id)
        bot.answer_callback_query(call.id, "Rozilik berildi!")
        bot.edit_message_text(
            "✅ Foydalanish shartlariga rozilik berdingiz!",
            call.message.chat.id,
            call.message.message_id
        )
        show_user_menu(call.message)
        return
    
    elif call.data == "cancel_terms":
        bot.answer_callback_query(call.id, "Bekor qilindi!")
        bot.edit_message_text(
            "❌ Foydalanish shartlari rad etildi. Botdan foydalanish uchun shartlarga rozilik berish kerak.",
            call.message.chat.id,
            call.message.message_id
        )
        return
    
    if call.data == "already_processed":
        bot.answer_callback_query(call.id, "Bu so'rov allaqachon qayta ishlangan!")
        return
    
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "Sizda ruxsat yo'q!")
        return
    
    action, request_id = call.data.split('_', 1)
    
    if request_id not in pending_requests:
        bot.answer_callback_query(call.id, "So'rov topilmadi yoki allaqachon qayta ishlangan!")
        return
    
    user_id = pending_requests[request_id]
    data = user_data.get(user_id, {})
    
    if action == "approve":
        approved_requests[request_id] = {
            'user_id': user_id,
            'admin_id': call.from_user.id,
            'admin_name': call.from_user.first_name,
            'timestamp': datetime.now().isoformat()
        }
        
        approval_text = (
            "✅ Sizning so'rovingiz tasdiqlandi!\n\n"
            f"🔑 Login: {data.get('login', 'N/A')}\n"
            f"🔐 Parol: {data.get('password', 'N/A')}\n\n"
            "Login va parolingiz faollashtirildi.\n"
            "Foydalanish yo'riqnomasi uchun /foydalanish buyrug'ini bosing."
        )
        
        bot.send_message(int(user_id), approval_text)
        
        # Adminга javob
        bot.answer_callback_query(call.id, "So'rov tasdiqlandi!")
        
        approved_markup = types.InlineKeyboardMarkup()
        approved_markup.add(types.InlineKeyboardButton("✅ Tasdiqlangan", callback_data="already_processed"))
        
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=approved_markup
        )
        
        notification_text = (
            f"ℹ️ So'rov tasdiqlandi (Admin: {call.from_user.first_name})\n"
            f"Foydalanuvchi: {data.get('name', 'N/A')}\n"
            f"Login: {data.get('login', 'N/A')}"
        )
        
        for admin_id in ADMIN_IDS:
            if admin_id != call.from_user.id:
                try:
                    bot.send_message(admin_id, notification_text)
                except:
                    pass
        
    elif action == "reject":
        # Foydalanuvchiga rad etish xabari
        bot.send_message(
            int(user_id),
            "❌ Sizning so'rovingiz rad etildi.\n"
            "Iltimos, qaytadan urinib ko'ring."
        )
        
        # Adminга javob
        bot.answer_callback_query(call.id, "So'rov rad etildi!")
        
        rejected_markup = types.InlineKeyboardMarkup()
        rejected_markup.add(types.InlineKeyboardButton("❌ Rad etilgan", callback_data="already_processed"))
        
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=rejected_markup
        )
        
        notification_text = (
            f"ℹ️ So'rov rad etildi (Admin: {call.from_user.first_name})\n"
            f"Foydalanuvchi: {data.get('name', 'N/A')}"
        )
        
        for admin_id in ADMIN_IDS:
            if admin_id != call.from_user.id:
                try:
                    bot.send_message(admin_id, notification_text)
                except:
                    pass
    
    # So'rovni o'chirish
    del pending_requests[request_id]
    save_data()

@bot.message_handler(commands=['users'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "Sizda admin huquqi yo'q!")
        return
    
    if not user_data:
        bot.send_message(message.chat.id, "📭 Hech qanday foydalanuvchi ma'lumoti yo'q.")
        return
    
    info = "👥 Barcha foydalanuvchilar:\n\n"
    count = 0
    for user_id, data in user_data.items():
        if data.get('step') == 'completed':  # Faqat tugallangan so'rovlar
            count += 1
            info += f"🆔 ID: {user_id}\n"
            info += f"👤 Ism: {data.get('name', 'N/A')}\n"
            info += f"👥 Guruh: {data.get('group', 'N/A')}\n"
            info += f"📱 Telefon: {data.get('phone', 'N/A')}\n"
            info += f"🔑 Login: {data.get('login', 'N/A')}\n"
            info += f"🔐 Parol: {data.get('password', 'N/A')}\n"
            info += f"🔄 Tur: {data.get('type', 'N/A')}\n"
            info += f"📅 Vaqt: {data.get('timestamp', 'N/A')}\n"
            info += "─" * 30 + "\n"
    
    info += f"\n📊 Jami: {count} ta foydalanuvchi"
    
    if len(info) > 4000:
        parts = [info[i:i+4000] for i in range(0, len(info), 4000)]
        for part in parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, info)

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    print(f"Admin IDs: {ADMIN_IDS}")
    try:
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Bot xatolik: {e}")
        # Qayta ishga tushirish
        import time
        time.sleep(5)
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
