# Warehouse Management System (Pure DAO)

**Author:** Tony Menšík

A robust desktop application for warehouse and e-shop management, re-engineered to use a strict **Data Access Object (DAO)** architecture. The system cleanly separates the database logic (DAO layer) from the business objects (Model layer) and the user interface (GUI), ensuring modularity, testability, and maintainability.

## 🚀 Features

* **Pure DAO Architecture:**
    * **DAO Layer (`src/dao/`):** Dedicated classes (`UserDAO`, `OrderDAO`, `ProductDAO`, `ReportDAO`) handle all SQL queries and database communication.
    * **Model Layer (`src/models.py`):** Simple Data Transfer Objects (DTOs) like `User` and `Product` that hold data without any database logic.
* **Database Features:**
    * **Transactions:** Implements atomic transactions for order processing (Order + Order Items) with rollback support.
    * **Views & Reporting:** Utilizes SQL Views (`v_sales_report`) for real-time sales aggregation.
    * **Data Types:** Handles various types including Float, Boolean, Enum, Varchar, and Datetime.
* **User Interface:** A comprehensive GUI built with **Tkinter**, featuring tabs for ordering, order management, and statistical reports.
* **Data Import:** Functionality to import products from JSON files directly into the database.
* **Robust Testing:** Includes a suite of unit tests using `unittest.mock` to validate DAO logic without requiring a live database connection.

## 🛠️ Installation

1. **Database Setup:**
    * Ensure **XAMPP** (or MySQL Server) is running.
    * Create a database named `eshop_db`.
    * Import the SQL script located in `sql/import.sql`. This will create all tables, views, and insert dummy data.

2. **Install dependencies:**
    ```bash
    py -m pip install -r requirements.txt
    ```

3. **Run the application:**
   * Double-click `run.bat` or run:
        ```bash
        python src/main.py
        ```

4. **Run Tests:**
   * run:
        ```bash
        python tests/test_app.py
        ```

## ⚙️ Configuration & Structure

The system configuration is located in `config/config.json`. Ensure your database credentials match your local setup.

**Example `config.json`:**
```json
{
    "db": {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "eshop_db"
    }
}