from backend.database import get_connection


def execute_query(sql: str):
    """
    Execute a validated SELECT query and return
    column names and query results.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            connection.execute("SET TRANSACTION READ ONLY")
            cursor.execute("SET statement_timeout = 10000")
            cursor.execute(sql)

            rows = cursor.fetchall()

            columns = [
                description.name
                for description in cursor.description
            ]

            return columns, rows

    finally:
        connection.close()