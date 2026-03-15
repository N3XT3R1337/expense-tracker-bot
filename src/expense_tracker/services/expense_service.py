from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.expense import Budget, Category, Expense


async def add_expense(
    session: AsyncSession,
    user_id: int,
    category_id: int,
    amount: Decimal,
    description: str | None = None,
) -> Expense:
    expense = Expense(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        description=description,
    )
    session.add(expense)
    await session.commit()
    return expense


async def get_expenses(
    session: AsyncSession,
    user_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    category_id: int | None = None,
    limit: int = 50,
) -> list[Expense]:
    stmt = (
        select(Expense)
        .options(joinedload(Expense.category))
        .where(Expense.user_id == user_id)
    )
    if start_date:
        stmt = stmt.where(Expense.created_at >= start_date)
    if end_date:
        stmt = stmt.where(Expense.created_at <= end_date)
    if category_id:
        stmt = stmt.where(Expense.category_id == category_id)
    stmt = stmt.order_by(Expense.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def delete_expense(session: AsyncSession, expense_id: int, user_id: int) -> bool:
    stmt = select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
    result = await session.execute(stmt)
    expense = result.scalar_one_or_none()
    if not expense:
        return False
    await session.delete(expense)
    await session.commit()
    return True


async def get_monthly_total(session: AsyncSession, user_id: int, year: int, month: int) -> Decimal:
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    stmt = (
        select(func.coalesce(func.sum(Expense.amount), 0))
        .where(Expense.user_id == user_id)
        .where(Expense.created_at >= start)
        .where(Expense.created_at < end)
    )
    result = await session.execute(stmt)
    return Decimal(str(result.scalar()))


async def get_monthly_by_category(
    session: AsyncSession, user_id: int, year: int, month: int
) -> list[tuple[str, str, Decimal]]:
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    stmt = (
        select(
            Category.name,
            Category.emoji,
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .join(Category, Expense.category_id == Category.id)
        .where(Expense.user_id == user_id)
        .where(Expense.created_at >= start)
        .where(Expense.created_at < end)
        .group_by(Category.name, Category.emoji)
        .order_by(func.sum(Expense.amount).desc())
    )
    result = await session.execute(stmt)
    return [(row[0], row[1], Decimal(str(row[2]))) for row in result.all()]


async def get_daily_totals(
    session: AsyncSession, user_id: int, year: int, month: int
) -> list[tuple[int, Decimal]]:
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    stmt = (
        select(
            func.extract("day", Expense.created_at).label("day"),
            func.sum(Expense.amount).label("total"),
        )
        .where(Expense.user_id == user_id)
        .where(Expense.created_at >= start)
        .where(Expense.created_at < end)
        .group_by(func.extract("day", Expense.created_at))
        .order_by(func.extract("day", Expense.created_at))
    )
    result = await session.execute(stmt)
    return [(int(row[0]), Decimal(str(row[1]))) for row in result.all()]
