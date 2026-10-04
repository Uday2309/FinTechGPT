from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthRegister(BaseModel):
    email: str
    password: str = Field(min_length=8)


class AuthLogin(BaseModel):
    email: str
    password: str


class TransactionIn(BaseModel):
    transaction_date: date
    description: str
    amount: Decimal
    transaction_type: str
    category: str
    account: str = "Main"
    merchant: str | None = None
    notes: str | None = None


class TransactionOut(TransactionIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BudgetIn(BaseModel):
    month: str
    category: str
    amount: Decimal


class BudgetOut(BudgetIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


class InvestmentIn(BaseModel):
    asset_type: str
    symbol: str | None = None
    name: str
    units: Decimal | None = None
    avg_cost: Decimal | None = None
    current_price: Decimal | None = None
    invested_amount: Decimal = 0
    current_value: Decimal = 0


class InvestmentOut(InvestmentIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


class InvestmentCashflowIn(BaseModel):
    flow_date: date
    amount: Decimal
    note: str | None = None

class AffordabilityRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    category: str = "Shopping"
    month: str | None = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    tool_trace: list[str] = []
