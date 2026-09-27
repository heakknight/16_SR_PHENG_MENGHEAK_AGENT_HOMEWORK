"""
Tool implementation module.
Provides domain-specific business functions and inventory operations backed by PostgreSQL.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    """Establish and return a connection to PostgreSQL."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def search_products(query: str) -> dict:
    """Search available items by product name."""
    sql = "SELECT id, name, price, stock FROM products WHERE name ILIKE %s ORDER BY id ASC;"
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (f"%{query}%",))
                rows = cur.fetchall()
                return {
                    "results": [
                        {
                            "id": r["id"],
                            "name": r["name"],
                            "price": float(r["price"]),
                            "in_stock": r["stock"] > 0
                        }
                        for r in rows
                    ]
                }
    except Exception as exc:
        return {"error": f"Database search failed: {str(exc)}"}


def check_stock(product_id: int) -> dict:
    """Check exact warehouse stock count of a specific product ID (Admin only)."""
    sql = "SELECT id, name, stock FROM products WHERE id = %s;"
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (product_id,))
                row = cur.fetchone()
                if not row:
                    return {"error": f"Product with ID {product_id} not found."}
                return {"product_id": row["id"], "name": row["name"], "stock": row["stock"]}
    except Exception as exc:
        return {"error": f"Database query failed: {str(exc)}"}


def buy_product(product_id: int, quantity: int) -> dict:
    """Purchase a specific quantity of a product with transactional stock deduction."""
    lock_sql = "SELECT id, name, stock FROM products WHERE id = %s FOR UPDATE;"
    update_sql = "UPDATE products SET stock = stock - %s WHERE id = %s RETURNING stock;"

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(lock_sql, (product_id,))
                item = cur.fetchone()

                if not item:
                    return {"error": f"Product with ID {product_id} not found."}
                if item["stock"] < quantity:
                    return {"error": "INSUFFICIENT_STOCK", "available_stock": item["stock"]}

                cur.execute(update_sql, (quantity, product_id))
                row = cur.fetchone()
                if not row:
                    return {"error": f"Failed to update stock for product {product_id}."}

                updated_stock = row["stock"]
                conn.commit()

                return {
                    "status": "SUCCESS",
                    "product_id": product_id,
                    "purchased": quantity,
                    "remaining_stock": updated_stock
                }
    except Exception as exc:
        return {"error": f"Database transaction failed: {str(exc)}"}


def delete_product(product_id: int) -> dict:
    """Remove a product entirely from the database (Admin only)."""
    sql = "DELETE FROM products WHERE id = %s RETURNING id, name;"
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (product_id,))
                deleted = cur.fetchone()
                if not deleted:
                    return {"error": f"Product with ID {product_id} not found."}
                conn.commit()
                return {"status": "DELETED", "product_id": deleted["id"], "name": deleted["name"]}
    except Exception as exc:
        return {"error": f"Database deletion failed: {str(exc)}"}
    
def restock_product(product_id: int, amount: int) -> dict:
    """Add stock to an existing product in the database (Admin only)."""
    sql = "UPDATE products SET stock = stock + %s WHERE id = %s RETURNING id, stock;"
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (amount, product_id))
                row = cur.fetchone()
                if not row:
                    return {"error": f"Product with ID {product_id} not found."}
                conn.commit()
                return {"status": "RESTOCKED", "product_id": row["id"], "new_stock": row["stock"]}
    except Exception as exc:
        return {"error": f"Database restock failed: {str(exc)}"}