import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.expense_tracker.models.base import Base
from src.expense_tracker.models.expense import Budget, Category, Expense, User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as sess:
        yield sess


@pytest_asyncio.fixture
async def sample_user(session: AsyncSession) -> User:
    user = User(telegram_id=123456789, username="testuser", first_name="Test")
    session.add(user)
    await session.flush()
    return user


@pytest_asyncio.fixture
async def sample_category(session: AsyncSession, sample_user: User) -> Category:
    cat = Category(user_id=sample_user.id, name="Food", emoji="🍔")
    session.add(cat)
    await session.flush()
    return cat
