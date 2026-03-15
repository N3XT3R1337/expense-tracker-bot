from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from ..models.base import async_session_factory
from ..services.user_service import get_or_create_user
from .keyboards import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session_factory() as session:
        await get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )
    await message.answer(
        f"👋 Welcome to Expense Tracker, {message.from_user.first_name}!\n\n"
        "I'll help you track your expenses, set budgets, and generate reports.\n\n"
        "Choose an option below:",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>Available Commands:</b>\n\n"
        "/start - Main menu\n"
        "/help - Show this help\n"
        "/add - Quick add expense\n"
        "/report - Monthly report\n"
        "/budget - Manage budgets\n"
        "/export - Export CSV\n"
        "/categories - Manage categories\n"
        "/stats - Quick statistics",
        parse_mode="HTML",
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    from datetime import datetime
    from ..services.expense_service import get_monthly_total, get_monthly_by_category

    now = datetime.utcnow()
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id)
        total = await get_monthly_total(session, user.id, now.year, now.month)
        by_category = await get_monthly_by_category(session, user.id, now.year, now.month)

    text = f"📊 <b>Stats for {now.strftime('%B %Y')}</b>\n\n"
    text += f"💰 Total spent: <b>${total:,.2f}</b>\n\n"

    if by_category:
        text += "<b>By category:</b>\n"
        for name, emoji, amount in by_category:
            text += f"  {emoji} {name}: ${amount:,.2f}\n"
    else:
        text += "No expenses recorded this month."

    await message.answer(text, parse_mode="HTML")


@router.message(Command("add"))
async def cmd_add(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Usage: /add <amount> [description]\n"
            "Or use the inline menu to add expenses with categories.",
            reply_markup=main_menu_keyboard(),
        )
        return

    from .callbacks import start_add_expense
    await start_add_expense(message)
