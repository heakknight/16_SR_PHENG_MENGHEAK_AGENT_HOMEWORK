"""
Application configuration module.
Defines model parameters, iteration thresholds, and role-based access rules.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
LLM_MODEL = "qwen3:4b"
MAX_ITERATIONS = 5

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

ROLE_PERMISSIONS = {
    "customer": ["search_products", "buy_product"],
    "admin": ["search_products", "buy_product", "check_stock", "delete_product","restock_product"]
}

SYSTEM_PROMPT = """You are a helpful e-commerce shopping assistant.
    Guidelines:
    1. For general conversation or greetings, answer directly without invoking tools.
    2. If the user asks about product details, stock, or purchases, select and call the appropriate tool.
    3. If a tool call returns a PERMISSION_DENIED or VALIDATION_ERROR observation, politely explain the limitation to the user.
    4. Provide a clear, natural final response once all necessary tool observations are obtained.
"""