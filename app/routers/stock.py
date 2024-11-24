from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import date
import yfinance as yf
from ..database.connection import DatabaseConnection
from ..database.models import create_stock_table
import pandas as pd
from sqlalchemy import MetaData, text 
from sqlalchemy.exc import SQLAlchemyError
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"]
)
@router.get("/{stock_code}")
async def get_stock_data(
    stock_code: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    try:
        logger.info(f"Fetching data for stock: {stock_code}")
        
        # 標準化股票代碼
        if not stock_code.endswith('.TW'):
            stock_code = f"{stock_code}.TW"
            
        # 取得資料庫連線
        db = DatabaseConnection.get_instance()
        table_name = stock_code.replace('.TW', '').lower()
        
        # 檢查表是否存在，不存在則建立並下載資料
        if not db.table_exists(table_name):
            logger.info(f"Table {table_name} does not exist. Creating and downloading data...")
            
            # 建立表格
            metadata = MetaData()
            table = create_stock_table(table_name, metadata)
            metadata.create_all(db._engine)
            
            # 下載資料
            stock = yf.Ticker(stock_code)
            df = stock.history(period="max")
            
            if df.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data available for {stock_code}"
                )
            
            # 處理資料格式
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
            # 存入資料庫
            if not db.table_exists(table_name):
                db.create_table(table_name)
                
            # 使用 to_sql 存入資料
            df.to_sql(
                table_name,
                db._engine,
                schema='dbo',
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=500
            )
        
                    # 查詢資料
            query = text(f"""
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
            {f"AND trade_date >= :start_date" if start_date else ""}
            {f"AND trade_date <= :end_date" if end_date else ""}
            ORDER BY trade_date DESC
            """)

            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            with db.get_session() as session:
                result = session.execute(query, params)
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        df = pd.read_sql(query, db._engine)
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for stock {stock_code} in specified date range"
            )
            
        return {
            "stock_code": stock_code,
            "data": df.to_dict(orient="records"),
            "count": len(df)
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.get("/update/{stock_code}")
async def update_stock_data(stock_code: str):
    """更新特定股票的資料"""
    try:
        logger.info(f"Updating data for stock: {stock_code}")
        
        if not stock_code.endswith('.TW'):
            stock_code = f"{stock_code}.TW"
            
        db = DatabaseConnection.get_instance()
        table_name = stock_code.replace('.TW', '').lower()
        
        # 下載新資料
        stock = yf.Ticker(stock_code)
        df = stock.history(period="max")
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {stock_code}"
            )
            
        # 處理資料格式
        df = df.reset_index()
        # 重命名欄位
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
        # 轉換日期格式
        df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
            
        # 更新資料
        df.to_sql(
            table_name,
            db._engine,
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=500
        )
        
        return {
            "message": f"Successfully updated {stock_code}",
            "rows_updated": len(df)
        }
        
    except Exception as e:
        logger.error(f"Error updating stock data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating stock data: {str(e)}"
        )
    

@router.get("/download/{stock_code}")
async def download_stock_data(stock_code: str):
    """下載並儲存股票資料"""
    try:
        logger.info(f"Downloading data for stock: {stock_code}")
        
        # 標準化股票代碼
        if not stock_code.endswith('.TW'):
            stock_code = f"{stock_code}.TW"
            
        db = DatabaseConnection.get_instance()
        table_name = f"[dbo].[{stock_code.replace('.TW', '')}]"  # 修改這裡
        
        # 下載資料
        stock = yf.Ticker(stock_code)
        df = stock.history(period="max")
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {stock_code}"
            )
        
        # 處理資料格式
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
            
        # 存入資料庫 - 修改這裡
        try:
            with db.get_session() as session:
                # 先檢查表是否存在，如果存在就先刪除
                session.execute(text(f"IF OBJECT_ID(N'{table_name}', N'U') IS NOT NULL DROP TABLE {table_name}"))
                # 建立新表
                session.execute(text(f"""
                    CREATE TABLE {table_name} (
                        trade_date DATE PRIMARY KEY,
                        open_price FLOAT,
                        high_price FLOAT,
                        low_price FLOAT,
                        close_price FLOAT,
                        volume FLOAT,
                        dividends FLOAT,
                        stock_splits FLOAT
                    )
                """))
                session.commit()

                # 使用 BULK INSERT 或分批插入資料
                for _, row in df.iterrows():
                    session.execute(
                        text(f"""
                        INSERT INTO {table_name}
                        (trade_date, open_price, high_price, low_price, close_price, volume, dividends, stock_splits)
                        VALUES
                        (:trade_date, :open_price, :high_price, :low_price, :close_price, :volume, :dividends, :stock_splits)
                        """),
                        {
                            'trade_date': row['trade_date'],
                            'open_price': row['open_price'],
                            'high_price': row['high_price'],
                            'low_price': row['low_price'],
                            'close_price': row['close_price'],
                            'volume': row['volume'],
                            'dividends': row['dividends'],
                            'stock_splits': row['stock_splits']
                        }
                    )
                session.commit()
        
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )
        
        return {
            "message": f"Successfully downloaded and saved data for {stock_code}",
            "rows": len(df)
        }
        
    except Exception as e:
        logger.error(f"Error downloading stock data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading stock data: {str(e)}"
        )