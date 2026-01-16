# index.py
import asyncio
import json
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.client.session.aiohttp import AiohttpSession

API_TOKEN = "BOT_TOKENNI_BU_YERGA_QO'YING"
DATA_FILE = "user_tasks.json"

# ================= PROXY SESSION =================
session = AiohttpSession(
    proxy="http://47.6.9.54:80"
)

# ================= BOT =================
bot = Bot(token=API_TOKEN, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ================= FSM =================
class DailyTask(StatesGroup):
    waiting_for_task = State()
    edit_task_number = State()
    edit_task_text = State()
    delete_task_number = State()

# ================= DATA =================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
else:
    user_data = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

# ================= KEYBOARDS =================
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📓 Ish yozish")],
        [KeyboardButton(text="📊 Statistikani ko‘rish")],
        [KeyboardButton(text="⚙️ Statistika sozlash")]
    ],
    resize_keyboard=True
)

settings_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Ishni tahrirlash")],
        [KeyboardButton(text="🗑 Ishni o‘chirish")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True
)

# ================= START =================
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Salom! Kundalik botga xush kelibsiz 👋",
        reply_markup=main_kb
    )

# ================= ISH YOZISH =================
@dp.message(lambda m: m.text == "📓 Ish yozish")
async def write_task(message: Message, state: FSMContext):
    await message.answer("Bugungi ishingizni yozing:")
    await state.set_state(DailyTask.waiting_for_task)

@dp.message(DailyTask.waiting_for_task)
async def save_task(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data.setdefault(user_id, []).append(message.text)
    save_data()
    await message.answer("✅ Ish saqlandi", reply_markup=main_kb)
    await state.clear()

# ================= STATISTIKA =================
@dp.message(lambda m: m.text == "📊 Statistikani ko‘rish")
async def show_stats(message: Message):
    user_id = str(message.from_user.id)
    tasks = user_data.get(user_id, [])

    if not tasks:
        await message.answer("Siz hali hech qanday ish yozmagansiz.")
        return

    text = "📋 Sizning ishlaringiz:\n\n"
    for i, t in enumerate(tasks, 1):
        text += f"{i}. {t}\n"

    await message.answer(text)

# ================= SOZLASH =================
@dp.message(lambda m: m.text == "⚙️ Statistika sozlash")
async def open_settings(message: Message):
    await message.answer(
        "Statistika sozlash bo‘limi:",
        reply_markup=settings_kb
    )

# ================= ISHNI TAHRIRLASH =================
@dp.message(lambda m: m.text == "✏️ Ishni tahrirlash")
async def edit_task_start(message: Message, state: FSMContext):
    await message.answer("Qaysi ishni tahrirlamoqchisiz? (raqamini yozing)")
    await state.set_state(DailyTask.edit_task_number)

@dp.message(DailyTask.edit_task_number)
async def edit_task_number(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, raqam kiriting")
        return

    await state.update_data(index=int(message.text) - 1)
    await message.answer("Yangi matnni yozing:")
    await state.set_state(DailyTask.edit_task_text)

@dp.message(DailyTask.edit_task_text)
async def edit_task_save(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    data = await state.get_data()
    idx = data["index"]

    if idx < 0 or idx >= len(user_data.get(user_id, [])):
        await message.answer("❌ Noto‘g‘ri raqam")
    else:
        user_data[user_id][idx] = message.text
        save_data()
        await message.answer("✏️ Ish tahrirlandi", reply_markup=settings_kb)

    await state.clear()

# ================= ISHNI O‘CHIRISH =================
@dp.message(lambda m: m.text == "🗑 Ishni o‘chirish")
async def delete_task_start(message: Message, state: FSMContext):
    await message.answer("Qaysi ishni o‘chirmoqchisiz? (raqamini yozing)")
    await state.set_state(DailyTask.delete_task_number)

@dp.message(DailyTask.delete_task_number)
async def delete_task(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)

    if not message.text.isdigit():
        await message.answer("Iltimos, raqam kiriting")
        return

    idx = int(message.text) - 1
    tasks = user_data.get(user_id, [])

    if idx < 0 or idx >= len(tasks):
        await message.answer("❌ Noto‘g‘ri raqam")
    else:
        deleted = tasks.pop(idx)
        save_data()
        await message.answer(
            f"🗑 O‘chirildi:\n{deleted}",
            reply_markup=settings_kb
        )

    await state.clear()

# ================= ORQAGA =================
@dp.message(lambda m: m.text == "⬅️ Orqaga")
async def back(message: Message):
    await message.answer("Asosiy menyu", reply_markup=main_kb)

# ================= RUN =================
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
