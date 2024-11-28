# app/routers/stock.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import date
from ..factories.service_factory import StockServiceFactory
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"]
)

async def get_stock_service():
    return StockServiceFactory.create('yahoo')

@router.get("/{stock_code}")
async def get_stock_data(
    stock_code: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service = Depends(get_stock_service)
):
    try:
        return await service.get_stock_data(stock_code, start_date, end_date)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )