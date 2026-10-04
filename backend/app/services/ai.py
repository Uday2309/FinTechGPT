from sqlalchemy.orm import Session
from .analytics import affordability, budget_status, dashboard, portfolio_summary, recurring_expenses
from .rag import search as rag_search
from ..config import settings
from ..models import Transaction
from google import genai
from google.genai import types

client = genai.Client(api_key=settings.gemini_api_key)


def get_spending_summary(month: str) -> dict:
    """
    Get income, expenses, savings rate and category-level spending for a month.

    Args:
        month: Month in YYYY-MM format.
    """
    return _runtime.db_tools.dashboard(month)


def get_budget_status(month: str) -> list:
    """
    Get budget versus actual spending by category for a month.

    Args:
        month: Month in YYYY-MM format.
    """
    return _runtime.db_tools.budget_status(month)


def get_portfolio_summary() -> dict:
    """Get total invested amount, current value, return and asset allocation."""
    return _runtime.db_tools.portfolio_summary()


def search_financial_documents(query: str) -> list:
    """
    Search the user's uploaded financial documents for supporting context.

    Args:
        query: Search question or keywords.
    """
    return rag_search(query, _runtime.user_id, 5)


def can_afford_purchase(
    amount: float,
    category: str = "Shopping",
    month: str | None = None,
) -> dict:
    """Test a proposed purchase against current cash flow and an optional category budget.

    Args:
        amount: Proposed purchase amount.
        category: Spending category for the purchase.
        month: Month in YYYY-MM format; defaults to the current month.
    """
    from decimal import Decimal

    return affordability(
        _runtime.db_tools.db,
        _runtime.user_id,
        Decimal(str(amount)),
        category,
        month,
    )


def find_recurring_expenses() -> list:
    """Find repeated expense descriptions that appear in at least two months."""
    return recurring_expenses(_runtime.db_tools.db, _runtime.user_id)


class Runtime:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.db_tools = DBTools(db, user_id)


class DBTools:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def dashboard(self, month: str):
        return dashboard(self.db, self.user_id, month)

    def budget_status(self, month: str):
        return budget_status(self.db, self.user_id, month)

    def portfolio_summary(self):
        return portfolio_summary(self.db, self.user_id)


_runtime: Runtime


def answer_question(db: Session, user_id: int, message: str):
    global _runtime

    _runtime = Runtime(db, user_id)
    tool_trace = []

    system ="""You are FinTechGPT, a personal finance data assistant.

Use tools for factual calculations about the user's stored finances. Never invent numbers.

Use the minimum number of tools necessary to answer the user's question.
Do not call unrelated tools.
For a spending question, use get_spending_summary.
For a budget question, use get_budget_status.
For a portfolio question, use get_portfolio_summary.
For uploaded-document questions, use search_financial_documents.
For affordability questions, use can_afford_purchase.
For recurring-expense questions, use find_recurring_expenses.

Do not repeat the same tool unless the result is genuinely insufficient.

All monetary amounts in the user's financial data are in Indian Rupees (INR).
Always display INR amounts using ₹.
Never use $, USD, €, or other currency symbols unless the user's stored data explicitly uses that currency.

Do not provide regulated financial advice or tell the user what investment to buy or sell.
You may explain patterns, arithmetic, budgeting scenarios and document facts.
Be concise, show calculations where useful, and state when data is missing.
""" 

    tools = [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="get_spending_summary",
                    description="Get income, expenses, savings rate and category-level spending for a month.",
                    parameters_json_schema={
                        "type": "object",
                        "properties": {
                            "month": {
                                "type": "string",
                                "description": "Month in YYYY-MM format."
                            }
                        },
                        "required": ["month"]
                    }
                ),
                types.FunctionDeclaration(
                    name="get_budget_status",
                    description="Get budget versus actual spending by category for a month.",
                    parameters_json_schema={
                        "type": "object",
                        "properties": {
                            "month": {
                                "type": "string",
                                "description": "Month in YYYY-MM format."
                            }
                        },
                        "required": ["month"]
                    }
                ),
                types.FunctionDeclaration(
                    name="get_portfolio_summary",
                    description="Get total invested amount, current value, return and asset allocation.",
                    parameters_json_schema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.FunctionDeclaration(
                    name="search_financial_documents",
                    description="Search the user's uploaded financial documents for supporting context.",
                    parameters_json_schema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search question or keywords."
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.FunctionDeclaration(
                    name="can_afford_purchase",
                    description="Test a proposed purchase against current cash flow and an optional category budget.",
                    parameters_json_schema={
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "Proposed purchase amount."
                            },
                            "category": {
                                "type": "string",
                                "description": "Spending category for the purchase."
                            },
                            "month": {
                                "type": "string",
                                "description": "Month in YYYY-MM format; defaults to the current month."
                            }
                        },
                        "required": ["amount"]
                    }
                ),
                types.FunctionDeclaration(
                    name="find_recurring_expenses",
                    description="Find repeated expense descriptions that appear in at least two months.",
                    parameters_json_schema={
                        "type": "object",
                        "properties": {}
                    }
                ),
            ]
        )
    ]

   

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"{system}\n\nUser: {message}"
                )
            ],
        )
    ]

    while True:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=tools
            ),
        )

        function_calls = []

        for part in response.candidates[0].content.parts:
            if part.function_call:
                function_calls.append(part.function_call)

        if not function_calls:
            return (
                response.text or "I was unable to generate a response.",
                tool_trace,
            )

        contents.append(response.candidates[0].content)

        function_response_parts = []

        for function_call in function_calls:
            name = function_call.name
            args = dict(function_call.args or {})

            tool_trace.append(name)

            if name == "get_spending_summary":
                result = get_spending_summary(**args)

            elif name == "get_budget_status":
                result = get_budget_status(**args)

            elif name == "get_portfolio_summary":
                result = get_portfolio_summary()

            elif name == "search_financial_documents":
                result = search_financial_documents(**args)

            elif name == "can_afford_purchase":
                result = can_afford_purchase(**args)

            elif name == "find_recurring_expenses":
                result = find_recurring_expenses()

            else:
                result = {"error": "Unknown tool"}

            function_response_parts.append(
                types.Part.from_function_response(
                    name=name,
                    response={"result": result},
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=function_response_parts,
            )
        )