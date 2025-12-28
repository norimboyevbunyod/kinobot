from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db_query

def lang_kb():
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("🇺🇿 Uz", callback_data="lang_uz"),
        InlineKeyboardButton("🇷🇺 Ru", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 Eng", callback_data="lang_en")
    )

def main_menu(user_id, lang, GLAVNI_ADMIN):
    # Til bazada bo'lmasa default 'uz' qilish
    if lang not in ['uz', 'ru', 'en']:
        lang = 'uz'
        
    texts = {
        'uz': ['Seriallar 🎬', 'Kinolar 🎥', 'Admin Panel ⚙️'], 
        'ru': ['Сериалы 🎬', 'Кино 🎥', 'Админ Панель ⚙️'], 
        'en': ['Serials 🎬', 'Movies 🎥', 'Admin Panel ⚙️']
    }
    
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(texts[lang][0], callback_data="m_serial"),
        InlineKeyboardButton(texts[lang][1], callback_data="m_kino")
    )
    
    # Adminlikni tekshirish
    is_admin = db_query("SELECT id FROM admins WHERE id=?", (user_id,), fetch=True, one=True)
    if user_id == GLAVNI_ADMIN or is_admin:
        kb.add(InlineKeyboardButton(texts[lang][2], callback_data="m_admin"))
    return kb
