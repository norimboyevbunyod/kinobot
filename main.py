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
    channels = db_query("SELECT id FROM channels", fetch=True)
    for ch in channels:
        try:
            m = await bot.get_chat_member(ch[0], user_id)
            if m.status in ['left', 'kicked']: return False
        except: continue
    return True

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    init_db()
    db_query("INSERT OR IGNORE INTO users (id) VALUES (?)", (m.from_user.id,))
    await m.answer("Tilni tanlang / Выберите язык:", reply_markup=lang_kb())

@dp.callback_query_handler(lambda c: c.data.startswith('lang_'))
async def set_lang(c: types.CallbackQuery):
    l = c.data.split('_')[1]
    db_query("UPDATE users SET lang=? WHERE id=?", (l, c.from_user.id))
    if await check_sub(c.from_user.id):
        await c.message.edit_text("Hush kelibsiz!", reply_markup=main_menu(c.from_user.id, l, GLAVNI_ADMIN))
    else:
        # Kanalga azo bolish logic
        kb = InlineKeyboardMarkup(row_width=1)
        for ch in db_query("SELECT url FROM channels", fetch=True):
            kb.add(InlineKeyboardButton("A'zo bo'lish", url=ch[0]))
        kb.add(InlineKeyboardButton("✅ Tekshirish", callback_data="recheck"))
        await c.message.edit_text("Kanallarga a'zo bo'ling:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "m_admin")
async def admin_panel(c: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    if c.from_user.id == GLAVNI_ADMIN:
        kb.add(InlineKeyboardButton("👥 Admin qo'shish/o'chirish", callback_data="adm_manage"))
    kb.add(InlineKeyboardButton("📢 Kanallarni boshqarish", callback_data="ch_manage"),
           InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main"))
    await c.message.edit_text("Admin boshqaruv paneli:", reply_markup=kb)

# --- SERIAL KANALIDAN QABUL QILISH ---
@dp.channel_post_handler()
async def channel_post(m: types.Message):
    if m.chat.id == KINO_CHANNEL:
        # Kino nomi regex orqali ajratish
        name = re.split(r'\n|\(', m.caption)[0].strip() if m.caption else "Nomsiz kino"
        if not db_query("SELECT id FROM movies WHERE name=?", (name,), fetch=True, one=True):
            db_query("INSERT INTO movies (name, file_id) VALUES (?, ?)", (name, m.video.file_id))
            await bot.send_message(GLAVNI_ADMIN, f"✅ Kino saqlandi: {name}")

    if m.chat.id == SERIAL_CHANNEL:
        await bot.send_message(GLAVNI_ADMIN, f"Yangi serial qismi keldi. Tasdiqlang yoki nomlang.")

@dp.callback_query_handler(lambda c: c.data == "back_main")
async def back_main(c: types.CallbackQuery):
    l = db_query("SELECT lang FROM users WHERE id=?", (c.from_user.id,), fetch=True, one=True)[0]
    await c.message.edit_text("Asosiy menyu:", reply_markup=main_menu(c.from_user.id, l, GLAVNI_ADMIN))

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)