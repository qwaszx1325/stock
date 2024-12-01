from typing import Optional, Dict, Any
from datetime import date
import yfinance as yf
import pandas as pd
import numpy as np
from fastapi import HTTPException
from ..interfaces.stock_service import IStockService
from ..interfaces.stock_repository import IStockRepository
from ..repository.stock_repository import StockRepositoryFactory

class YahooFinanceStockService(IStockService):
    def __init__(self):
        self.repository: IStockRepository = StockRepositoryFactory.create('sql')
    
    def _normalize_stock_code(self, stock_code: str) -> str:
        if not stock_code.endswith('.TW'):
            return f"{stock_code}.TW"
        return stock_code
    
    def _get_table_name(self, stock_code: str) -> str:
        return stock_code.replace('.TW', '').lower()
    
    def _calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """計算指數移動平均"""
        return data.ewm(span=period, adjust=False).mean()
    
    def _calculate_macd(self, data: pd.Series) -> tuple:
        """計算MACD"""
        ema12 = self._calculate_ema(data, 12)
        ema26 = self._calculate_ema(data, 26)
        macd_line = ema12 - ema26
        signal_line = self._calculate_ema(macd_line, 9)
        macd_hist = macd_line - signal_line
        return macd_line, signal_line, macd_hist

    def _calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """計算RSI"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_bollinger_bands(self, data: pd.Series, period: int = 20) -> tuple:
        """計算布林帶"""
        middle_band = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper_band = middle_band + (std * 2)
        lower_band = middle_band - (std * 2)
        return upper_band, middle_band, lower_band

    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                            k_period: int = 14, d_period: int = 3) -> tuple:
        """計算KD指標"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        return k, d

    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """計算ATR"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def _transform_yf_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # 過濾掉未開盤的資料
        df = df[df['Volume'] > 0].copy()
        
        # 重設索引並重命名基本列
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
        
        # 計算日漲跌幅
        df['change_percent'] = ((df['close_price'] - df['close_price'].shift(1)) / df['close_price'].shift(1) * 100).round(2)

        # 計算移動平均線
        df['ma5'] = df['close_price'].rolling(window=5).mean()
        df['ma10'] = df['close_price'].rolling(window=10).mean()
        df['ma20'] = df['close_price'].rolling(window=20).mean()
        df['ma60'] = df['close_price'].rolling(window=60).mean()
        
        # 計算EMA
        df['ema12'] = self._calculate_ema(df['close_price'], 12)
        df['ema26'] = self._calculate_ema(df['close_price'], 26)
        
        # 計算MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = self._calculate_macd(df['close_price'])
        
        # 計算RSI
        df['rsi14'] = self._calculate_rsi(df['close_price'], 14)
        
        # 計算布林通道
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = self._calculate_bollinger_bands(df['close_price'])
        
        # 計算成交量移動平均
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        df['volume_ma20'] = df['volume'].rolling(window=20).mean()
        
        # 計算KD指標
        df['k_value'], df['d_value'] = self._calculate_stochastic(
            df['high_price'], 
            df['low_price'], 
            df['close_price']
        )
        
        # 計算ATR
        df['atr14'] = self._calculate_atr(
            df['high_price'],
            df['low_price'],
            df['close_price']
        )
        
        # 計算20日波動率
        df['volatility20'] = df['close_price'].rolling(window=20).std()
        
        # 將NaN值替換為None
        df = df.replace({np.nan: None})
        
        return df
    
    async def get_stock_data(
        self,
        stock_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        stock_code = self._normalize_stock_code(stock_code)
        table_name = self._get_table_name(stock_code)
        
        if not self.repository.table_exists(table_name):
            await self._fetch_and_save_data(stock_code, table_name)
        
        data = self.repository.get_stock_data(table_name, start_date, end_date)
        return {
            "stock_code": stock_code,
            "data": data,
            "count": len(data)
        }
    
    async def _fetch_and_save_data(self, stock_code: str, table_name: str):
        stock = yf.Ticker(stock_code)
        df = stock.history(period="max")
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for {stock_code}"
            )
        
        df = self._transform_yf_data(df)
        self.repository.save_stock_data(table_name, df)
    
    async def update_stock_data(self, stock_code: str) -> Dict[str, Any]:
        stock_code = self._normalize_stock_code(stock_code)
        table_name = self._get_table_name(stock_code)
        await self._fetch_and_save_data(stock_code, table_name)
        return {
            "message": f"Successfully updated {stock_code}",
            "rows_updated": len(df)
        }