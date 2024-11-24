import yfinance as yf

# 下載台積電資料
tsmc = yf.download('2330.TW', start='2023-01-01', end='2024-01-01')

# 儲存成 CSV
tsmc.to_csv('tsmc_stock.csv')