import sqlite3
import logging

DB_NAME = "finance.db"
logger = logging.getLogger(__name__)
ALLOWED_OPERATION_TYPES = ("expense", "income")


def _ensure_operation_type_column(cursor: sqlite3.Cursor) -> None:
    """Безопасно добавляет колонку operation_type в существующую таблицу."""
    cursor.execute("PRAGMA table_info(expenses)")
    columns = {row[1] for row in cursor.fetchall()}
    if "operation_type" not in columns:
        cursor.execute(
            "ALTER TABLE expenses ADD COLUMN operation_type TEXT NOT NULL DEFAULT 'expense'"
        )
        cursor.execute(
            "UPDATE expenses SET operation_type = 'expense' WHERE operation_type IS NULL"
        )

def init_db() -> None:
    """Инициализирует базу данных и создает таблицу расходов."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    product TEXT NOT NULL,
                    operation_type TEXT NOT NULL DEFAULT 'expense' CHECK(operation_type IN ('expense', 'income')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            _ensure_operation_type_column(cursor)
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_expenses_user_id_created_at
                ON expenses (user_id, created_at)
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_expenses_user_id_type_created_at
                ON expenses (user_id, operation_type, created_at)
                """
            )
            conn.commit()
            logger.info("db_initialized", extra={"db": DB_NAME})
    except sqlite3.Error:
        logger.exception("db_init_failed", extra={"db": DB_NAME})
        raise

def add_operation(user_id: int, amount: float, product: str, operation_type: str) -> None:
    """Добавляет запись об операции (расход/доход) в базу данных."""
    if user_id <= 0:
        raise ValueError("user_id must be positive")
    if amount <= 0:
        raise ValueError("amount must be greater than zero")
    if operation_type not in ALLOWED_OPERATION_TYPES:
        raise ValueError("operation_type must be one of: expense, income")

    normalized_product = product.strip()
    if not normalized_product:
        raise ValueError("product must not be empty")

    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO expenses (user_id, amount, product, operation_type)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, amount, normalized_product, operation_type),
            )
            conn.commit()
            logger.info(
                "operation_added",
                extra={"user_id": user_id, "amount": amount, "operation_type": operation_type},
            )
    except sqlite3.Error:
        logger.exception("db_insert_failed", extra={"user_id": user_id})
        raise


def add_expense(user_id: int, amount: float, product: str) -> None:
    """Совместимость: добавляет запись о расходе в базу данных."""
    add_operation(user_id=user_id, amount=amount, product=product, operation_type="expense")


def get_operations_summary(user_id: int, period: str = "all") -> dict[str, float]:
    """Возвращает суммы расходов, доходов и баланс за указанный период."""
    if user_id <= 0:
        raise ValueError("user_id must be positive")

    period_clause = ""
    if period == "day":
        period_clause = " AND date(created_at) = date('now')"
    elif period == "week":
        period_clause = " AND date(created_at) >= date('now', '-7 days')"
    elif period == "month":
        period_clause = " AND date(created_at) >= date('now', 'start of month')"

    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT operation_type, COALESCE(SUM(amount), 0)
                FROM expenses
                WHERE user_id = ? {period_clause}
                GROUP BY operation_type
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()

            totals = {"expense": 0.0, "income": 0.0}
            for op_type, total in rows:
                if op_type in totals:
                    totals[op_type] = float(total or 0.0)

            totals["balance"] = totals["income"] - totals["expense"]
            return totals
    except sqlite3.Error:
        logger.exception("db_select_failed", extra={"user_id": user_id, "period": period})
        raise

def get_total_expenses(user_id: int, period: str = "all") -> float:
    """Совместимость: возвращает сумму расходов за период."""
    return get_operations_summary(user_id=user_id, period=period)["expense"]
