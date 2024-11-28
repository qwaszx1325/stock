from typing import Type
from ..interfaces.stock_service import IStockService
from ..services.yahoo_finance_service import YahooFinanceStockService

class StockServiceFactory:
    """股票服務工廠"""
    
    _services = {
        'yahoo': YahooFinanceStockService,
    }
    
    @classmethod
    def create(cls, provider: str = 'yahoo') -> IStockService:
        service_class = cls._services.get(provider)
        if not service_class:
            raise ValueError(f"Unknown provider: {provider}")
        return service_class()