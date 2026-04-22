from main import bot
import env
async def alert_for_all_admins(alert_message_http : str):
    for i in env.admins:
        await bot.send_message(chat_id=i , text=alert_message_http , parse_mode="HTML")