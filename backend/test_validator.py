from sql_validator import validate_sql


test_queries = [
    "SELECT SUM(total_amount) FROM orders;",
    
    "SELECT city, SUM(total_amount) "
    "FROM orders GROUP BY city;",
    
    "DELETE FROM orders;",
    
    "DROP TABLE orders;",
    
    "SELECT * FROM unknown_table;",
    
    "SELECT * FROM orders; SELECT * FROM customers;",
]


for query in test_queries:
    valid, result = validate_sql(query)

    print("\nQuery:")
    print(query)

    print("Valid:", valid)
    print("Result:", result)