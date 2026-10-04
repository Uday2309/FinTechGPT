from datetime import date
from decimal import Decimal
from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Budget, Investment, Transaction, User

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    user = db.query(User).filter(User.email == "demo@fintechgpt.local").first()
    if not user:
        user = User(email="demo@fintechgpt.local", password_hash=hash_password("Demo@12345"))
        db.add(user)
        db.commit()
        db.refresh(user)

    if not db.query(Transaction).filter(Transaction.user_id == user.id).first():
        rows = [
            (date(2026, 9, 1), "Salary", 50000, "income", "Salary"),
            (date(2026, 9, 2), "Rent", 12000, "expense", "Housing"),
            (date(2026, 9, 4), "Grocery Store", 3200, "expense", "Food"),
            (date(2026, 9, 5), "Metro Recharge", 800, "expense", "Travel"),
            (date(2026, 9, 8), "Netflix", 649, "expense", "Subscriptions"),
            (date(2026, 9, 10), "Amazon", 1800, "expense", "Shopping"),
        ]
        for d, desc, amount, typ, cat in rows:
            db.add(Transaction(user_id=user.id, transaction_date=d, description=desc, amount=Decimal(amount), transaction_type=typ, category=cat, account="Demo"))

    for cat, amount in [("Food", 5000), ("Travel", 3000), ("Shopping", 4000), ("Subscriptions", 1500), ("Housing", 12000)]:
        if not db.query(Budget).filter(Budget.user_id == user.id, Budget.month == "2026-09", Budget.category == cat).first():
            db.add(Budget(user_id=user.id, month="2026-09", category=cat, amount=Decimal(amount)))

    if not db.query(Investment).filter(Investment.user_id == user.id).first():
        db.add(Investment(user_id=user.id, asset_type="stock", symbol="RELIANCE.NS", name="Reliance Industries", units=Decimal("10"), avg_cost=Decimal("2500"), current_price=Decimal("2900"), invested_amount=Decimal("25000"), current_value=Decimal("29000")))
        db.add(Investment(user_id=user.id, asset_type="mutual_fund", symbol="DEMO-MF", name="Demo Flexi Cap Fund", units=Decimal("100"), avg_cost=Decimal("150"), current_price=Decimal("168"), invested_amount=Decimal("15000"), current_value=Decimal("16800")))

    db.commit()
    print("Demo data ready. Login: demo@fintechgpt.local / Demo@12345")
finally:
    db.close()
