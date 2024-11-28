# app/repository/stock_repository.py
from typing import Optional, List, Dict
from datetime import date
import pandas as pd
from sqlalchemy import select
from ..database.connection import DatabaseConnection
from ..database.models import create_stock_table
from ..interfaces.stock_repository import IStockRepository

class StockRepository(IStockRepository):
    def __init__(self):
        self.db = DatabaseConnection.get_instance()
    
    def get_stock_data(
        self,
        table_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        stock_table = create_stock_table(table_name, self.db.metadata)
        
        with self.db.get_session() as session:
            query = select(stock_table).order_by(stock_table.c.trade_date)
            
            if start_date:
                query = query.where(stock_table.c.trade_date >= start_date)
            if end_date:
                query = query.where(stock_table.c.trade_date <= end_date)
            
            results = session.execute(query).fetchall()
            return [
                {
                    'trade_date': result.trade_date,
                    'open_price': result.open_price,
                    'high_price': result.high_price,
                    'low_price': result.low_price,
                    'close_price': result.close_price,
                    'volume': result.volume,
                    'dividends': result.dividends,
                    'stock_splits': result.stock_splits
                }
                for result in results
            ]
    
    def save_stock_data(self, table_name: str, data: pd.DataFrame):
        stock_table = create_stock_table(table_name, self.db.metadata)
        
        with self.db.get_session() as session:
            stock_table.create(self.db.engine, checkfirst=True)
            session.execute(
                stock_table.insert(),
                [row.to_dict() for _, row in data.iterrows()]
            )
            session.commit()
    
    def table_exists(self, table_name: str) -> bool:
        return self.db.table_exists(table_name)

class StockRepositoryFactory:
    @classmethod
    def create(cls, provider: str = 'sql') -> IStockRepository:
        if provider.lower() == 'sql':
            return StockRepository()
        raise ValueError(f"Unknown repository provider: {provider}")