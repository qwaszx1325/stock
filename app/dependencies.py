from typing import Generator
from .database.connection import DatabaseConnection
from .repository.stock_repository import StockDataRepository
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    db = DatabaseConnection.get_instance()
    with db.get_session() as session:
        yield session

def get_stock_repository(db: Session = get_db()) -> StockDataRepository:
    return StockDataRepository(db)