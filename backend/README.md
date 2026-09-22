# AI Business Intelligence Assistant

An AI-powered Business Intelligence system that allows users to ask business questions in natural language and receive SQL-based results, AI-generated insights, and automatically selected visualizations.

## Overview

Traditional Business Intelligence tools often require users to manually build queries, filters, and charts.

This project provides a conversational interface where a user can simply ask:

- What was our total sales?
- Which product had the highest sales?
- Show me monthly sales for 2026.
- Show sales by city.
- What is our total expense by department?
- Which products are running low in inventory?

The system converts the natural-language question into SQL, validates the generated SQL for security, executes it against a read-only PostgreSQL database, and presents the result with an AI-generated business insight and visualization.

## Key Features

- Natural language business queries
- AI-generated PostgreSQL SQL
- SQL validation and security checks
- Read-only database access
- Query execution with timeout protection
- AI-generated business insights
- Automatic chart selection
- Bar charts
- Line charts
- Pie charts
- Scatter plots
- KPI cards
- AI-selected chart orientation
- Conversational follow-up questions
- JWT-based authentication
- Protected API endpoints
- Responsive dashboard
- Environment-variable based secrets
- Git-safe `.env` configuration

## System Workflow

```text
User Question
      ↓
Natural Language Understanding
      ↓
AI-generated SQL
      ↓
SQL Security Validation
      ↓
Read-only PostgreSQL Query
      ↓
Query Result
      ↓
 ┌───────────────┬─────────────────┐
 ↓               ↓                 ↓
AI Insight    Chart Selection    Result Table
 ↓               ↓
Business      Visualization
Summary       Rendering


Technology Stack
Frontend
Next.js
React
TypeScript
Tailwind CSS
Plotly.js
Backend
Python
FastAPI
Psycopg
Pandas
SQLGlot
JWT Authentication
bcrypt
Database
PostgreSQL
AI
Groq API
openai/gpt-oss-120b
Database

The application uses a company-style relational database containing:

Customers
Products
Orders
Order Items
Employees
Expenses
Inventory

The development dataset contains:

Table	Records
Customers	500
Products	50
Orders	2,000
Order Items	6,054
Employees	50
Expenses	500
Inventory	50
Security

Security is an important part of the application.

SQL Validation

The backend validates AI-generated SQL before execution.

The system:

Allows only SELECT queries
Rejects INSERT operations
Rejects UPDATE operations
Rejects DELETE operations
Rejects DROP operations
Rejects ALTER operations
Rejects CREATE operations
Rejects TRUNCATE operations
Rejects multiple SQL statements
Checks allowed tables and columns
Read-only Database

The application uses a dedicated PostgreSQL read-only user for business queries.

Database transactions are also explicitly configured as read-only.

Query Timeout

Database queries have a timeout to prevent excessively long-running queries.

Authentication

The application uses JWT-based authentication to protect the business intelligence API.

Passwords are hashed using bcrypt.

Environment Variables

Sensitive information such as:

Groq API key
Database password
JWT secret

is stored in environment variables instead of source code.

AI Chart Selection

The system does not use a fixed chart for every query.

The AI analyzes the query result and selects an appropriate visualization.

Supported chart types:

Chart	Usage
KPI	Single important numeric value
Bar	Category comparison or ranking
Line	Time-based trends
Pie	Part-to-whole distribution
Scatter	Relationship between numeric variables

For bar charts, the AI can also select:

Vertical orientation
Horizontal orientation

For example, a result containing many city names can automatically use a horizontal bar chart to improve readability.


Running the Project Locally
1. Start PostgreSQL

Make sure PostgreSQL is running and the database is available.

2. Configure Backend Environment

Create:

backend/.env

Example:

DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_business_intelligence
DB_USER=bi_readonly
DB_PASSWORD=your_database_password

GROQ_API_KEY=your_groq_api_key

JWT_SECRET_KEY=your_jwt_secret

Never commit the real .env file to GitHub.

3. Activate Python Environment

From the project root:

.\backend\.venv\Scripts\Activate.ps1
4. Start FastAPI
uvicorn backend.main:app --reload

Backend:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs
5. Start Next.js

Open another terminal:

cd frontend
npm run dev

Frontend:

http://localhost:3000
Demo Login

For the current local development version:

Username: admin
Password: admin123

For production deployment, the demo authentication should be replaced with a proper user-management system.

Future Improvements

Possible future improvements include:

Production user management
Role-based access control
More advanced dashboard pages
Export results to CSV/Excel
More business-specific chart types
Improved natural-language query understanding
Query caching
Rate limiting
Production-grade authentication
Cloud deployment
Database connection pooling
More advanced conversational analytics
Project Goal

The goal of this project is to demonstrate how modern AI can be combined with traditional Business Intelligence systems to make business data easier to explore through natural-language interaction.

Instead of requiring users to manually write SQL queries or configure every visualization, the system provides an AI-assisted workflow from question to data to insight.

Author

Md. Arfan Ahmed

AI Business Intelligence Assistant
MSc in CSE