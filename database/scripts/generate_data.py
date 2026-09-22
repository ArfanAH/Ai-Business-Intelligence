import os
import random
from datetime import date, timedelta
from decimal import Decimal

import psycopg
from dotenv import load_dotenv
from faker import Faker


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv("backend/.env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

fake = Faker()
Faker.seed(42)
random.seed(42)


# --------------------------------------------------
# Dataset configuration
# --------------------------------------------------

NUM_CUSTOMERS = 500
NUM_PRODUCTS = 50
NUM_ORDERS = 2000
NUM_EMPLOYEES = 50
NUM_EXPENSES = 500

CITIES = [
    "Dhaka",
    "Chittagong",
    "Sylhet",
    "Rajshahi",
    "Khulna",
    "Rangpur",
    "Barishal",
    "Mymensingh",
]

CATEGORIES = [
    "Electronics",
    "Home Appliances",
    "Mobile Accessories",
    "Office Supplies",
    "Computer Accessories",
    "Networking",
    "Furniture",
    "Grocery",
]

DEPARTMENTS = [
    "Sales",
    "Marketing",
    "IT",
    "HR",
    "Finance",
    "Operations",
]

EXPENSE_CATEGORIES = [
    "Office Rent",
    "Electricity",
    "Internet",
    "Transportation",
    "Marketing",
    "Office Supplies",
    "Maintenance",
    "Software",
]


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def random_date(start_date, end_date):
    days = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, days))


