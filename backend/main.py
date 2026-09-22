from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.ai import generate_sql, generate_insight
from backend.sql_validator import validate_sql
from backend.query_executor import execute_query
from backend.database import get_connection
from fastapi.security import OAuth2PasswordRequestForm
from backend.ai import (
    generate_sql,
    generate_insight,
    generate_chart_config,
)
from backend.auth import (create_access_token, 
                          get_password_hash, 
                          verify_password,
                          get_current_user,
                          )

class AskRequest(BaseModel):
    question: str
    conversation: list[dict] = []


app = FastAPI(
    title="AI Business Intelligence Assistant",
    description="AI-powered Business Intelligence backend",
    version="1.0.0",
)
DEMO_USER = {
    "username": "admin",
    "password_hash": get_password_hash("admin123")
}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Business Intelligence Assistant API is running"
    }


@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != DEMO_USER["username"]:
        return {
            "success": False,
            "error": "Invalid username or password"
        }

    if not verify_password(
        form_data.password,
        DEMO_USER["password_hash"]
    ):
        return {
            "success": False,
            "error": "Invalid username or password"
        }

    token = create_access_token({
        "sub": form_data.username
    })

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/api/health")
def health_check():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

        return {
            "status": "healthy",
            "database": "connected",
            "test": result[0],
        }

    except Exception as e:

        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


@app.get("/api/customers")
def get_customers(limit: int = 20):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        customer_id,
                        name,
                        city,
                        phone,
                        registration_date
                    FROM customers
                    ORDER BY customer_id
                    LIMIT %s
                """, (limit,))

                rows = cursor.fetchall()

                columns = [
                    "customer_id",
                    "name",
                    "city",
                    "phone",
                    "registration_date",
                ]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/api/products")
def get_products(limit: int = 20):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        product_id,
                        product_name,
                        category,
                        unit_price,
                        stock_quantity
                    FROM products
                    ORDER BY product_id
                    LIMIT %s
                """, (limit,))

                rows = cursor.fetchall()

                columns = [
                    "product_id",
                    "product_name",
                    "category",
                    "unit_price",
                    "stock_quantity",
                ]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/orders")
def get_orders(limit: int = 20):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        order_id,
                        customer_id,
                        order_date,
                        city,
                        total_amount
                    FROM orders
                    ORDER BY order_date DESC
                    LIMIT %s
                """, (limit,))

                rows = cursor.fetchall()

                columns = [
                    "order_id",
                    "customer_id",
                    "order_date",
                    "city",
                    "total_amount",
                ]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.get("/api/analytics/summary")
def sales_summary():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                # Total sales
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0)
                    FROM orders
                """)
                total_sales = cursor.fetchone()[0]

                # Total orders
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM orders
                """)
                total_orders = cursor.fetchone()[0]

                # Average order value
                cursor.execute("""
                    SELECT COALESCE(AVG(total_amount), 0)
                    FROM orders
                """)
                average_order_value = cursor.fetchone()[0]

                # Total customers
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM customers
                """)
                total_customers = cursor.fetchone()[0]

                # Total expenses
                cursor.execute("""
                    SELECT COALESCE(SUM(amount), 0)
                    FROM expenses
                """)
                total_expenses = cursor.fetchone()[0]

                # Total profit approximation
                total_profit = total_sales - total_expenses

                return {
                    "total_sales": float(total_sales),
                    "total_orders": total_orders,
                    "average_order_value": float(average_order_value),
                    "total_customers": total_customers,
                    "total_expenses": float(total_expenses),
                    "sales_minus_expenses": float(total_profit),
                }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/analytics/monthly-sales")
def monthly_sales():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        DATE_TRUNC('month', order_date)::date AS month,
                        SUM(total_amount) AS sales,
                        COUNT(*) AS orders
                    FROM orders
                    GROUP BY DATE_TRUNC('month', order_date)
                    ORDER BY month
                """)

                rows = cursor.fetchall()

                return [
                    {
                        "month": row[0].isoformat(),
                        "sales": float(row[1]),
                        "orders": row[2],
                    }
                    for row in rows
                ]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.post("/api/ask")
def ask_business_question(request: AskRequest,
    current_user: str = Depends(get_current_user)):

    # 1. Generate SQL using AI
    generated_sql = generate_sql(request.question,request.conversation)

    # 2. Validate the generated SQL
    is_valid, validation_result = validate_sql(generated_sql)

    if not is_valid:
        return {
            "success": False,
            "question": request.question,
            "sql": generated_sql,
            "error": validation_result
        }

    # 3. Execute validated SQL
    try:
        columns, rows = execute_query(validation_result)

        data = [
            dict(zip(columns, row))
            for row in rows
        ]

        insight = generate_insight(
            request.question,
            columns,
            data
        )
        chart_config = generate_chart_config(
            request.question,
            columns,
            data
        )

        return {
            "success": True,
            "question": request.question,
            "sql": validation_result,
            "columns": columns,
            "data": data,
            "insight": insight,
            "chart_config": chart_config
        }

    except Exception as e:
        return {
            "success": False,
            "question": request.question,
            "sql": validation_result,
            "error": str(e)
        }