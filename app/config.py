# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

# 取得目前檔案的目錄
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 取得專案根目錄
ROOT_DIR = os.path.dirname(CURRENT_DIR)
# .env 檔案的完整路徑
ENV_FILE = os.path.join(ROOT_DIR, '.env')

# 手動載入 .env 檔案
load_dotenv(ENV_FILE)

class Settings(BaseSettings):
    # 資料庫設定
    DB_SERVER: str = os.getenv('DB_SERVER', 'localhost')
    DB_NAME: str = os.getenv('DB_NAME', 'stock_db')
    DB_USERNAME: str = os.getenv('DB_USERNAME', 'sa')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')

    # 資料庫連線池設定
    DB_POOL_SIZE: int = int(os.getenv('DB_POOL_SIZE', '5'))
    DB_MAX_OVERFLOW: int = int(os.getenv('DB_MAX_OVERFLOW', '10'))
    DB_POOL_TIMEOUT: int = int(os.getenv('DB_POOL_TIMEOUT', '30'))
    DB_POOL_RECYCLE: int = int(os.getenv('DB_POOL_RECYCLE', '3600'))

    # API 設定
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"
    DOWNLOAD_BATCH_SIZE: int = 100
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra='allow'
    )
""
@lru_cache
def get_settings():
    return Settings()

settings = get_settings()

# 印出設定值（不包含密碼）以進行除錯
print("Current settings:")
for key, value in settings.model_dump().items():
    if 'PASSWORD' not in key:
        print(f"{key}: {value}")