from aiogram import Bot, Dispatcher, html, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
#from aiogram.fsm.context import ContextTypes
from aiogram import Router
from aiogram.types import ReplyParameters
from aiogram.utils.markdown import blockquote
import alerts
import env
from aiogram.types import FSInputFile
rt = Router()

@rt.message(Command("deploy"))
async def command_deploy(mess : Message):
    if mess.from_user.id in env.admins:
        await mess.answer("[+] Starting deploy")

    else:
        await alerts.alert_for_all_admins(f"[!]ALERT \n some one wrote :\n<blockquote>/deploy</blockquote>\n \n userID: <blockquote>{mess.from_user.id}</blockquote>")


@rt.message(Command("get_database"))
async def command_deploy(mess : Message):
    if mess.from_user.id in env.admins:
        await mess.answer("[+] Starting get_database")
        document = FSInputFile(env.db_file)
        await mess.answer_document(document=document , caption=f"database")
    else:
        await alerts.alert_for_all_admins(f"[!]ALERT \n some one wrote :\n<blockquote>/get_database</blockquote>\n \n userID: <blockquote>{mess.from_user.id}</blockquote>")

