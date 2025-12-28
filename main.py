import logging
import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import *
from database import *
from keyboards import *

bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

class BotState(StatesGroup):
    s_ser = State()
    s_kino = State()
    add_adm = State()
    add_ch = State()

async def check_sub(user_id):
    # Kanallar bazasini tekshirish
    channels = db_query("SELECT id FROM channels", fetch=True)
    if not channels:
        return True # Agar kanallar qo'shilmagan bo'lsa, o'tkazib yuboradi
        
    for ch in channels:
        try:
            m = await bot.get_chat_member(ch[0], user_id)
            if m.status in ['left', 'kicked']: 
                return False
        except Exception as e:
            logging.error(f"Kanalni tekshirishda xato: {e}")
            continue
    return True

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    init_db()
    db_query("INSERT OR IGNORE INTO users (id) VALUES (?)", (m.from_user.id,))
    await m.answer("Tilni tanlang / Выберите язык:", reply_markup=lang_kb())

@dp.callback_query_handler(lambda c: c.data.startswith('lang_'))
async def set_lang(c: types.CallbackQuery):
    try:
        l = c.data.split('_')[1]
        # Bazaga tilni saqlash
        db_query("UPDATE users SET lang=? WHERE id=?", (l, c.from_user.id))
        
        # Obunani tekshirish
        if await check_sub(c.from_user.id):
            welcome_text = {"uz": "Xush kelibsiz!", "ru": "Добро пожаловать!", "en": "Welcome!"}
            menu = main_menu(c.from_user.id, l, GLAVNI_ADMIN)
            await c.message.edit_text(welcome_text.get(l, "Xush kelibsiz!"), reply_markup=menu)
        else:
            # Kanallarga azo bolish logic
            kb = InlineKeyboardMarkup(row_width=1)
            channels = db_query("SELECT url FROM channels", fetch=True)
            for ch in channels:
                kb.add(InlineKeyboardButton("A'zo bo'lish / Подписаться", url=ch[0]))
            
            kb.add(InlineKeyboardButton("✅ Tekshirish / Проверить", callback_data=f"recheck_{l}"))
            await c.message.edit_text("Botdan foydalanish uchun kanallarga a'zo bo'ling:\nПодпишитесь на каналы, чтобы использовать бота:", reply_markup=kb)
    except Exception as e:
        logging.error(f"set_lang xatosi: {e}")
        await c.answer(f"Xatolik yuz berdi: {e}", show_alert=True)

@dp.callback_query_handler(lambda c: c.data.startswith('recheck_'))
async def recheck_sub(c: types.CallbackQuery):
    l = c.data.split('_')[1]
    if await check_sub(c.from_user.id):
        menu = main_menu(c.from_user.id, l, GLAVNI_ADMIN)
        await c.message.edit_text("Rahmat! Endi botdan foydalanishingiz mumkin.", reply_markup=menu)
    else:
        await c.answer("Hali hamma kanallarga a'zo bo'lmadingiz!", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "m_admin")
async def admin_panel(c: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    if c.from_user.id == GLAVNI_ADMIN:
        kb.add(InlineKeyboardButton("👥 Admin qo'shish/o'chirish", callback_data="adm_manage"))
    kb.add(InlineKeyboardButton("📢 Kanallarni boshqarish", callback_data="ch_manage"),
           InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main"))
    await c.message.edit_text("Admin boshqaruv paneli:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "back_main")
async def back_main(c: types.CallbackQuery):
    user_data = db_query("SELECT lang FROM users WHERE id=?", (c.from_user.id,), fetch=True, one=True)
    l = user_data[0] if user_data else 'uz'
    await c.message.edit_text("Asosiy menyu:", reply_markup=main_menu(c.from_user.id, l, GLAVNI_ADMIN))

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
