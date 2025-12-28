from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db_query

def lang_kb():
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("🇺🇿 Uz", callback_data="lang_uz"),
        InlineKeyboardButton("🇷🇺 Ru", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 Eng", callback_data="lang_en")
    )

def main_menu(user_id, lang, GLAVNI_ADMIN):
    texts = {'uz': ['Serial', 'Kino', 'Admin panel'], 'ru': ['Сериал', 'Кино', 'Админ'], 'en': ['Serial', 'Movie', 'Admin']}
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(texts[lang][0], callback_data="m_serial"),
        InlineKeyboardButton(texts[lang][1], callback_data="m_kino")
    )
    is_admin = db_query("SELECT id FROM admins WHERE id=?", (user_id,), fetch=True, one=True)
    if user_id == GLAVNI_ADMIN or is_admin:
        kb.add(InlineKeyboardButton(texts[lang][2], callback_data="m_admin"))
    return kb

def serial_parts_kb(name, start=1):
    kb = InlineKeyboardMarkup(row_width=5)
    for i in range(start, start + 10):
        kb.insert(InlineKeyboardButton(str(i), callback_data=f"getser_{name}_{i}"))
    kb.row(InlineKeyboardButton("⬅️", callback_data=f"page_{name}_{start-10}"),
           InlineKeyboardButton("➡️", callback_data=f"page_{name}_{start+10}"))
    kb.add(InlineKeyboardButton("⬅️ Orqaga", callback_data="m_serial"))
    return kb