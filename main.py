import logging
import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
    """Kanallarga a'zo bo'lganlikni tekshirish funksiyasi"""
    channels = db_query("SELECT id FROM channels", fetch=True)
    if not channels:
        return True # Kanallar yo'q bo'lsa, o'tkazib yuboradi
    
    for ch in channels:
        try:
            m = await bot.get_chat_member(ch[0], user_id)
            if m.status in ['left', 'kicked']: 
                return False
        except Exception as e:
            logging.error(f"Tekshirishda xato: {e}")
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
        db_query("UPDATE users SET lang=? WHERE id=?", (l, c.from_user.id))
        
        if await check_sub(c.from_user.id):
            menu = main_menu(c.from_user.id, l, GLAVNI_ADMIN)
            await c.message.edit_text("Xush kelibsiz! / Добро пожаловать!", reply_markup=menu)
        else:
            kb = InlineKeyboardMarkup(row_width=1)
            channels = db_query("SELECT url FROM channels", fetch=True)
            for ch in channels:
                kb.add(InlineKeyboardButton("A'zo bo'lish", url=ch[0]))
            kb.add(InlineKeyboardButton("✅ Tekshirish", callback_data=f"recheck_{l}"))
            await c.message.edit_text("Kanallarga a'zo bo'ling:", reply_markup=kb)
    except Exception as e:
        logging.error(f"Xato: {e}")
        await c.answer("Xatolik yuz berdi!")

@dp.callback_query_handler(lambda c: c.data.startswith('recheck_'))
async def recheck(c: types.CallbackQuery):
    l = c.data.split('_')[1]
    if await check_sub(c.from_user.id):
        await c.message.edit_text("Rahmat!", reply_markup=main_menu(c.from_user.id, l, GLAVNI_ADMIN))
    else:
        await c.answer("Hali a'zo bo'lmadingiz!", show_alert=True)

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
