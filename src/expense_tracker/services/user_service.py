from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.expense import Category, User

DEFAULT_CATEGORIES = [
    ("🍔", "Food"),
    ("🚗", "Transport"),
    ("🏠", "Housing"),
    ("🎮", "Entertainment"),
    ("🛒", "Shopping"),
    ("💊", "Health"),
    ("📚", "Education"),
    ("💡", "Utilities"),
    ("👔", "Clothing"),
    ("✈️", "Travel"),
]


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: str | None = None, first_name: str | None = None
) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        if username and user.username != username:
            user.username = username
        if first_name and user.first_name != first_name:
            user.first_name = first_name
        await session.commit()
        return user
    user = User(telegram_id=telegram_id, username=username, first_name=first_name)
    session.add(user)
    await session.flush()
    for emoji, name in DEFAULT_CATEGORIES:
        category = Category(user_id=user.id, name=name, emoji=emoji)
        session.add(category)
    await session.commit()
    return user


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
