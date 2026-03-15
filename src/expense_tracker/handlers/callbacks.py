import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from ..config import load_config
from ..models.base import async_session_factory
from ..reports.csv_export import generate_csv
from ..reports.pdf_report import generate_pdf_report
from ..services.budget_service import check_budget_alerts, get_budgets, set_budget, delete_budget
from ..services.category_service import create_category, delete_category, get_categories
from ..services.expense_service import (
    add_expense,
    delete_expense,
    get_expenses,
    get_monthly_by_category,
    get_monthly_total,
)
from ..services.user_service import get_or_create_user
from .keyboards import (
    back_keyboard,
    budget_categories_keyboard,
    categories_keyboard,
    confirm_keyboard,
    expenses_list_keyboard,
    main_menu_keyboard,
    report_period_keyboard,
)
from .states import BudgetStates, CategoryStates, ExpenseStates

router = Router()
config = load_config()


@router.callback_query(F.data == "main_menu")
async def on_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "📋 <b>Main Menu</b>\n\nChoose an option:",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "add_expense")
async def on_add_expense(callback: CallbackQuery, state: FSMContext):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        cats = await get_categories(session, user.id)
    await callback.message.edit_text(
        "📂 Select a category:", reply_markup=categories_keyboard(cats, "select_cat"), parse_mode="HTML"
    )
    await state.set_state(ExpenseStates.waiting_for_category)
    await callback.answer()


@router.callback_query(F.data.startswith("select_cat:"))
async def on_select_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=category_id)
    await state.set_state(ExpenseStates.waiting_for_amount)
    await callback.message.edit_text(
        "💵 Enter the expense amount:", reply_markup=back_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


@router.message(ExpenseStates.waiting_for_amount)
async def on_amount_entered(message: Message, state: FSMContext):
    try:
        amount = Decimal(message.text.strip().replace(",", ""))
        if amount <= 0:
            raise ValueError()
    except (InvalidOperation, ValueError):
        await message.answer("❌ Please enter a valid positive number.")
        return

    await state.update_data(amount=str(amount))
    await state.set_state(ExpenseStates.waiting_for_description)
    await message.answer("📝 Enter a description (or send /skip):")


@router.message(ExpenseStates.waiting_for_description)
async def on_description_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    description = None if message.text.strip() == "/skip" else message.text.strip()

    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id)
        expense = await add_expense(
            session,
            user.id,
            int(data["category_id"]),
            Decimal(data["amount"]),
            description,
        )

        alerts = await check_budget_alerts(session, user.id, config.budget_alert_threshold)

    text = f"✅ Expense recorded: <b>${Decimal(data['amount']):,.2f}</b>"
    if description:
        text += f"\n📝 {description}"

    if alerts:
        text += "\n\n⚠️ <b>Budget Alerts:</b>"
        for cat_name, spent, limit, ratio in alerts:
            pct = int(ratio * 100)
            text += f"\n  {cat_name}: ${spent:,.2f} / ${limit:,.2f} ({pct}%)"

    await state.clear()
    await message.answer(text, parse_mode="HTML", reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "recent_expenses")
async def on_recent_expenses(callback: CallbackQuery):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        expenses = await get_expenses(session, user.id, limit=20)

    if not expenses:
        await callback.message.edit_text(
            "📭 No expenses found.", reply_markup=back_keyboard(), parse_mode="HTML"
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "📋 <b>Recent Expenses</b>\n(Tap to delete)",
        reply_markup=expenses_list_keyboard(expenses),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("page:"))
async def on_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        expenses = await get_expenses(session, user.id, limit=50)

    await callback.message.edit_reply_markup(
        reply_markup=expenses_list_keyboard(expenses, page)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("del_exp:"))
async def on_delete_expense(callback: CallbackQuery):
    expense_id = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        result = await delete_expense(session, expense_id, user.id)

    if result:
        await callback.answer("🗑 Expense deleted!")
    else:
        await callback.answer("❌ Expense not found.")

    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        expenses = await get_expenses(session, user.id, limit=20)

    if expenses:
        await callback.message.edit_text(
            "📋 <b>Recent Expenses</b>\n(Tap to delete)",
            reply_markup=expenses_list_keyboard(expenses),
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            "📭 No expenses found.", reply_markup=back_keyboard(), parse_mode="HTML"
        )


@router.callback_query(F.data == "report_month")
async def on_report_month(callback: CallbackQuery):
    await callback.message.edit_text(
        "📊 Select report period:",
        reply_markup=report_period_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("report:"))
