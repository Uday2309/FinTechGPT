from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from .routers import auth, budgets, chat, dashboard, documents, investments, transactions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinTechGPT API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(investments.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"name": "FinTechGPT", "status": "ok", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
