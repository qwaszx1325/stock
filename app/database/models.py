# app/database/models.py
from sqlalchemy import Column, Float, Date, MetaData, Table

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