from query_executor import execute_query


sql = """
SELECT
    SUM(total_amount) AS total_sales
FROM orders;
"""


columns, rows = execute_query(sql)

print("\nColumns:")
print(columns)

print("\nRows:")
print(rows)