# src/data_fetch.py
import yfinance as yf
import pandas as pd
import os

def fetch_data(ticker="510300.SS", start="2018-01-01", end="2024-12-31", save_path="../data/510300.csv"):
    """
    从 yfinance 抓取指定股票或ETF的历史行情数据。
    参数：
        ticker: 股票代码（如 510300.SS 代表沪深300 ETF）
        start, end: 时间范围
        save_path: 保存路径
    """
    print(f"正在从 yfinance 下载 {ticker} 数据...")
    df = yf.download(ticker, start=start, end=end)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path)
    print(f"数据已保存到 {save_path}，共 {len(df)} 条记录。")
    return df

if __name__ == "__main__":
    df = fetch_data()
    print(df.head())