def money(min_value, max_value):
    return Decimal(str(round(random.uniform(min_value, max_value), 2)))


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("Connecting to PostgreSQL...")

    with psycopg.connect(**DB_CONFIG) as conn:

        with conn.cursor() as cur:

            # --------------------------------------------------
            # Clear existing generated data
            # --------------------------------------------------

            print("Clearing existing data...")

            cur.execute("""
                TRUNCATE TABLE
                    order_items,
                    orders,
                    inventory,
                    expenses,
                    employees,
                    products,
                    customers
                RESTART IDENTITY CASCADE;
            """)

            # --------------------------------------------------
            # Customers
            # --------------------------------------------------

            print("Generating customers...")

            customers = []

            for _ in range(NUM_CUSTOMERS):

                customers.append((
                    fake.name(),
                    random.choice(CITIES),
                    fake.phone_number()[:20],
                    random_date(
                        date(2023, 1, 1),
                        date(2026, 8, 31)
                    ),
                ))

            cur.executemany("""
                INSERT INTO customers
                    (name, city, phone, registration_date)
                VALUES
                    (%s, %s, %s, %s)
            """, customers)

            # --------------------------------------------------
            # Products
            # --------------------------------------------------

            print("Generating products...")

            product_names = [
                "Laptop",
                "Desktop PC",
                "Monitor",
                "Keyboard",
                "Mouse",
                "Headphone",
                "Webcam",
                "Printer",
                "Router",
                "WiFi Adapter",
                "SSD",
                "HDD",
                "RAM 8GB",
                "RAM 16GB",
                "USB Flash Drive",
                "Power Bank",
                "Smartphone",
                "Tablet",
                "Smart Watch",
                "Bluetooth Speaker",
                "USB Cable",
                "HDMI Cable",
                "Power Strip",
                "UPS",
                "Graphics Card",
                "Motherboard",
                "Processor",
                "Computer Case",
                "CPU Cooler",
                "Laptop Stand",
                "Office Chair",
                "Office Desk",
                "Printer Ink",
                "Notebook",
                "Pen Set",
                "File Folder",
                "External SSD",
                "Mechanical Keyboard",
                "Gaming Mouse",
                "Gaming Headset",
                "Network Switch",
                "Ethernet Cable",
                "Webcam Cover",
                "Microphone",
                "Barcode Scanner",
                "POS Machine",
                "Projector",
                "Projector Screen",
                "Surge Protector",
                "Wireless Mouse",
            ]

            products = []

            for i in range(NUM_PRODUCTS):

                products.append((
                    product_names[i],
                    random.choice(CATEGORIES),
                    money(500, 150000),
                    random.randint(5, 200),
                ))

            cur.executemany("""
                INSERT INTO products
                    (product_name, category, unit_price, stock_quantity)
                VALUES
                    (%s, %s, %s, %s)
            """, products)

            # Get product IDs and prices
            cur.execute("""
                SELECT product_id, unit_price
                FROM products
                ORDER BY product_id
            """)

            product_data = cur.fetchall()

            # --------------------------------------------------
            # Employees
            # --------------------------------------------------

            print("Generating employees...")

            employees = []

            for _ in range(NUM_EMPLOYEES):

                employees.append((
                    fake.name(),
                    random.choice(DEPARTMENTS),
                    money(25000, 150000),
                    random_date(
                        date(2020, 1, 1),
                        date(2026, 8, 31)
                    ),
                ))

            cur.executemany("""
                INSERT INTO employees
                    (name, department, salary, joining_date)
                VALUES
                    (%s, %s, %s, %s)
            """, employees)

            # --------------------------------------------------
            # Orders + Order Items
            # --------------------------------------------------

            print("Generating orders and order items...")

            order_records = []
            order_item_records = []

            for order_id in range(1, NUM_ORDERS + 1):

                customer_id = random.randint(1, NUM_CUSTOMERS)

                order_date = random_date(
                    date(2023, 1, 1),
                    date(2026, 8, 31)
                )

                city = random.choice(CITIES)

                number_of_items = random.randint(1, 5)

                selected_products = random.sample(
                    product_data,
                    number_of_items
                )

                total_amount = Decimal("0.00")

                for product_id, unit_price in selected_products:

                    quantity = random.randint(1, 5)

                    item_total = unit_price * quantity

                    total_amount += item_total

                    order_item_records.append((
                        order_id,
                        product_id,
                        quantity,
                        unit_price,
                    ))

                order_records.append((
                    customer_id,
                    order_date,
                    city,
                    total_amount,
                ))

            cur.executemany("""
                INSERT INTO orders
                    (customer_id, order_date, city, total_amount)
                VALUES
                    (%s, %s, %s, %s)
            """, order_records)

            cur.executemany("""
                INSERT INTO order_items
                    (order_id, product_id, quantity, unit_price)
                VALUES
                    (%s, %s, %s, %s)
            """, order_item_records)

            # --------------------------------------------------
            # Expenses
            # --------------------------------------------------

            print("Generating expenses...")

            expenses = []

            for _ in range(NUM_EXPENSES):

                expenses.append((
                    random.choice(EXPENSE_CATEGORIES),
                    money(1000, 200000),
                    random_date(
                        date(2023, 1, 1),
                        date(2026, 8, 31)
                    ),
                    random.choice(DEPARTMENTS),
                ))

            cur.executemany("""
                INSERT INTO expenses
                    (category, amount, expense_date, department)
                VALUES
                    (%s, %s, %s, %s)
            """, expenses)

            # --------------------------------------------------
            # Inventory
            # --------------------------------------------------

            print("Generating inventory...")

            inventory = []

            for product_id, _ in product_data:

                inventory.append((
                    product_id,
                    random.randint(0, 200),
                    date(2026, 8, 31),
                ))

            cur.executemany("""
                INSERT INTO inventory
                    (product_id, quantity, last_updated)
                VALUES
                    (%s, %s, %s)
            """, inventory)

            # --------------------------------------------------
            # Commit
            # --------------------------------------------------

            conn.commit()

            # --------------------------------------------------
            # Summary
            # --------------------------------------------------

            cur.execute("SELECT COUNT(*) FROM customers")
            customer_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM products")
            product_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM orders")
            order_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM order_items")
            order_item_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM employees")
            employee_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM expenses")
            expense_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM inventory")
            inventory_count = cur.fetchone()[0]

            print()
            print("=" * 50)
            print("DATABASE SEEDING COMPLETED")
            print("=" * 50)
            print(f"Customers:    {customer_count}")
            print(f"Products:     {product_count}")
            print(f"Orders:       {order_count}")
            print(f"Order Items:  {order_item_count}")
            print(f"Employees:    {employee_count}")
            print(f"Expenses:     {expense_count}")
            print(f"Inventory:    {inventory_count}")
            print("=" * 50)


if __name__ == "__main__":
    main()