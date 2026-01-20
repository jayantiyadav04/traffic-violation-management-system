# Traffic Violation Management System

A full-stack web application built using **Flask**, **MySQL**, and **HTML/CSS/JavaScript** to manage traffic violations.

## Roles
- **Admin** – Full access (analytics, violations, users)
- **Officer** – Register and manage violations
- **Citizen** – View own violations and payment status

## Tech Stack
- Backend: Flask (Python)
- Database: MySQL
- Frontend: HTML, CSS, JavaScript

## Database Setup
- Create database traffic_violation_db
- Paste all the queries that are present in data.sql in MySQL

## Environment Configuration
### .env file (project root)
- DB_TYPE=mysql
- DB_HOST=localhost
- DB_USER=root
- DB_PASSWORD=your_mysql_password
- DB_NAME=traffic_violation_db
- APP_HOST=0.0.0.0
- APP_PORT=5000
- DEBUG=True

## Install Dependencies
- python -m venv venv
- venv\Scripts\activate
- pip install -r requirements.txt

## Run the Application
- main.py

## Access the Application
- http://localhost:5000

## Demo Login Credentials
- Admin    → admin / admin123
- Officer  → officer1 / officer123
- Citizen  → citizen1 / citizen123











