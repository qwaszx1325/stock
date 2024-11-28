from ..interfaces.stock_repository import IStockRepository
from ..repository.sql_stock_repository import SQLStockRepository
from ..repository.mongo_stock_repository import MongoStockRepository

class StockRepositoryFactory:
    """股票資料儲存庫工廠"""
    
    _repositories = {
        'sql': SQLStockRepository,
        'mongo': MongoStockRepository
    }
    
    @classmethod
    def create(cls, db_type: str = 'sql') -> IStockRepository:
        repo_class = cls._repositories.get(db_type)
        if not repo_class:
            raise ValueError(f"Unknown database type: {db_type}")
        return repo_class()