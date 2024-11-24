# app/main.py
from fastapi import FastAPI
from app.routers import stock
from app.database.connection import DatabaseConnection

app = FastAPI(title="Stock API")
app.include_router(stock.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    db = DatabaseConnection.get_instance()

@app.get("/health")
def health_check():
    return {"status": "healthy"}