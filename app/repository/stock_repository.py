# repository/stock_repository.py
from typing import Optional, List, Dict
from datetime import date
import pandas as pd
from sqlalchemy import text
from ..database.connection import DatabaseConnection
from ..interfaces.stock_repository import IStockRepository
from ..exceptions import DatabaseException

class StockRepository(IStockRepository):
    def __init__(self):
        self.db = DatabaseConnection.get_instance()
    
    def get_stock_data(
        self,
        table_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        query = f"""
        SELECT 
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            dividends,
            stock_splits
        FROM [dbo].[{table_name}]
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND trade_date >= :start_date"
            params['start_date'] = start_date
        if end_date:
            query += " AND trade_date <= :end_date"
            params['end_date'] = end_date
            
        query += " ORDER BY trade_date"
        
        with self.db.get_session() as session:
            try:
                results = session.execute(text(query), params).fetchall()
                return [
                    {
                        'trade_date': row.trade_date,
                        'open_price': row.open_price,
                        'high_price': row.high_price,
                        'low_price': row.low_price,
                        'close_price': row.close_price,
                        'volume': row.volume,
                        'dividends': row.dividends,
                        'stock_splits': row.stock_splits
                    }
                    for row in results
                ]
            except Exception as e:
                raise DatabaseException(f"Error fetching data: {str(e)}")
    
    def save_stock_data(self, table_name: str, data: pd.DataFrame):
        if not self.table_exists(table_name):
            self.db.create_table(table_name)
            
        insert_query = f"""
        INSERT INTO [dbo].[{table_name}] (
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            dividends,
            stock_splits
        ) VALUES (
            :trade_date,
            :open_price,
            :high_price,
            :low_price,
            :close_price,
            :volume,
            :dividends,
            :stock_splits
        )
        """
        
        with self.db.get_session() as session:
            try:
                records = data.to_dict('records')
                for record in records:
                    session.execute(text(insert_query), record)
                session.commit()
            except Exception as e:
                raise DatabaseException(f"Error saving data: {str(e)}")
    
    def table_exists(self, table_name: str) -> bool:
        try:
            return self.db.table_exists(table_name)
        except Exception as e:
            raise DatabaseException(f"Error checking table existence: {str(e)}")

class StockRepositoryFactory:
    @classmethod
    def create(cls, provider: str = 'sql') -> IStockRepository:
        if provider.lower() == 'sql':
            return StockRepository()
        raise ValueError(f"Unknown repository provider: {provider}")