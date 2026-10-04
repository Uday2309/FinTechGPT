from collections import defaultdict
from datetime import date
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..models import Budget, Investment, InvestmentCashflow, Transaction
from .xirr import xirr


def month_key(d: date) -> str:
    return d.strftime("%Y-%m")


def dashboard(db: Session, user_id: int, month: str | None = None):
    target = month or date.today().strftime("%Y-%m")
    txs = db.scalars(select(Transaction).where(Transaction.user_id == user_id)).all()
    by_cat = defaultdict(Decimal)
    income = Decimal("0")
    expenses = Decimal("0")
    for tx in txs:
        if month_key(tx.transaction_date) != target:
            continue
        if tx.transaction_type == "income":
            income += tx.amount
        else:
            expenses += tx.amount
            by_cat[tx.category] += tx.amount

    prev_month_dt = date(int(target[:4]), int(target[5:7]), 1)
    if prev_month_dt.month == 1:
        prev = f"{prev_month_dt.year - 1}-12"
    else:
        prev = f"{prev_month_dt.year}-{prev_month_dt.month - 1:02d}"

    prev_by_cat = defaultdict(Decimal)
    for tx in txs:
        if month_key(tx.transaction_date) == prev and tx.transaction_type == "expense":
            prev_by_cat[tx.category] += tx.amount

    categories = sorted(set(by_cat) | set(prev_by_cat), key=lambda c: by_cat[c], reverse=True)
    category_breakdown = []
    for cat in categories:
        current = by_cat[cat]
        previous = prev_by_cat[cat]
        delta = current - previous
        pct = (delta / previous * 100) if previous else None
        category_breakdown.append({"category": cat, "current": float(current), "previous": float(previous), "delta": float(delta), "pct_change": float(pct) if pct is not None else None})

    investments = db.scalars(select(Investment).where(Investment.user_id == user_id)).all()
    invested = sum((i.invested_amount for i in investments), Decimal("0"))
    current_value = sum((i.current_value for i in investments), Decimal("0"))
    return {
        "month": target,
        "income": float(income),
        "expenses": float(expenses),
        "net_cash_flow": float(income - expenses),
        "savings_rate": float((income - expenses) / income * 100) if income else None,
        "category_breakdown": category_breakdown,
        "portfolio": {
            "invested": float(invested),
            "current_value": float(current_value),
            "profit_loss": float(current_value - invested),
            "return_pct": float((current_value - invested) / invested * 100) if invested else None,
        },
    }


def budget_status(db: Session, user_id: int, month: str):
    budgets = db.scalars(select(Budget).where(Budget.user_id == user_id, Budget.month == month)).all()
    txs = db.scalars(select(Transaction).where(Transaction.user_id == user_id)).all()
    actual = defaultdict(Decimal)
    for tx in txs:
        if tx.transaction_type == "expense" and month_key(tx.transaction_date) == month:
            actual[tx.category] += tx.amount
    rows = []
    for b in budgets:
        spent = actual[b.category]
        remaining = b.amount - spent
        rows.append({"category": b.category, "budget": float(b.amount), "spent": float(spent), "remaining": float(remaining), "utilization_pct": float(spent / b.amount * 100) if b.amount else None})
    return rows


def portfolio_summary(db: Session, user_id: int):
    investments = db.scalars(select(Investment).where(Investment.user_id == user_id)).all()
    invested = sum((i.invested_amount for i in investments), Decimal("0"))
    current = sum((i.current_value for i in investments), Decimal("0"))
    allocation = defaultdict(Decimal)
    rows = []
    for i in investments:
        allocation[i.asset_type] += i.current_value
        rows.append({"id": i.id, "asset_type": i.asset_type, "symbol": i.symbol, "name": i.name, "invested_amount": float(i.invested_amount), "current_value": float(i.current_value), "profit_loss": float(i.current_value - i.invested_amount), "return_pct": float((i.current_value - i.invested_amount) / i.invested_amount * 100) if i.invested_amount else None})
    allocation_out = [{"asset_type": k, "value": float(v), "pct": float(v / current * 100) if current else 0} for k, v in allocation.items()]
    return {"invested": float(invested), "current_value": float(current), "profit_loss": float(current - invested), "return_pct": float((current - invested) / invested * 100) if invested else None, "allocation": allocation_out, "holdings": rows}


def affordability(db: Session, user_id: int, amount: Decimal, category: str, month: str | None = None):
    target = month or date.today().strftime("%Y-%m")
    txs = db.scalars(select(Transaction).where(Transaction.user_id == user_id)).all()
    income = sum((tx.amount for tx in txs if tx.transaction_type == "income" and month_key(tx.transaction_date) == target), Decimal("0"))
    expenses = sum((tx.amount for tx in txs if tx.transaction_type == "expense" and month_key(tx.transaction_date) == target), Decimal("0"))
    category_spend = sum((tx.amount for tx in txs if tx.transaction_type == "expense" and tx.category.lower() == category.lower() and month_key(tx.transaction_date) == target), Decimal("0"))
    budget = db.scalar(select(Budget).where(Budget.user_id == user_id, Budget.month == target, func.lower(Budget.category) == category.lower()))
    available_cash = income - expenses
    projected_cash = available_cash - amount
    budget_remaining = (budget.amount - category_spend) if budget else None
    return {
        "month": target, "purchase_amount": float(amount), "category": category,
        "income": float(income), "expenses": float(expenses), "current_available_cash": float(available_cash),
        "projected_available_cash": float(projected_cash),
        "category_budget_remaining": float(budget_remaining) if budget_remaining is not None else None,
        "within_current_cashflow": projected_cash >= 0,
        "within_category_budget": (budget_remaining is None or amount <= budget_remaining),
    }


def recurring_expenses(db: Session, user_id: int):
    txs = db.scalars(select(Transaction).where(Transaction.user_id == user_id, Transaction.transaction_type == "expense")).all()
    grouped = defaultdict(list)
    for tx in txs:
        key = (tx.description.strip().lower(), tx.category.strip().lower(), tx.amount.quantize(Decimal("0.01")))
        grouped[key].append(tx.transaction_date)
    results = []
    for (description, category, amount), dates in grouped.items():
        months = {month_key(d) for d in dates}
        if len(months) >= 2:
            results.append({"description": description.title(), "category": category.title(), "amount": float(amount), "months_seen": sorted(months), "occurrences": len(dates)})
    return sorted(results, key=lambda x: (x["category"], -x["occurrences"]))


def portfolio_xirr(db: Session, user_id: int):
    investments = db.scalars(select(Investment).where(Investment.user_id == user_id)).all()
    flows = db.scalars(select(InvestmentCashflow).where(InvestmentCashflow.user_id == user_id).order_by(InvestmentCashflow.flow_date)).all()
    if not flows:
        return None
    by_id = defaultdict(list)
    for f in flows:
        by_id[f.investment_id].append(f)
    today = date.today()
    all_flows = [(f.flow_date, float(f.amount)) for f in flows]
    for inv in investments:
        if inv.current_value:
            all_flows.append((today, float(inv.current_value)))
    return (xirr(all_flows) * 100) if len(all_flows) >= 2 and xirr(all_flows) is not None else None
