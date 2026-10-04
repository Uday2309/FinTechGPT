from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Budget, User
from ..schemas import BudgetIn, BudgetOut
from ..services.analytics import affordability, budget_status

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetOut])
def list_budgets(month: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Budget).where(Budget.user_id == user.id)
    if month:
        stmt = stmt.where(Budget.month == month)
    return db.scalars(stmt.order_by(Budget.month.desc(), Budget.category)).all()


@router.post("", response_model=BudgetOut)
def upsert_budget(payload: BudgetIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.scalar(select(Budget).where(Budget.user_id == user.id, Budget.month == payload.month, Budget.category == payload.category))
    if existing:
        existing.amount = payload.amount
        db.commit()
        db.refresh(existing)
        return existing
    obj = Budget(user_id=user.id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/status")
def get_budget_status(month: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return budget_status(db, user.id, month)


@router.get("/affordability")
def affordability_endpoint(amount: float, category: str = "Shopping", month: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from decimal import Decimal
    return affordability(db, user.id, Decimal(str(amount)), category, month)
