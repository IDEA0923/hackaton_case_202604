import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class registr(StatesGroup):
    role = State()

class student_what_wanna_do(StatesGroup):
    a1 = State()

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

import users_func
import alerts
import admin_pannel
import ai_api
import env

# Обычная сессия, без прокси – бот выйдет в интернет через твой системный VPN
bot = Bot(token=env.TOKEN)
rt = Router()

@rt.message(Command("start"))
async def command_start(message: Message, state: FSMContext):
    print(f"[+] message from {message.from_user.id}")
    buff = await users_func.database.db.aread(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    if buff:
        role = buff[0][1]
        if role == 1:           # ученик
            await student_main_menu(message, state)
        elif role == 2:         # учитель
            await message.answer("Интерфейс учителя пока в разработке.")
        else:                   # родитель
            await message.answer("Интерфейс родителя пока в разработке.")
    else:
        txt = f"Привет! Твой ID: {message.from_user.id}\n\nВыбери роль:"
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Ученик"), KeyboardButton(text="Учитель"), KeyboardButton(text="Родитель")],
            [KeyboardButton(text="Отменить")]
        ], resize_keyboard=True)
        await message.answer(txt, reply_markup=kb)
        await state.set_state(registr.role)

@rt.message(registr.role)
async def st_reg_2(mess: Message, state: FSMContext):
    await state.clear()
    ans = mess.text
    r = 0
    if ans == "Ученик":
        r = 1
    elif ans == "Учитель":
        r = 2
    elif ans == "Родитель":
        r = 3
    elif ans == "Отменить":
        await mess.answer("Ок, возвращайся позже.\n\n /start еще раз")
        return
    else:
        await mess.answer("Неверный вариант ответа. Нажми /start и выбери роль снова.")
        return

    code = await users_func.registration(mess.from_user.id, r)
    if code == 0:
        await mess.answer("Регистрация прошла успешно!", reply_markup=ReplyKeyboardRemove())
        if r == 1:
            await student_main_menu(mess, state)
    else:
        await mess.answer(f"Ошибка регистрации: {code}")
        await alerts.alert_for_all_admins(f"[-] ERROR: registration error at {mess.from_user.id}, code: {code}")

async def student_main_menu(mess: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Мои задачи"), KeyboardButton(text="Прогресс")],
        [KeyboardButton(text="Добавить задачу"), KeyboardButton(text="Помощь")],
        [KeyboardButton(text="Отменить")]
    ], resize_keyboard=True)
    await mess.answer("Ты ученик. Выбери действие:", reply_markup=kb)
    await state.set_state(student_what_wanna_do.a1)

@rt.message(student_what_wanna_do.a1)
async def st_what_wanna_do(mess: Message, state: FSMContext):
    if mess.text == "Мои задачи":
        tasks = await users_func.get_tasks(mess.from_user.id)
        if not tasks:
            await mess.answer("У тебя пока нет задач")
        else:
            resp = "📋 Твои задачи:\n"
            for t in tasks:
                status = "✅" if t[4] else "⬜"
                resp += f"{status} [{t[0]}] {t[1]} – {t[2]} (до {t[3]})\n"
            await mess.answer(resp)
    elif mess.text == "Добавить задачу":
        await mess.answer("Создавай задачи через Mini App (веб-интерфейс).")
    elif mess.text == "Прогресс":
        await mess.answer("Статистика доступна в Mini App.")
    elif mess.text == "Помощь":
        await mess.answer("Напиши любой текст, и я передам его AI‑помощнику.")
    elif mess.text == "Отменить":
        await mess.answer("Хорошо, возвращайся позже.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await mess.answer("Выбери действие с клавиатуры.")

@rt.message(F.text)
async def garbage_collector(mess: Message):
    if await users_func.is_regged(mess.from_user.id):
        await mess.answer("Передаю твой текст AI...")
        ai_ans = await ai_api.get_AI_answer(mess.text)
        if ai_ans is None:
            ai_ans = "Ошибка AI‑сервиса, попробуй позже."
            await alerts.alert_for_all_admins(f"[-] ERROR: AI answer is None for user {mess.from_user.id}")
        await mess.answer(ai_ans)
    else:
        await mess.answer("Сначала зарегистрируйся: /start")

async def main():
    dp = Dispatcher()
    dp.include_router(admin_pannel.rt)
    dp.include_router(rt)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())