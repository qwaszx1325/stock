from fastapi import HTTPException
from typing import Any

class StockException(HTTPException):
    def __init__(self, detail: Any = None):
        super().__init__(status_code=400, detail=detail)

class StockNotFoundException(HTTPException):
    def __init__(self, stock_code: str):
        super().__init__(
            status_code=404,
            detail=f"Stock with code {stock_code} not found"
        )

class DatabaseException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)