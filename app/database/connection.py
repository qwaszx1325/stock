from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from ..config import settings

class DatabaseConnection:
    _instance = None
    _engine = None
    _SessionLocal = None
    _metadata = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._engine is None:
            connection_string = (
                f'mssql+pyodbc://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@'
                f'{settings.DB_SERVER}/{settings.DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server'
            )

            self._engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=settings.DB_POOL_SIZE,
                pool_recycle=settings.DB_POOL_RECYCLE
            )
            
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            self._metadata = MetaData()
            
    @property
    def metadata(self):
        return self._metadata
    
    @property
    def engine(self):
        return self._engine
    
    def table_exists(self, table_name: str) -> bool:
        """檢查表是否存在"""
        query = text(f"""
        SELECT 1 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'dbo' 
        AND TABLE_NAME = :table_name
        """)
        
        with self.get_session() as session:
            result = session.execute(query, {'table_name': table_name})
            return bool(result.scalar())

    @contextmanager
    def get_session(self):
        session = self._SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create_table(self, table_name: str):
        """建立資料表，包含技術分析指標(sql server建表指令)"""
        query = text(f"""
        CREATE TABLE [dbo].[{table_name}] (
            -- 基本價格資訊
            trade_date DATE PRIMARY KEY,
            open_price FLOAT,
            high_price FLOAT,
            low_price FLOAT,
            close_price FLOAT,
            volume FLOAT,
            dividends FLOAT,
            stock_splits FLOAT,
            
            -- 移動平均線
            ma5 FLOAT,    -- 5日移動平均
            ma10 FLOAT,   -- 10日移動平均
            ma20 FLOAT,   -- 20日移動平均
            ma60 FLOAT,   -- 60日移動平均
            
            -- 指數移動平均線
            ema12 FLOAT,  -- 12日指數移動平均
            ema26 FLOAT,  -- 26日指數移動平均
            
            -- MACD指標
            macd FLOAT,           -- MACD線
            macd_signal FLOAT,    -- MACD信號線
            macd_hist FLOAT,      -- MACD柱狀圖
            
            -- RSI指標
            rsi14 FLOAT,  -- 14日RSI
            
            -- 布林通道
            bb_upper FLOAT,       -- 上軌
            bb_middle FLOAT,      -- 中軌
            bb_lower FLOAT,       -- 下軌
            
            -- 成交量指標
            volume_ma5 FLOAT,     -- 5日成交量平均
            volume_ma20 FLOAT,    -- 20日成交量平均
            
            -- KD指標
            k_value FLOAT,        -- K值
            d_value FLOAT,        -- D值
            
            -- ATR和波動率指標
            atr14 FLOAT,          -- 14日ATR
            volatility20 FLOAT,   -- 20日波動率
            
            -- 趨勢指標
            adx14 FLOAT,          -- 14日ADX
            
            -- 更新時間戳記
            last_updated DATETIME DEFAULT GETDATE()
        )
        """)
        
        with self.get_session() as session:
            try:
                session.execute(query)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e