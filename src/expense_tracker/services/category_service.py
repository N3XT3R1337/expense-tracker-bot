from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.expense import Category


async def get_categories(session: AsyncSession, user_id: int) -> list[Category]:
    stmt = select(Category).where(Category.user_id == user_id).order_by(Category.name)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_category_by_id(session: AsyncSession, category_id: int) -> Category | None:
    stmt = select(Category).where(Category.id == category_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_category(session: AsyncSession, user_id: int, name: str, emoji: str = "📦") -> Category:
    category = Category(user_id=user_id, name=name, emoji=emoji)
    session.add(category)
    await session.commit()
    return category


async def delete_category(session: AsyncSession, category_id: int) -> bool:
    category = await get_category_by_id(session, category_id)
    if not category:
        return False
    await session.delete(category)
    await session.commit()
    return True


async def update_category(session: AsyncSession, category_id: int, name: str | None = None, emoji: str | None = None) -> Category | None:
    category = await get_category_by_id(session, category_id)
    if not category:
        return None
    if name:
        category.name = name
    if emoji:
        category.emoji = emoji
    await session.commit()
    return category
