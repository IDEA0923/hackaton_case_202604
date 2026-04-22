import asyncio
import logging
import sys
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
            await student_main_menu(mess=message)
        else:
            await message.answer(str(buff))
    else:
        txt = f"какой-то ебанный текст , и регистрация \n\n твой ID :{message.from_user.id} \n , а еще петушара выбери роль :"
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Прораб"), KeyboardButton(text="Петух") , KeyboardButton(text="Рабовладелец")], [KeyboardButton(text="Отменить")]], resize_keyboard=True)
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
    else:
        await mess.answer(f"ERROR in registration : {ans}")
        await alerts.alert_for_all_admins(F"[-]ERROR:\n<blockquote>error in registrtion at {mess.from_user.id} \n error code: {ans} </blockquote>")



async def student_main_menu(mess : Message ,state: FSMContext ):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="задания"), KeyboardButton(text="оценки") ],[KeyboardButton(text="добавить учителя"), KeyboardButton(text="добавить родителя")] ,[KeyboardButton(text="Отменить")]], resize_keyboard=True)
    await mess.answer("Роль : <code> Ученик </code>\n\nВыбери действие : " , parse_mode="HTML" , reply_markup=kb)
    await state.set_state(student_what_wanna_do.a1)

@rt.message(student_what_wanna_do.a1)
async def st_what_wanna_do(mess : Message , state: FSMContext):
    if (mess.text == "задания" ):
        await mess.answer("your task:")


    

@rt.message(F.text)
async def garbage_collector(mess: Message):
    if await users_func.is_regged(mess.from_user.id):
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
