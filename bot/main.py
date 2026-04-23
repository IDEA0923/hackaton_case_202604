import asyncio
import logging
import sys
import time
from os import getenv

from aiogram import Bot, Dispatcher, html, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
#from aiogram.fsm.context import ContextTypes
from aiogram import Router
from aiogram.types import ReplyParameters
from aiogram.utils.markdown import blockquote
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import json
from datetime import datetime

from ai_code import date_to_seconds , datetime
# Обрати внимание, я переименовал функцию во избежание конфликта имён
class registr(StatesGroup):
    role = State()


class state_dialog(StatesGroup):
    a1 = State()
    a2 = State()
    a3 = State()
    a4 = State()
    a5 = State()

class student_what_wanna_do(StatesGroup):
    a1 = State()

class make_task(StatesGroup):
    ai = State()
    task = State()
    for_who = State()
    ids = State()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

import users_func
import alerts
import admin_pannel
import ai_api
import env

bot = Bot(token=env.TOKEN)
rt= Router()



@rt.message(Command("start"))
async def command_start(message : Message ,  state: FSMContext):
    print(f"[+] message from {message.from_user.id}")
    buff = await users_func.database.db.aread(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    if buff != []:
        if buff[0][1] ==2 :
            await student_main_menu(mess=message , state=state)
            return 
        else:
            await message.answer(str(buff))
    else:
        txt = f"какой-то текст , и регистрация \n\n твой ID :{message.from_user.id} \n , а еще петушара выбери роль :"
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Учитель"), KeyboardButton(text="Ученик") , KeyboardButton(text="Родитель")], [KeyboardButton(text="Отменить")]], resize_keyboard=True)
        await message.answer(text=txt , reply_markup=kb)
        await state.set_state(registr.role)


@rt.message(registr.role)
async def st_reg_2(mess : Message , state: FSMContext):
    await state.clear()
    ans = mess.text
    r = 0
    if(ans == "Ученик"):
        r = 2
    elif(ans == "Учитель"):
        r = 3
    elif(ans =="Родитель"):
        r =5
    elif(ans == "Отменить" ):
        await mess.answer("Окк\n\n /start еще раз")
        return
    else:
        await mess.answer("Неверный вариант ответа  \n\n /start и еще раз ")
        return
    ans = await users_func.registration(mess.from_user.id , r)
    if ans == 0:
        await mess.answer("DONE\n\nвы зарегестрированны" , reply_markup=ReplyKeyboardRemove())
        await command_start(mess , state)
    else:
        await mess.answer(f"ERROR in registration : {ans}")
        await alerts.alert_for_all_admins(F"[-]ERROR:\n<blockquote>error in registrtion at {mess.from_user.id} \n error code: {ans} </blockquote>")



async def student_main_menu(mess : Message ,state: FSMContext ):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="задания"), KeyboardButton(text="оценки") ],[KeyboardButton(text="добавить учителя"), KeyboardButton(text="добавить родителя")] ,[KeyboardButton(text="Отменить")]], resize_keyboard=True)
    await mess.answer("Роль : <code> Ученик </code>\n\nВыбери действие : " , parse_mode="HTML" , reply_markup=kb)
    await state.set_state(student_what_wanna_do.a1)

@rt.message(student_what_wanna_do.a1)
async def st_what_wanna_do(mess : Message , state: FSMContext):
    await state.clear()
    if (mess.text == "задания" ):
        print(f"time = {int(time.time())}")
        tasks_now = await users_func.database.db.aread(
            f"SELECT rowid, * FROM tasks WHERE foruser_id = {mess.from_user.id} AND task_end > {int(time.time())}"
            )
        if tasks_now == []:
            kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Создать задание")], [KeyboardButton(text="Отменить")]], resize_keyboard=True)
            await mess.answer(text="Сейчас у тебя нет заданий" , reply_markup=kb)
            await state.set_state(make_task.task)

        else:
            text = "📋 **Твои текущие задания:**\n\n"
            for task in tasks_now:
                t_id = task[0]  # Вот он, твой 143!
                deadline_ts = task[5] # Сдвинулось с 4 на 5 из-за rowid
                
                # Читаем файл
                print(f"id == {t_id}")
                try:
                    with open(f"tasks/{t_id}", "r", encoding="utf-8") as f:
                        task_desc = f.read()
                except FileNotFoundError:
                    task_desc = "Описание отсутствует"

                deadline = datetime.fromtimestamp(deadline_ts).strftime('%d.%m.%Y %H:%M')
                text += f"🆔 `{t_id}` | 🔹 {task_desc}\n🕒 Сдать до: {deadline}\n\n"
            
            await mess.answer(text, parse_mode="Markdown")
            # Возвращаем меню, чтобы юзер мог нажать что-то еще
            await student_main_menu(mess, state)
    
    elif mess.text == "Отменить":
        await state.clear()
        await mess.answer("Главное меню:", reply_markup=ReplyKeyboardRemove())
        await student_main_menu(mess, state)
        
    else:
        await mess.answer("Используй кнопки меню!")
        await state.set_state(student_what_wanna_do.a1)

            
            
