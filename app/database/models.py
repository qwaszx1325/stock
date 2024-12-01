from sqlalchemy import Column, Float, Date, MetaData, Table, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

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
    
    # 日漲跌幅
    change_percent = Column(Float)
    
    # 移動平均線
    ma5 = Column(Float)
    ma10 = Column(Float)
    ma20 = Column(Float)
    ma60 = Column(Float)
    
    # 指數移動平均線
    ema12 = Column(Float)
    ema26 = Column(Float)
    
    # MACD指標
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    
    # RSI指標
    rsi14 = Column(Float)
    
    # 布林通道
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    
    # 成交量指標
    volume_ma5 = Column(Float)
    volume_ma20 = Column(Float)
    
    # KD指標
    k_value = Column(Float)
    d_value = Column(Float)
    
    # ATR和波動率指標
    atr14 = Column(Float)
    volatility20 = Column(Float)
    
    # ADX指標
    adx14 = Column(Float)
    
    # 更新時間
    last_updated = Column(DATETIME, default=datetime.now)

def create_stock_table(table_name: str, metadata: MetaData):
    """建立股票資料表"""
    return Table(
        table_name, 
        metadata,
        # 基本價格資訊
        Column('trade_date', Date, primary_key=True),
        Column('open_price', Float),
        Column('high_price', Float),
        Column('low_price', Float),
        Column('close_price', Float),
        Column('volume', Float),
        Column('dividends', Float),
        Column('stock_splits', Float),
        
        # 日漲跌幅
        Column('change_percent', Float),
        
        # 移動平均線
        Column('ma5', Float),
        Column('ma10', Float),
        Column('ma20', Float),
        Column('ma60', Float),
        
        # 指數移動平均線
        Column('ema12', Float),
        Column('ema26', Float),
        
        # MACD指標
        Column('macd', Float),
        Column('macd_signal', Float),
        Column('macd_hist', Float),
        
        # RSI指標
        Column('rsi14', Float),
        
        # 布林通道
        Column('bb_upper', Float),
        Column('bb_middle', Float),
        Column('bb_lower', Float),
        
        # 成交量指標
        Column('volume_ma5', Float),
        Column('volume_ma20', Float),
        
        # KD指標
        Column('k_value', Float),
        Column('d_value', Float),
        
        # ATR和波動率指標
        Column('atr14', Float),
        Column('volatility20', Float),
        
        # ADX指標
        Column('adx14', Float),
        
        # 更新時間
        Column('last_updated', DATETIME, default=datetime.now),
        
        extend_existing=True
    )