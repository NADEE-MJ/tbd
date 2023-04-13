from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src import crud
from src.api import deps
from src.db.db import get_session
from src.models.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from src.models.user import User

router = APIRouter()


@router.get("/", response_model=list[BudgetResponse])
async def get_all_budgets(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all bank budgets for current user.
    """
    if current_user.id is not None:
        budgets = await crud.budget.get_all_budgets_for_user(db, user_id=current_user.id)

        return budgets


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get specific bank budget info for current user.
    """
    budget = await crud.budget.get(db, id=budget_id)
    if budget is None:
        raise HTTPException(status_code=404, detail="That budget does not exist.")

    if budget.user_id != current_user.id:
        raise HTTPException(status_code=401, detail="You are unauthorized to access this bank budget")
    return budget


@router.post("/", response_model=BudgetResponse)
async def create_budget(
    *,
    db: AsyncSession = Depends(get_session),
    budget_create: BudgetCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new bank budget. Must Be logged in first.
    """
    if current_user.id is not None:
        budgets = await crud.budget.get_all_budgets_for_user(db, user_id=current_user.id)

        if budgets is not None:
            for budget in budgets:
                if budget.name == budget_create.name:
                    raise HTTPException(
                        status_code=400,
                        detail="An budget with the name already exists in the system.",
                    )

        budget = await crud.budget.create(db, obj_in=budget_create, user_id=current_user.id)

        return budget


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an existing bank budget. Must be logged in first.
    """
    budget_from_db = await crud.budget.get(db, id=budget_id)

    if budget_from_db is None:
        raise HTTPException(status_code=404, detail="That budget does not exist.")

    if budget_from_db.user_id != current_user.id:
        raise HTTPException(status_code=401, detail="You are unauthorized to update this bank budget")

    budgets = await crud.budget.get_all_budgets_for_user(db, user_id=current_user.id)

    if budgets is not None:
        for budget in budgets:
            if budget.name == budget_update.name:
                raise HTTPException(
                    status_code=400,
                    detail="An budget with the name already exists in the system.",
                )

    budget = await crud.budget.update(db, db_obj=budget_from_db, obj_in=budget_update)

    return budget


@router.delete("/{budget_id}", response_model=BudgetResponse)
async def remove_budget(
    budget_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove an existing bank budget. Must be logged in first.
    """
    budget = await crud.budget.get(db, id=budget_id)

    if budget is None:
        raise HTTPException(status_code=404, detail="That budget does not exist.")

    if budget.user_id != current_user.id:
        raise HTTPException(status_code=401, detail="You are unauthorized to remove this bank budget")

    budget = await crud.budget.remove(db, id=budget_id)

    return budget
