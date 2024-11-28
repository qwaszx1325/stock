# app/database/models.py
from sqlalchemy import Column, Float, Date, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class StockPrice(Base):
    __tablename__ = 'stock_prices'
    
    trade_date = Column(Date, primary_key=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)
    dividends = Column(Float)
    stock_splits = Column(Float)

def create_stock_table(table_name: str, metadata: MetaData):
    """建立股票資料表"""
    return Table(
        table_name, 
        metadata,
        Column('trade_date', Date, primary_key=True),
        Column('open_price', Float),
        Column('high_price', Float),
        Column('low_price', Float),
        Column('close_price', Float),
        Column('volume', Float),
        Column('dividends', Float),
        Column('stock_splits', Float),
        extend_existing=True
    )