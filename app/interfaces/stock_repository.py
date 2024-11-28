from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import date
import pandas as pd

class IStockRepository(ABC):
    @abstractmethod
    def get_stock_data(
        self, table_name:str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
        ):
        pass

    @abstractmethod
    def save_stock_data(self, table_name:str, data: pd.DataFrame):
        pass

    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        pass