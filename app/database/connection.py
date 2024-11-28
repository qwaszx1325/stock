# database/connection.py
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
        """建立資料表"""
        query = text(f"""
        CREATE TABLE [dbo].[{table_name}] (
            trade_date DATE PRIMARY KEY,
            open_price FLOAT,
            high_price FLOAT,
            low_price FLOAT,
            close_price FLOAT,
            volume FLOAT,
            dividends FLOAT,
            stock_splits FLOAT
        )
        """)
        
        with self.get_session() as session:
            try:
                session.execute(query)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e