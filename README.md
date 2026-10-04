# FinTechGPT — Personal AI Financial Assistant

A local-first personal finance platform built with React, FastAPI, PostgreSQL, ChromaDB and Ollama.

## What it includes

- Expense and income tracker with CSV import
- Category analytics and monthly comparisons
- Budget planning and “can I afford this?” calculations
- Investment dashboard for stocks, mutual funds, gold, FDs and cash
- Portfolio value, absolute return, allocation and XIRR
- Local AI chat powered by Ollama with database tools/function calling
- Financial document RAG for PDFs and CSVs
- Responsive React dashboard
- JWT authentication for the personal account
- No paid API required for the local AI stack

## Architecture

```text
React + Vite
     |
     v
FastAPI REST API
  |       |        \
  v       v         v
Postgres  ChromaDB  Ollama
          (RAG)     (LLM + embeddings)
```

## Requirements

- Windows 10/11
- Python 3.12 recommended
- Node.js 22 LTS (or Node 20.19+)
- PostgreSQL 17 or 18
- Ollama
- Git
- VS Code

## Quick start

### 1. Database

Create a PostgreSQL database named `fintechgpt` and a user/password you control.

Example in pgAdmin Query Tool:

```sql
CREATE DATABASE fintechgpt;
```

### 2. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` with your PostgreSQL password.

Run:

```powershell
python -m app.main
```

Backend docs: http://127.0.0.1:8000/docs

### 3. Ollama

Open a second PowerShell window:

```powershell
ollama pull qwen3:4b
ollama pull nomic-embed-text
```

Then confirm:

```powershell
ollama list
```

### 4. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints, usually http://localhost:5173.

## First login

Use the Register screen to create your local account. Nothing is sent to a paid AI service.

## Notes about financial data

This app is intended for personal tracking and calculations. Market data can be delayed or unavailable. AI output is an interface over your own stored data and should not be treated as regulated financial advice.
