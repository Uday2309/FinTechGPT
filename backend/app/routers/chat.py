from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import ChatMessage, User
from ..schemas import ChatRequest, ChatResponse
from ..services.ai import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_msg = ChatMessage(user_id=user.id, role="user", content=payload.message)
    db.add(user_msg)
    db.commit()
    answer, trace = answer_question(db, user.id, payload.message)
    db.add(ChatMessage(user_id=user.id, role="assistant", content=answer))
    db.commit()
    return ChatResponse(answer=answer, tool_trace=trace)
