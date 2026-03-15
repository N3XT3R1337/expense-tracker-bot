from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.expense_tracker.models.expense import Category, User
from src.expense_tracker.services.category_service import (
    create_category,
    delete_category,
    get_categories,
    update_category,
)


@pytest.mark.asyncio
async def test_create_category(session: AsyncSession, sample_user: User):
    cat = await create_category(session, sample_user.id, "Transport", "🚗")
    assert cat.id is not None
    assert cat.name == "Transport"
    assert cat.emoji == "🚗"


@pytest.mark.asyncio
async def test_get_categories(session: AsyncSession, sample_user: User, sample_category: Category):
    cats = await get_categories(session, sample_user.id)
    assert len(cats) >= 1
    names = [c.name for c in cats]
    assert "Food" in names


@pytest.mark.asyncio
async def test_delete_category(session: AsyncSession, sample_user: User):
    cat = await create_category(session, sample_user.id, "Temp", "🗑")
    result = await delete_category(session, cat.id)
    assert result is True

    result = await delete_category(session, 99999)
    assert result is False


@pytest.mark.asyncio
async def test_update_category(session: AsyncSession, sample_user: User):
    cat = await create_category(session, sample_user.id, "Old Name", "📦")
    updated = await update_category(session, cat.id, name="New Name", emoji="🎯")
    assert updated.name == "New Name"
    assert updated.emoji == "🎯"
