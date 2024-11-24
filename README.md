
# Stock Market Data API

一個基於 **FastAPI** 的股票資料 API，用於下載、儲存及查詢台股資料。

---

## 功能特點 🌟
- **下載與儲存**：支援台股股票歷史資料的下載與儲存。
- **自動建表**：無需手動操作，API 自動建立資料庫表結構。
- **查詢功能**：支援按照日期範圍查詢指定股票的數據。
- **更新資料**：快速同步最新的股票歷史資料。

---

## 環境需求 🛠️
- **Python**：3.8+
- **SQL Server**：資料庫
- **ODBC Driver**：17 for SQL Server

---

## 安裝 🚀

1. 安裝必要套件：
   ```bash
   pip install fastapi uvicorn sqlalchemy pyodbc pandas yfinance
   ```

2. 配置環境變數：  
   創建 `.env` 文件，並填入以下內容：
   ```env
   DB_SERVER=localhost
   DB_NAME=stock_db
   DB_USERNAME=your_username
   DB_PASSWORD=your_password
   DB_POOL_SIZE=5
   DB_MAX_OVERFLOW=10
   DB_POOL_TIMEOUT=30
   DB_POOL_RECYCLE=3600
   ```

---

## API 端點 🔗

### 1️⃣ **下載股票資料**
- **描述**：下載並儲存指定股票的歷史資料。
- **方法**：`GET`
- **URL**：`/api/v1/stocks/download/{stock_code}`
- **參數**：
  - `stock_code`：股票代碼（例如：`2330`）。
- **範例**：
  ```http
  GET /api/v1/stocks/download/2330
  ```

---

### 2️⃣ **查詢股票資料**
- **描述**：查詢指定股票的歷史資料，支援日期範圍。
- **方法**：`GET`
- **URL**：`/api/v1/stocks/{stock_code}`
- **參數**：
  - `stock_code` (必填)：股票代碼（例如：`2330`）。
  - `start_date` (選填)：開始日期，格式為 `YYYY-MM-DD`。
  - `end_date` (選填)：結束日期，格式為 `YYYY-MM-DD`。
- **範例**：
  ```http
  GET /api/v1/stocks/2330?start_date=2023-01-01&end_date=2023-12-31
  ```

---

### 3️⃣ **更新股票資料**
- **描述**：更新指定股票的歷史資料至最新。
- **方法**：`GET`
- **URL**：`/api/v1/stocks/update/{stock_code}`
- **參數**：
  - `stock_code`：股票代碼（例如：`2330`）。
- **範例**：
  ```http
  GET /api/v1/stocks/update/2330
  ```