async def on_report_period(callback: CallbackQuery):
    parts = callback.data.split(":")
    year, month = int(parts[1]), int(parts[2])

    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        total = await get_monthly_total(session, user.id, year, month)
        by_category = await get_monthly_by_category(session, user.id, year, month)

    month_name = datetime(year, month, 1).strftime("%B %Y")
    text = f"📊 <b>Report for {month_name}</b>\n\n"
    text += f"💰 Total: <b>${total:,.2f}</b>\n\n"

    if by_category:
        text += "<b>Breakdown:</b>\n"
        for name, emoji, amount in by_category:
            pct = (amount / total * 100) if total > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            text += f"  {emoji} {name}: ${amount:,.2f} ({pct:.1f}%)\n  {bar}\n"
    else:
        text += "No expenses recorded."

    await callback.message.edit_text(text, reply_markup=back_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "categories")
async def on_categories(callback: CallbackQuery):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        cats = await get_categories(session, user.id)

    text = "📁 <b>Your Categories:</b>\n\n"
    for cat in cats:
        text += f"  {cat.emoji} {cat.name}\n"
    text += "\nSend /newcategory <emoji> <name> to add a new category."

    await callback.message.edit_text(text, reply_markup=back_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "budgets")
async def on_budgets(callback: CallbackQuery, state: FSMContext):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        budgets = await get_budgets(session, user.id)
        alerts = await check_budget_alerts(session, user.id, 0.0)

    text = "💳 <b>Your Budgets:</b>\n\n"
    if budgets:
        for cat_name, spent, limit, ratio in alerts:
            pct = int(ratio * 100)
            status = "🟢" if ratio < 0.5 else "🟡" if ratio < 0.8 else "🔴"
            text += f"  {status} {cat_name}: ${spent:,.2f} / ${limit:,.2f} ({pct}%)\n"
    else:
        text += "No budgets set.\n"

    text += "\nTap a category below to set/update a budget:"

    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        cats = await get_categories(session, user.id)

    await callback.message.edit_text(
        text, reply_markup=budget_categories_keyboard(cats), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("budget_cat:"))
async def on_budget_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split(":")[1])
    await state.update_data(budget_category_id=category_id)
    await state.set_state(BudgetStates.waiting_for_amount)
    await callback.message.edit_text(
        "💳 Enter the monthly budget limit (or 0 to remove):",
        reply_markup=back_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(BudgetStates.waiting_for_amount)
async def on_budget_amount(message: Message, state: FSMContext):
    try:
        amount = Decimal(message.text.strip().replace(",", ""))
        if amount < 0:
            raise ValueError()
    except (InvalidOperation, ValueError):
        await message.answer("❌ Please enter a valid non-negative number.")
        return

    data = await state.get_data()
    category_id = int(data["budget_category_id"])

    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id)
        if amount == 0:
            await delete_budget(session, user.id, category_id)
            await message.answer("🗑 Budget removed.", reply_markup=main_menu_keyboard())
        else:
            await set_budget(session, user.id, category_id, amount)
            await message.answer(
                f"✅ Budget set to <b>${amount:,.2f}</b>/month",
                parse_mode="HTML",
                reply_markup=main_menu_keyboard(),
            )

    await state.clear()


@router.callback_query(F.data == "export_csv")
async def on_export_csv(callback: CallbackQuery):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        expenses = await get_expenses(session, user.id, limit=1000)

    if not expenses:
        await callback.message.edit_text(
            "📭 No expenses to export.", reply_markup=back_keyboard(), parse_mode="HTML"
        )
        await callback.answer()
        return

    csv_data = generate_csv(expenses)
    file = BufferedInputFile(
        csv_data.encode("utf-8"),
        filename=f"expenses_{datetime.utcnow().strftime('%Y%m%d')}.csv",
    )
    await callback.message.answer_document(file, caption="📥 Your expense export")
    await callback.answer()


@router.callback_query(F.data == "pdf_report")
async def on_pdf_report(callback: CallbackQuery):
    now = datetime.utcnow()
    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        expenses = await get_expenses(session, user.id, limit=500)
        by_category = await get_monthly_by_category(session, user.id, now.year, now.month)
        total = await get_monthly_total(session, user.id, now.year, now.month)

    if not expenses:
        await callback.message.edit_text(
            "📭 No expenses for PDF report.", reply_markup=back_keyboard(), parse_mode="HTML"
        )
        await callback.answer()
        return

    pdf_bytes = generate_pdf_report(
        expenses=expenses,
        by_category=by_category,
        total=total,
        month_name=now.strftime("%B %Y"),
        username=callback.from_user.first_name or "User",
    )

    file = BufferedInputFile(
        pdf_bytes,
        filename=f"report_{now.strftime('%Y%m')}.pdf",
    )
    await callback.message.answer_document(file, caption="📄 Your monthly PDF report")
    await callback.answer()


async def start_add_expense(message: Message):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id)
        cats = await get_categories(session, user.id)
    await message.answer(
        "📂 Select a category:",
        reply_markup=categories_keyboard(cats, "select_cat"),
        parse_mode="HTML",
    )
