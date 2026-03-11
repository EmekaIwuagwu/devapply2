from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.backend.models.strategy import Strategy
from app.backend.schemas.strategy import StrategyCreate, StrategyUpdate
import uuid
from typing import List


async def get_strategies(db: AsyncSession, user_id: uuid.UUID) -> List[Strategy]:
    result = await db.execute(select(Strategy).where(Strategy.user_id == user_id))
    return result.scalars().all()


async def get_strategy(
    db: AsyncSession, strategy_id: uuid.UUID, user_id: uuid.UUID
) -> Strategy:
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id, Strategy.user_id == user_id)
    )
    return result.scalars().first()


async def create_strategy(
    db: AsyncSession, strategy: StrategyCreate, user_id: uuid.UUID
) -> Strategy:
    db_strategy = Strategy(**strategy.dict(), user_id=user_id)
    db.add(db_strategy)
    await db.commit()
    await db.refresh(db_strategy)
    return db_strategy


async def update_strategy(
    db: AsyncSession,
    strategy_id: uuid.UUID,
    strategy_update: StrategyUpdate,
    user_id: uuid.UUID,
) -> Strategy:
    db_strategy = await get_strategy(db, strategy_id, user_id)
    if not db_strategy:
        return None

    update_data = strategy_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_strategy, key, value)

    await db.commit()
    await db.refresh(db_strategy)
    return db_strategy


async def delete_strategy(
    db: AsyncSession, strategy_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    db_strategy = await get_strategy(db, strategy_id, user_id)
    if not db_strategy:
        return False

    await db.delete(db_strategy)
    await db.commit()
    return True
