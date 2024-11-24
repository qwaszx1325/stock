from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.models import StockPrice
from ..exceptions import StockNotFoundException, DatabaseException
from typing import List, Optional
from datetime import date

class StockDataRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_stock_data(
        self,
        stock_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[StockPrice]:
        try:
            query = self.db.query(StockPrice).filter(
                StockPrice.stock_code == stock_code
            )
            
            if start_date:
                query = query.filter(StockPrice.date >= start_date)
            if end_date:
                query = query.filter(StockPrice.date <= end_date)
                
            return query.order_by(StockPrice.date.desc())\
                       .offset(skip)\
                       .limit(limit)\
                       .all()
        except Exception as e:
            raise DatabaseException(str(e))

    def get_latest_stock_data(self, stock_code: str) -> StockPrice:
        try:
            stock = self.db.query(StockPrice)\
                          .filter(StockPrice.stock_code == stock_code)\
                          .order_by(StockPrice.date.desc())\
                          .first()
            if not stock:
                raise StockNotFoundException(stock_code)
            return stock
        except StockNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(str(e))

    def create_stock_data(self, stock_data: List[StockPrice]) -> bool:
        try:
            self.db.bulk_save_objects(stock_data)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(str(e))

    def search_stocks(self, query: str, limit: int = 10) -> List[str]:
        try:
            return self.db.query(StockPrice.stock_code)\
                         .filter(StockPrice.stock_code.like(f'%{query}%'))\
                         .distinct()\
                         .limit(limit)\
                         .all()
        except Exception as e:
            raise DatabaseException(str(e))