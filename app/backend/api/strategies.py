from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse
from app.backend.services.auth_service import get_current_user
from app.backend.services import strategy_service
from app.backend.database.connection import get_db
from app.backend.models.user import User

router = APIRouter()


@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await strategy_service.create_strategy(db, strategy, current_user.id)


@router.get("/", response_model=List[StrategyResponse])
async def list_strategies(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await strategy_service.get_strategies(db, current_user.id)


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = await strategy_service.get_strategy(db, strategy_id, current_user.id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: uuid.UUID,
    strategy: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = await strategy_service.update_strategy(
        db, strategy_id, strategy, current_user.id
    )
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = await strategy_service.delete_strategy(db, strategy_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "Strategy deleted successfully"}


@router.post("/{strategy_id}/activate")
async def activate_strategy(
    strategy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # deactivate others first
    strategies = await strategy_service.get_strategies(db, current_user.id)
    for s in strategies:
        s.is_active = s.id == str(strategy_id)
    await db.commit()
    return {"message": f"Strategy {strategy_id} activated"}