@rt.message(make_task.task)
async def make_a_task(mess : Message , state: FSMContext):
    if mess.text == "Отменить":
        await state.clear()
        await mess.answer("Отменено")
        return
    role =  await users_func.get_role(mess.from_user.id)
    if role ==2:
        kb =  ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отменить")]] , resize_keyboard= True )
        await mess.answer("Пропиши задание и время , до которого надо сдать  " , reply_markup=kb)
        await state.set_state(make_task.ai)
    


        

# @rt.message(make_task.ai)
# async def make_a_task(mess : Message , state: FSMContext):
#     if mess.text == "Отменить":
#         await state.clear()
#         await mess.answer("Отменено")
#         return
#     ai_answer = await ai_api.get_AI_answer("")

@rt.message(make_task.ai)
async def process_ai_task_creation(mess: Message, state: FSMContext):
    if mess.text == "Отменить":
        await state.clear()
        await mess.answer("Отменено", reply_markup=ReplyKeyboardRemove())
        return
    
    # 1. Запрос к ИИ. 
    # Промпт должен просить ИИ вернуть JSON: {"task": "текст", "date": "ДД.ММ.ГГГГ ЧЧ:ММ"}
    prompt = (
        f"Извлеки из текста задание и дату дедлайна. "
        f"Текст: {mess.text}. "
        f"Верни ТОЛЬКО JSON формата: {{\"task\": \"...\", \"date\": \"...\"}}. "
        f"Если даты нет, поставь дату через 24 часа от сейчас ({datetime.now().strftime('%d.%m.%Y %H:%M')})."
    )
    
    raw_ai_ans = await ai_api.get_AI_answer(prompt)
    
    try:
        # Парсим JSON из ответа ИИ
        data = json.loads(raw_ai_ans)
        task_text = data.get("task")
        date_str = data.get("date")
        
        # Конвертируем дату в секунды (твой ai_code)
        deadline_seconds = date_to_seconds(date_str)
        start_seconds = int(time.time())
        
        # 2. Пишем в базу
        # task_id (автоинкремент или рандом), foruser_id, fromuser_id, start, end, graded...
        query = (
            "INSERT INTO tasks (foruser_id, fromuser_id, task_start, task_end, graded) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        id = await users_func.database.db.awrite(query, (mess.from_user.id, mess.from_user.id, start_seconds, deadline_seconds, 0))
        print(f"id == {id}")
        tsk =  open(f"tasks/{id}" , "w")
        tsk.write(task_text)
        tsk.close()

        await mess.answer(
            f"✅ Задание создано!\n\n"
            f"📝 **Что:** {task_text}\n"
            f"⏰ **Дедлайн:** {date_str}",
            parse_mode="Markdown"
        )
        await state.clear()
        await student_main_menu(mess, state)

    except Exception as e:
        logging.error(f"Ошибка при создании таска: {e}")
        await mess.answer("Не удалось распознать задание. Попробуй написать четче, например: 'Математика до 25.10.2023 15:00'")


@rt.message(F.text)
async def garbage_collector(mess: Message , state: FSMContext):
    if await users_func.is_regged(mess.from_user.id):
        if mess.text == "задания":
            await st_what_wanna_do(mess ,state )
            return 
        text = "Возможно твой текст содержит таск и это отправляется в нейрослоп ( тк не было явных указаний до  )"
        await mess.answer(text=text)
        ai_ans = await ai_api.get_AI_answer(mess.text)
        if ai_ans == None:
            ai_ans ="ERROR : trouble with AI API"
            await alerts.alert_for_all_admins(F"[-]ERROR:\n<blockquote>error in AI answer at {mess.from_user.id} \n error prompt : {mess.text} </blockquote>")
        await mess.answer(text=ai_ans)
    else: 
        await mess.answer("для того чтобы пользоваться ИИ , надо зарегаться \n\n/start - регистрация")


async def main():
    dp = Dispatcher()
    #добавлене внешних функуий 
    #dp.include_router(common.router)
    dp.include_router(admin_pannel.rt)
    dp.include_router(rt)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[+]bot is started")
