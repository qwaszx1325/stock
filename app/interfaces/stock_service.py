from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import date

class IStockService(ABC):
    @abstractmethod
    async def get_stock_data(
        self,
        sotck_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update_stock_data(self, stock_code: str) -> Dict[str, Any]:
        pass

    