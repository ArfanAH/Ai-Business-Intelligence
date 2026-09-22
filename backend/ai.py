import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv("backend/.env")


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


DATABASE_SCHEMA = """
Database: PostgreSQL

Tables:

customers
- customer_id INTEGER PRIMARY KEY
- name VARCHAR
- city VARCHAR
- phone VARCHAR
- registration_date DATE

products
- product_id INTEGER PRIMARY KEY
- product_name VARCHAR
- category VARCHAR
- unit_price NUMERIC
- stock_quantity INTEGER

orders
- order_id INTEGER PRIMARY KEY
- customer_id INTEGER
- order_date DATE
- city VARCHAR
- total_amount NUMERIC

order_items
- order_item_id INTEGER PRIMARY KEY
- order_id INTEGER
- product_id INTEGER
- quantity INTEGER
- unit_price NUMERIC

employees
- employee_id INTEGER PRIMARY KEY
- name VARCHAR
- department VARCHAR
- salary NUMERIC
- joining_date DATE

expenses
- expense_id INTEGER PRIMARY KEY
- category VARCHAR
- amount NUMERIC
- expense_date DATE
- department VARCHAR

inventory
- inventory_id INTEGER PRIMARY KEY
- product_id INTEGER
- quantity INTEGER
- last_updated DATE
"""


def generate_sql(question: str, conversation: list[dict] = None) -> str:
    if conversation is None:
        conversation = []
    prompt = f"""
You are an expert PostgreSQL Business Intelligence SQL generator.

Your task is to convert the user's natural language business question
into ONE PostgreSQL SELECT query.

DATABASE SCHEMA:
{DATABASE_SCHEMA}

RULES:

1. Return ONLY SQL.
2. Generate only SELECT statements.
3. Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE,
   CREATE, GRANT, REVOKE, or other data-modifying statements.
4. Do not use multiple SQL statements.
5. Use only tables and columns from the provided schema.
6. Use PostgreSQL syntax.
7. Do not include markdown code fences.
8. Do not explain the query.
9. Use appropriate JOINs when information comes from multiple tables.

CONVERSATION HISTORY:
{conversation}

Use this history to understand references such as:
- "it"
- "that product"
- "the previous result"
- "how much did it sell?"
- "show me more details"

USER QUESTION:
{question}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You generate safe PostgreSQL SELECT queries for business analytics."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()

    return sql
def generate_insight(question: str, columns: list, data: list) -> str:
    prompt = f"""
You are a business intelligence analyst.

Analyze the database result below and provide a short, useful business insight.

USER QUESTION:
{question}

COLUMNS:
{columns}

DATA:
{data}

RULES:
1. Give a concise business insight in 1-3 sentences.
2. Mention important numbers when relevant.
3. Do not invent information.
4. Only use information present in the provided data.
5. Do not generate SQL.
6. Do not mention technical implementation details.
7. Use the conversation history when the current question refers to a previous result.
8. If the current question is independent, ignore the conversation history.
9. Do not invent missing information.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a concise business intelligence analyst."
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()

def generate_chart_config(question: str, columns: list[str], data: list[dict]):
    prompt = f"""
You are a business intelligence chart selection assistant.

USER QUESTION:
{question}

QUERY RESULT COLUMNS:
{columns}

QUERY RESULT DATA:
{data}

Choose the most appropriate visualization for this result.

Allowed chart types:
- "bar" for category comparisons, rankings, and discrete values
- "line" for time-based trends or ordered progression
- "pie" for part-to-whole proportions or shares
- "scatter" for relationships between two numeric variables
- "kpi" for a single important numeric value

Return ONLY valid JSON in this exact format:

{{
    "chart_type": "bar",
    "x_column": "column_name",
    "y_column": "column_name",
    "title": "Chart title",
    "orientation": "vertical"
}}

Rules:
1. Use only columns that exist in the query result.
2. Do not invent column names.
3. If there is only one row with one numeric value, use "kpi".
4. Use "line" when the result represents a time trend.
5. Use "pie" only when the values represent parts of one meaningful whole.
6. Use "bar" for category comparisons or rankings.
7. Use "scatter" only when both X and Y are numeric and their relationship is meaningful.
8. For "kpi", x_column and y_column can be the same numeric column.
9. Use "horizontal" orientation for bar charts when there are many categories
   or when category labels are long.
10. Use "vertical" orientation for bar charts when there are only a few
    short category labels.
11. For line, pie, scatter, and kpi charts, always use "vertical".
12. The orientation must be either "horizontal" or "vertical".
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    import json

    return json.loads(content)