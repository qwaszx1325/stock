from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional

class StockBase(BaseModel):
    date: date
    stock_code: str = Field(..., description="股票代碼")
    open_price: float = Field(..., description="開盤價")
    high_price: float = Field(..., description="最高價")
    low_price: float = Field(..., description="最低價")
    close_price: float = Field(..., description="收盤價")
    adj_close: float = Field(..., description="調整後收盤價")
    volume: float = Field(..., description="成交量")

class StockCreate(StockBase):
    pass

class StockUpdate(StockBase):
    pass

class StockInDB(StockBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StockResponse(StockBase):
    class Config:
        from_attributes = True

class StockList(BaseModel):
    data: List[StockResponse]
    total: int
    page: int
    page_size: int