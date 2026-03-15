from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.expense_tracker.models.expense import Category, User
from src.expense_tracker.services.budget_service import (
    delete_budget,
    get_budget_for_category,
    get_budgets,
    set_budget,
)


@pytest.mark.asyncio
async def test_set_budget(session: AsyncSession, sample_user: User, sample_category: Category):
    budget = await set_budget(session, sample_user.id, sample_category.id, Decimal("500.00"))
    assert budget.monthly_limit == Decimal("500.00")
    assert budget.user_id == sample_user.id
    assert budget.category_id == sample_category.id


@pytest.mark.asyncio
async def test_update_budget(session: AsyncSession, sample_user: User, sample_category: Category):
    await set_budget(session, sample_user.id, sample_category.id, Decimal("500.00"))
    updated = await set_budget(session, sample_user.id, sample_category.id, Decimal("750.00"))
    assert updated.monthly_limit == Decimal("750.00")


@pytest.mark.asyncio
async def test_delete_budget(session: AsyncSession, sample_user: User, sample_category: Category):
    await set_budget(session, sample_user.id, sample_category.id, Decimal("300.00"))
    result = await delete_budget(session, sample_user.id, sample_category.id)
    assert result is True

    budget = await get_budget_for_category(session, sample_user.id, sample_category.id)
    assert budget is None
