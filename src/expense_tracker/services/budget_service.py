from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.expense import Budget, Category, Expense


async def set_budget(
    session: AsyncSession, user_id: int, category_id: int, monthly_limit: Decimal
) -> Budget:
    stmt = select(Budget).where(
        Budget.user_id == user_id, Budget.category_id == category_id
    )
    result = await session.execute(stmt)
    budget = result.scalar_one_or_none()
    if budget:
        budget.monthly_limit = monthly_limit
    else:
        budget = Budget(
            user_id=user_id, category_id=category_id, monthly_limit=monthly_limit
        )
        session.add(budget)
    await session.commit()
    return budget


async def get_budgets(session: AsyncSession, user_id: int) -> list[Budget]:
    stmt = (
        select(Budget)
        .options(joinedload(Budget.category))
        .where(Budget.user_id == user_id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_budget_for_category(
    session: AsyncSession, user_id: int, category_id: int
) -> Budget | None:
    stmt = select(Budget).where(
        Budget.user_id == user_id, Budget.category_id == category_id
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def delete_budget(session: AsyncSession, user_id: int, category_id: int) -> bool:
    budget = await get_budget_for_category(session, user_id, category_id)
    if not budget:
        return False
    await session.delete(budget)
    await session.commit()
    return True


async def check_budget_alerts(
    session: AsyncSession, user_id: int, threshold: float = 0.8
) -> list[tuple[str, Decimal, Decimal, float]]:
    now = datetime.utcnow()
    year, month = now.year, now.month
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)

    budgets = await get_budgets(session, user_id)
    alerts = []
    for budget in budgets:
        stmt = (
            select(func.coalesce(func.sum(Expense.amount), 0))
            .where(Expense.user_id == user_id)
            .where(Expense.category_id == budget.category_id)
            .where(Expense.created_at >= start)
            .where(Expense.created_at < end)
        )
        result = await session.execute(stmt)
        spent = Decimal(str(result.scalar()))
        if budget.monthly_limit > 0:
            ratio = float(spent / budget.monthly_limit)
            if ratio >= threshold:
                alerts.append(
                    (budget.category.name, spent, budget.monthly_limit, ratio)
                )
    return alerts
