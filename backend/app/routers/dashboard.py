from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..services.analytics import dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(month: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return dashboard(db, user.id, month)
