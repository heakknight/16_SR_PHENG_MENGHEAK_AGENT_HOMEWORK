"""
Execution harness and safety enforcement module.
Validates input schemas, enforces authorization policies, and encapsulates tool execution.
"""

from config import ROLE_PERMISSIONS
from schemas import (
    SearchProductsSchema,
    CheckStockSchema,
    BuyProductSchema,
    DeleteProductSchema,
    RestockProductSchema,
)
from tools import (
    search_products,
    check_stock,
    buy_product,
    delete_product,
    restock_product,
)

TOOL_REGISTRY = {
    "search_products": (search_products, SearchProductsSchema),
    "check_stock": (check_stock, CheckStockSchema),
    "buy_product": (buy_product, BuyProductSchema),
    "delete_product": (delete_product, DeleteProductSchema),
    "restock_product": (restock_product, RestockProductSchema),
}

def execute_safe_tool(role: str, tool_name: str, raw_args: dict) -> dict:
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Tool '{tool_name}' is not recognized."}

    allowed_tools = ROLE_PERMISSIONS.get(role, [])
    if tool_name not in allowed_tools:
        return {"error": f"PERMISSION_DENIED: Role '{role}' cannot run '{tool_name}'."}

    func, schema_cls = TOOL_REGISTRY[tool_name]

    try:
        validated_data = schema_cls(**raw_args)
        validated_args = validated_data.model_dump()
    except Exception as exc:
        return {"error": f"VALIDATION_ERROR: {str(exc)}"}

    try:
        return func(**validated_args)
    except Exception as exc:
        return {"error": f"EXECUTION_ERROR: {str(exc)}"}