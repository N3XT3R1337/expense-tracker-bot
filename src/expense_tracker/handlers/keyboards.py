from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..models.expense import Category


def main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💰 Add Expense", callback_data="add_expense")],
        [InlineKeyboardButton(text="📊 Monthly Report", callback_data="report_month")],
        [InlineKeyboardButton(text="📋 Recent Expenses", callback_data="recent_expenses")],
        [InlineKeyboardButton(text="📁 Categories", callback_data="categories")],
        [InlineKeyboardButton(text="💳 Budgets", callback_data="budgets")],
        [InlineKeyboardButton(text="📥 Export CSV", callback_data="export_csv")],
        [InlineKeyboardButton(text="📄 PDF Report", callback_data="pdf_report")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def categories_keyboard(categories: list[Category], action: str = "select_cat") -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        buttons.append(
            [InlineKeyboardButton(text=f"{cat.emoji} {cat.name}", callback_data=f"{action}:{cat.id}")]
        )
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def budget_categories_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        buttons.append(
            [InlineKeyboardButton(text=f"{cat.emoji} {cat.name}", callback_data=f"budget_cat:{cat.id}")]
        )
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm_exp:{expense_id}"),
            InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_exp:{expense_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")]]
    )


def report_period_keyboard() -> InlineKeyboardMarkup:
    from datetime import datetime

    now = datetime.utcnow()
    current_month = now.strftime("%B %Y")
    prev_month_num = now.month - 1 if now.month > 1 else 12
    prev_year = now.year if now.month > 1 else now.year - 1
    prev_month = datetime(prev_year, prev_month_num, 1).strftime("%B %Y")

    buttons = [
        [InlineKeyboardButton(text=f"📅 {current_month}", callback_data=f"report:{now.year}:{now.month}")],
        [InlineKeyboardButton(text=f"📅 {prev_month}", callback_data=f"report:{prev_year}:{prev_month_num}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def expenses_list_keyboard(expenses: list, page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    buttons = []
    start = page * per_page
    end = start + per_page
    page_expenses = expenses[start:end]

    for exp in page_expenses:
        buttons.append(
            [InlineKeyboardButton(
                text=f"🗑 {exp.category.emoji} {exp.amount} - {exp.description or 'No desc'}",
                callback_data=f"del_exp:{exp.id}",
            )]
        )

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"page:{page - 1}"))
    if end < len(expenses):
        nav_buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data=f"page:{page + 1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
