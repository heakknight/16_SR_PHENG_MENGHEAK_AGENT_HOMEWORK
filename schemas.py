"""
Tool input schemas module.
Specifies Pydantic contracts and field-level validation boundaries for tool execution.
"""

from pydantic import BaseModel, Field

class SearchProductsSchema(BaseModel):
    query: str = Field(..., min_length=1, description="Keyword to search for items")


class CheckStockSchema(BaseModel):
    product_id: int = Field(..., gt=0, description="Positive integer ID of the product")


class BuyProductSchema(BaseModel):
    product_id: int = Field(..., gt=0, description="Positive integer ID of the product")
    quantity: int = Field(..., gt=0, le=10, description="Quantity to purchase between 1 and 10")


class DeleteProductSchema(BaseModel):
    product_id: int = Field(..., gt=0, description="ID of the product to remove from inventory")


class RestockProductSchema(BaseModel):
    product_id: int = Field(..., gt=0, description="ID of the product to restock")
    amount: int = Field(..., gt=0, le=100, description="Units to add (1 to 100)")