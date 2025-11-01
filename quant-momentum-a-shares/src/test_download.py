# test_download.py
import yfinance as yf

# 测试不同的标的
test_symbols = [
    "ASHR",      # 德银沪深300ETF (美股)
    "SPY",       # 标普500ETF (测试用)
    "000001.SS", # 上证指数
    "510300.SS", # 沪深300ETF
]

for symbol in test_symbols:
    print(f"\n尝试下载: {symbol}")
    try:
        df = yf.download(symbol, period="1mo")
        print(f"结果: {len(df)} 行数据")
        if len(df) > 0:
            print("前3行:")
            print(df.head(3))
    except Exception as e:
        print(f"错误: {e}")