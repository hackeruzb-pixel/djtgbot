# index.py
import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

API_TOKEN = "8571256535:AAFiVlsiPLyCH57VTKA728jvOQt5K8_gznI"  # Bot tokenini shu yerga qo'ying
DATA_FILE = "user_tasks.json"      # Ma'lumotlarni saqlash fayli

# Bot va Dispatcher yaratamiz
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Foydalanuvchi ishlarini yozish uchun holat (FSM)
class DailyTask(StatesGroup):
    waiting_for_task = State()

# Foydalanuvchi ma'lumotlarini JSON fayldan yuklash
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
else:
    user_data = {}

# Ma'lumotlarni JSON faylga saqlash
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

# Klaviatura
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📓 Ish yozish")],
        [KeyboardButton(text="📊 Statistikani ko‘rish")]
    ],
    resize_keyboard=True
)

# /start komandasi
@dp.message(Command(commands=["start"]))
async def start(message: Message):
    await message.answer(
        "Salom! Men sizning shaxsiy kundalik yordamchingizman.\n"
        "Quyidagi tugmalar orqali ishlarni yozing yoki statistikani ko‘ring.",
        reply_markup=main_kb
    )

# "Ish yozish" tugmasi
@dp.message(lambda m: m.text == "📓 Ish yozish")
async def write_task(message: Message, state: FSMContext):
    await message.answer("Iltimos, bugungi ishlaringizni yozing:")
    await state.set_state(DailyTask.waiting_for_task)

# Foydalanuvchi ishlarni yozganini qabul qilish
@dp.message(DailyTask.waiting_for_task)
async def save_task(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)  # JSON uchun str ga o'tkazamiz
    task = message.text

    # Agar foydalanuvchi oldin yozgan bo'lsa qo'shamiz
    if user_id in user_data:
        user_data[user_id].append(task)
    else:
        user_data[user_id] = [task]

    save_data()  # Faylga saqlaymiz
    await message.answer("✅ Ishingiz saqlandi!", reply_markup=main_kb)
    await state.clear()

# "Statistikani ko‘rish" tugmasi
@dp.message(lambda m: m.text == "📊 Statistikani ko‘rish")
async def show_stats(message: Message):
    user_id = str(message.from_user.id)
    tasks = user_data.get(user_id, [])

    if not tasks:
        await message.answer("Siz hali hech qanday ish yozmadingiz.")
        return

    stats_text = "📋 Sizning bugungi ishlaringiz:\n\n"
    for i, t in enumerate(tasks, 1):
        stats_text += f"{i}. {t}\n"

    await message.answer(stats_text)

# Botni ishga tushirish
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
