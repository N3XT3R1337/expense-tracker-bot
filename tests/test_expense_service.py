from datetime import datetime
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.expense_tracker.models.expense import Category, Expense, User
from src.expense_tracker.services.expense_service import (
    add_expense,
    delete_expense,
    get_expenses,
    get_monthly_by_category,
    get_monthly_total,
)


@pytest.mark.asyncio
async def test_add_expense(session: AsyncSession, sample_user: User, sample_category: Category):
    expense = await add_expense(
        session, sample_user.id, sample_category.id, Decimal("25.50"), "Lunch"
    )
    assert expense.id is not None
    assert expense.amount == Decimal("25.50")
    assert expense.description == "Lunch"
    assert expense.user_id == sample_user.id
    assert expense.category_id == sample_category.id


@pytest.mark.asyncio
async def test_get_expenses(session: AsyncSession, sample_user: User, sample_category: Category):
    await add_expense(session, sample_user.id, sample_category.id, Decimal("10.00"), "Coffee")
    await add_expense(session, sample_user.id, sample_category.id, Decimal("20.00"), "Dinner")

    expenses = await get_expenses(session, sample_user.id)
    assert len(expenses) >= 2
    amounts = [e.amount for e in expenses]
    assert Decimal("10.00") in amounts
    assert Decimal("20.00") in amounts


@pytest.mark.asyncio
async def test_delete_expense(session: AsyncSession, sample_user: User, sample_category: Category):
    expense = await add_expense(
        session, sample_user.id, sample_category.id, Decimal("15.00"), "Snack"
    )
    result = await delete_expense(session, expense.id, sample_user.id)
    assert result is True

    result = await delete_expense(session, 99999, sample_user.id)
    assert result is False


@pytest.mark.asyncio
async def test_get_monthly_total(session: AsyncSession, sample_user: User, sample_category: Category):
    await add_expense(session, sample_user.id, sample_category.id, Decimal("100.00"))
    await add_expense(session, sample_user.id, sample_category.id, Decimal("50.00"))

    now = datetime.utcnow()
    total = await get_monthly_total(session, sample_user.id, now.year, now.month)
    assert total >= Decimal("150.00")
