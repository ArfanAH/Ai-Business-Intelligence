import sqlglot
from sqlglot import exp


ALLOWED_SCHEMA = {
    "customers": {
        "customer_id",
        "name",
        "city",
        "phone",
        "registration_date",
    },
    "products": {
        "product_id",
        "product_name",
        "category",
        "unit_price",
        "stock_quantity",
    },
    "orders": {
        "order_id",
        "customer_id",
        "order_date",
        "city",
        "total_amount",
    },
    "order_items": {
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
    },
    "employees": {
        "employee_id",
        "name",
        "department",
        "salary",
        "joining_date",
    },
    "expenses": {
        "expense_id",
        "category",
        "amount",
        "expense_date",
        "department",
    },
    "inventory": {
        "inventory_id",
        "product_id",
        "quantity",
        "last_updated",
    },
}


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate AI-generated PostgreSQL SQL.

    Checks:
    - SQL is not empty
    - exactly one statement
    - only SELECT is allowed
    - only approved tables are allowed
    - only approved columns are allowed
    - dangerous SQL operations are rejected
    """

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    # Remove accidental Markdown code fences
    sql = sql.strip()

    if sql.startswith("```"):
        sql = sql.replace("```sql", "", 1)
        sql = sql.replace("```", "")
        sql = sql.strip()

    # Parse SQL
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except Exception as e:
        return False, f"Invalid SQL syntax: {e}"

    # Only one statement
    if len(statements) != 1:
        return False, "Multiple SQL statements are not allowed."

    statement = statements[0]

    # Only SELECT
    if not isinstance(statement, exp.Select):
        return False, "Only SELECT queries are allowed."

    # ---------------------------------------------------------
    # 1. Check tables
    # ---------------------------------------------------------

    tables = statement.find_all(exp.Table)

    aliases = {}

    for table in tables:
        table_name = table.name.lower()

        if table_name not in ALLOWED_SCHEMA:
            return False, f"Access to table '{table_name}' is not allowed."

        # Store table aliases
        alias = table.alias

        if alias:
            aliases[alias.lower()] = table_name
        else:
            aliases[table_name] = table_name

    # ---------------------------------------------------------
    # 2. Collect SELECT aliases
    # ---------------------------------------------------------

    select_aliases = set()

    for expression in statement.expressions:
        if isinstance(expression, exp.Alias):
            select_aliases.add(expression.alias.lower())

    # ---------------------------------------------------------
    # 3. Check columns
    # ---------------------------------------------------------

    for column in statement.find_all(exp.Column):

        column_name = column.name.lower()
        table_qualifier = column.table.lower() if column.table else None

        # Allow references to aliases created in SELECT
        # Example: ORDER BY total_sales
        if not table_qualifier and column_name in select_aliases:
            continue

        # Qualified column: p.product_name
        if table_qualifier:

            if table_qualifier not in aliases:
                return False, (
                    f"Unknown table or alias '{table_qualifier}'."
                )

            real_table = aliases[table_qualifier]

            if column_name not in ALLOWED_SCHEMA[real_table]:
                return False, (
                    f"Column '{column_name}' is not allowed "
                    f"for table '{real_table}'."
                )

        # Unqualified column: total_amount
        else:

            matching_tables = [
                table_name
                for table_name, columns in ALLOWED_SCHEMA.items()
                if column_name in columns
                and (
                    table_name in aliases.values()
                    or not aliases
                )
            ]

            if not matching_tables:
                return False, (
                    f"Column '{column_name}' is not allowed."
                )

    # ---------------------------------------------------------
    # 4. Explicit dangerous-operation check
    # ---------------------------------------------------------

    dangerous_expressions = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
        exp.TruncateTable,
        exp.Grant,
        exp.Revoke,
    )

    for expression_type in dangerous_expressions:
        if statement.find(expression_type):
            return False, "Dangerous SQL operation detected."

    # Return normalized PostgreSQL SQL
    return True, statement.sql(dialect="postgres")