import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from config import TELEGRAM_BOT_TOKEN, ADMIN_CHAT_ID
from spreadsheet import get_employees, parse_date, get_expiring_soon
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        await message.answer("Доступ запрещён")
        return
    
    await message.answer(
        "🔔 Бот напоминатель ЭЦП\n\n"
        "Команды:\n"
        "/list - список всех\n"
        "/check - проверить сроки\n"
        "/soon - истекающие скоро"
    )

@router.message(Command("list"))
async def cmd_list(message: Message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        await message.answer("Доступ запрещён")
        return
    
    employees = get_employees()
    
    if not employees:
        await message.answer("Список сотрудников пуст")
        return
    
    today = datetime.now().date()
    lines = ["📋 Список сотрудников:\n"]
    
    for emp in employees:
        end_date = parse_date(emp['end_date'])
        if end_date:
            days_left = (end_date.date() - today).days
            if days_left < 0:
                status = f"⚠️ Просрочено на {abs(days_left)} дн."
            elif days_left == 0:
                status = "🔴 Сегодня!"
            elif days_left <= 7:
                status = f"🟡 {days_left} дн."
            else:
                status = f"🟢 {days_left} дн."
        else:
            status = "❓ Неизвестно"
        
        lines.append(f"{emp['name']}")
        lines.append(f"   {emp['position']} | {status}")
        lines.append("")
    
    await message.answer("\n".join(lines))

@router.message(Command("check"))
async def cmd_check(message: Message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        await message.answer("Доступ запрещён")
        return
    
    expiring = get_expiring_soon([30, 14, 7, 3, 1])
    overdue = expiring.get(-1, [])
    
    msg_parts = ["🔍 Проверка сроков ЭЦП:\n"]
    
    if overdue:
        msg_parts.append("⚠️ Просрочены:")
        for emp in overdue:
            msg_parts.append(f"• {emp['name']} ({emp.get('days_overdue', '')} дн.)")
        msg_parts.append("")
    
    for days in [30, 14, 7, 3, 1]:
        if expiring.get(days):
            msg_parts.append(f"⏰ Через {days} дн.:")
            for emp in expiring[days]:
                msg_parts.append(f"• {emp['name']}")
            msg_parts.append("")
    
    if len(msg_parts) == 1:
        await message.answer("✅ Нет сотрудников с истекающей ЭЦП")
        return
    
    await message.answer("\n".join(msg_parts))

@router.message(Command("soon"))
async def cmd_soon(message: Message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        await message.answer("Доступ запрещён")
        return
    
    expiring = get_expiring_soon([7, 3, 1])
    
    if not any(expiring.values()):
        await message.answer("✅ Нет сотрудников с истекающей ЭЦП (7 дней)")
        return
    
    msg_parts = ["⚠️ Истекают в ближайшую неделю:\n"]
    
    for days in [7, 3, 1]:
        if expiring.get(days):
            msg_parts.append(f"{'🔴' if days <= 3 else '🟡'} {days} дн.:")
            for emp in expiring[days]:
                msg_parts.append(f"• {emp['name']} - {emp['position']}")
    
    await message.answer("\n".join(msg_parts))

async def send_daily_notification():
    pass

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
