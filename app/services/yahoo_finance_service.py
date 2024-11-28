from typing import Optional, Dict, Any
from datetime import date
import yfinance as yf
import pandas as pd
from fastapi import HTTPException
from ..interfaces.stock_service import IStockService
from ..interfaces.stock_repository import IStockRepository
from ..repository.stock_repository import StockRepositoryFactory

class YahooFinanceStockService(IStockService):
    def __init__(self):
        self.repository: IStockRepository = StockRepositoryFactory.create('sql')
    
    def _normalize_stock_code(self, stock_code: str) -> str:
        if not stock_code.endswith('.TW'):
            return f"{stock_code}.TW"
        return stock_code
    
    def _get_table_name(self, stock_code: str) -> str:
        return stock_code.replace('.TW', '').lower()
    
    def _transform_yf_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.reset_index()
        df.columns = [
            'trade_date',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume',
            'dividends',
            'stock_splits'
        ]
        df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
        return df
    
    async def get_stock_data(
        self,
        stock_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        stock_code = self._normalize_stock_code(stock_code)
        table_name = self._get_table_name(stock_code)
        
        if not self.repository.table_exists(table_name):
            await self._fetch_and_save_data(stock_code, table_name)
        
        data = self.repository.get_stock_data(table_name, start_date, end_date)
        return {
            "stock_code": stock_code,
            "data": data,
            "count": len(data)
        }
    
    async def _fetch_and_save_data(self, stock_code: str, table_name: str):
        stock = yf.Ticker(stock_code)
        df = stock.history(period="max")
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {stock_code}"
            )
        
        df = self._transform_yf_data(df)
        self.repository.save_stock_data(table_name, df)
    
    async def update_stock_data(self, stock_code: str) -> Dict[str, Any]:
        stock_code = self._normalize_stock_code(stock_code)
        table_name = self._get_table_name(stock_code)
        await self._fetch_and_save_data(stock_code, table_name)
        return {
            "message": f"Successfully updated {stock_code}",
            "rows_updated": len(df)
        }