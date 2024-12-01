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
                    # 基本價格資訊
                    'trade_date': result.trade_date,
                    'open_price': result.open_price,
                    'high_price': result.high_price,
                    'low_price': result.low_price,
                    'close_price': result.close_price,
                    'volume': result.volume,
                    'dividends': result.dividends,
                    'stock_splits': result.stock_splits,
                    
                    # 移動平均線
                    'ma5': result.ma5,
                    'ma10': result.ma10,
                    'ma20': result.ma20,
                    'ma60': result.ma60,
                    
                    # 指數移動平均線
                    'ema12': result.ema12,
                    'ema26': result.ema26,
                    
                    # MACD指標
                    'macd': result.macd,
                    'macd_signal': result.macd_signal,
                    'macd_hist': result.macd_hist,
                    
                    # RSI指標
                    'rsi14': result.rsi14,
                    
                    # 布林通道
                    'bb_upper': result.bb_upper,
                    'bb_middle': result.bb_middle,
                    'bb_lower': result.bb_lower,
                    
                    # 成交量指標
                    'volume_ma5': result.volume_ma5,
                    'volume_ma20': result.volume_ma20,
                    
                    # KD指標
                    'k_value': result.k_value,
                    'd_value': result.d_value,
                    
                    # ATR和波動率指標
                    'atr14': result.atr14,
                    'volatility20': result.volatility20,
                    
                    # ADX指標
                    'adx14': result.adx14
                }
                for result in results
            ]
    
    def save_stock_data(self, table_name: str, data: pd.DataFrame):
        stock_table = create_stock_table(table_name, self.db.metadata)
        
        with self.db.get_session() as session:
            # 先刪除現有資料（如果存在）
            if self.table_exists(table_name):
                session.execute(stock_table.delete())
            else:
                stock_table.create(self.db.engine, checkfirst=True)
                
            # 插入新資料
            records = [row.to_dict() for _, row in data.iterrows()]
            if records:  # 確保有資料才執行插入
                session.execute(stock_table.insert(), records)
            session.commit()
    
    def table_exists(self, table_name: str) -> bool:
        return self.db.table_exists(table_name)

class StockRepositoryFactory:
    @classmethod
    def create(cls, provider: str = 'sql') -> IStockRepository:
        if provider.lower() == 'sql':
            return StockRepository()
        raise ValueError(f"Unknown repository provider: {provider}")