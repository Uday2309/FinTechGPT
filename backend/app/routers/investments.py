from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Investment, InvestmentCashflow, User
from ..schemas import InvestmentCashflowIn, InvestmentIn, InvestmentOut
from ..services.analytics import portfolio_summary, portfolio_xirr
from ..services.market import get_stock_quote

router = APIRouter(prefix="/investments", tags=["investments"])


@router.get("", response_model=list[InvestmentOut])
def list_investments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Investment).where(Investment.user_id == user.id).order_by(Investment.asset_type, Investment.name)).all()


@router.post("", response_model=InvestmentOut)
def create_investment(payload: InvestmentIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    obj = Investment(user_id=user.id, **payload.model_dump())
    if obj.current_price is not None and obj.units is not None:
        obj.current_value = obj.current_price * obj.units
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/summary")
def summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {**portfolio_summary(db, user.id), "xirr_pct": portfolio_xirr(db, user.id)}


@router.get("/quote/{symbol}")
def quote(symbol: str, user: User = Depends(get_current_user)):
    return get_stock_quote(symbol)


@router.post("/{investment_id}/cashflow")
def add_cashflow(investment_id: int, payload: InvestmentCashflowIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    investment = db.scalar(select(Investment).where(Investment.id == investment_id, Investment.user_id == user.id))
    if not investment:
        return {"error": "Investment not found"}
    flow = InvestmentCashflow(user_id=user.id, investment_id=investment_id, **payload.model_dump())
    db.add(flow)
    db.commit()
    return {"id": flow.id, "status": "recorded"}


@router.get("/analytics/xirr")
def xirr_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"xirr_pct": portfolio_xirr(db, user.id)}
