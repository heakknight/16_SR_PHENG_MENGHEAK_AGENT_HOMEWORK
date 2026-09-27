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

### 1. Model Setup
Make sure Ollama is installed and running, then pull the model:
```powershell
ollama pull qwen3:4b
```

### 2. Install Dependencies
```powershell
pip install ollama pydantic psycopg2-binary python-dotenv
```

### 3. Set Up Database
Create the `products` table and insert initial data in PostgreSQL:
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

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your PostgreSQL credentials:
```powershell
cp .env.example .env
```

### 5. Run the App
```powershell
python main.py
```

#### Console Commands
* `role customer` - Switch to Customer mode (default).
* `role admin` - Switch to Admin mode.
* `exit` or `quit` - Exit the application.

---

## 7. Example Run

### Sample Test Prompts
* **Customer Search & Buy:** `Search for a macbook and buy 1`
* **Customer Denied Action:** `How many units of product 1 are in the warehouse?`
* **Admin Restock Action:** `role admin` then `Restock product 4 by 10 units`
* **Admin Delete Action:** `role admin` then `Delete product with ID 4`

---

### Test 1: Permitted Flow (Customer Search & Buy)
```text
User > search for a macbook and buy 1
[action] calling search_products with {'query': 'macbook'}
[observation] {'results': [{'id': 1, 'name': 'MacBook Pro M3', 'price': 1999.0, 'in_stock': True}]}
[action] calling buy_product with {'product_id': 1, 'quantity': 1}
[observation] {'status': 'SUCCESS', 'product_id': 1, 'purchased': 1, 'remaining_stock': 4}

[Agent] > Your MacBook Pro M3 (ID: 1) has been successfully purchased! 1 unit was bought for $1999.00.
```

### Test 2: Permission Enforcement (Customer Denied)
```text
User > how many units of product 1 are in the warehouse?
[action] calling check_stock with {'product_id': 1}
[observation] {'error': "PERMISSION_DENIED: Role 'customer' cannot run 'check_stock'."}

[Agent] > I'm sorry, but as a customer, I don't have permission to check stock levels.
```

### Test 3: Authorized Flow (Admin Restock)
```text
User > role admin
Active role switched to: admin

User > Restock product 4 by 10 units
[action] calling restock_product with {'amount': 10, 'product_id': 4}
[observation] {'status': 'RESTOCKED', 'product_id': 4, 'new_stock': 10}

[Agent] > Product 4 has been successfully restocked with 10 units. The new stock count is 10.
```
