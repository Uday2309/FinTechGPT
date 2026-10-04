from datetime import date
from decimal import Decimal
from io import StringIO
import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Transaction, User
from ..schemas import TransactionIn, TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Transaction).where(Transaction.user_id == user.id).order_by(Transaction.transaction_date.desc())).all()


@router.post("", response_model=TransactionOut)
def create_transaction(payload: TransactionIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tx = Transaction(user_id=user.id, **payload.model_dump())
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    raw = await file.read()
    df = pd.read_csv(StringIO(raw.decode("utf-8-sig")))
    required = {"date", "description", "amount", "type", "category"}
    missing = required - set(df.columns)
    if missing:
        return {"error": f"Missing columns: {sorted(missing)}", "expected": sorted(required)}
    created = 0
    for _, row in df.iterrows():
        tx = Transaction(
            user_id=user.id,
            transaction_date=pd.to_datetime(row["date"]).date(),
            description=str(row["description"]),
            amount=Decimal(str(abs(float(row["amount"])))),
            transaction_type=str(row["type"]).lower(),
            category=str(row["category"]),
            account=str(row.get("account", "Imported")),
            merchant=str(row.get("merchant")) if pd.notna(row.get("merchant")) else None,
            notes=str(row.get("notes")) if pd.notna(row.get("notes")) else None,
        )
        db.add(tx)
        created += 1
    db.commit()
    return {"created": created}
