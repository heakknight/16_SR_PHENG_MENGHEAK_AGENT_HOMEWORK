# Simple Safe E-Commerce Agent

A simple shopping agent built with Python, Ollama, and PostgreSQL that demonstrates an agent decision loop with application-level permission control.

---

## 1. Project Overview
This project implements an autonomous agent for an e-commerce store. Users can search for items, buy products, check inventory, and manage stock.

The model proposes actions, but the application safety harness decides whether the action is allowed to run.

---

## 2. Available Tools
The agent uses 5 database-backed tools:

* `search_products(query)`: Search items in the catalog by name.
* `buy_product(product_id, quantity)`: Purchase items and reduce stock in PostgreSQL.
* `check_stock(product_id)`: Check warehouse stock count (Admin only).
* `restock_product(product_id, amount)`: Add more stock to an item (Admin only).
* `delete_product(product_id)`: Remove a product from inventory (Admin only).

---

## 3. Agent Loop
The agent runs in a standard loop:
1. **User Request:** Receives a question from the user.
2. **Model Decision:** The LLM decides whether to answer directly or call a tool.
3. **Safety Check:** `harness.py` validates the user role and inputs before calling the database.
4. **Observation:** Tool output is returned to the LLM.
5. **Final Answer:** The LLM answers the user once the task is finished.

---

## 4. Permission Rules
Permissions are enforced in application code (`harness.py`):

| Tool | Customer | Admin |
|---|:---:|:---:|
| `search_products` | Allowed | Allowed |
| `buy_product` | Allowed | Allowed |
| `check_stock` | Denied | Allowed |
| `restock_product` | Denied | Allowed |
| `delete_product` | Denied | Allowed |

If a customer tries to call an admin tool, the harness blocks it and returns `PERMISSION_DENIED`.

---

## 5. Safety Controls
* **Input Validation:** Pydantic schemas enforce valid, positive IDs and quantities (`schemas.py`).
* **Error Handling:** Returns structured errors (like `INSUFFICIENT_STOCK` or `PERMISSION_DENIED`) without crashing the application.
* **Loop Limit:** Bounded by `MAX_ITERATIONS = 5` to prevent infinite loops.

---

## 6. Setup & How to Run

### 1. Install Dependencies
```powershell
pip install ollama pydantic psycopg2-binary
```

### 2. Set Up Database
Create the `products` table in PostgreSQL:

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    stock INT NOT NULL CHECK (stock >= 0)
);

INSERT INTO products (name, price, stock) VALUES
('MacBook Pro M3', 1999.00, 5),
('Wireless Mouse', 25.00, 15),
('Mechanical Keyboard', 85.00, 8),
('USB-C Adapter', 19.99, 0);
```

### 3. Run the App
```powershell
python main.py
```
