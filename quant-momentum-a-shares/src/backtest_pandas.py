# src/backtest_pandas.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


def load_data(path="../data/510300.csv"):
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df = df[['Close']].dropna()
    df.sort_index(inplace=True)
    return df


def compute_momentum(df, window=20):
    """计算过去 window 天的收益率作为动量指标"""
    return df['Close'].pct_change(periods=window)


def backtest_momentum(df, window=20, fee=0.001):
    """基于动量信号的简单回测"""
    df = df.copy()
    df['momentum'] = compute_momentum(df, window)
    df['signal'] = (df['momentum'] > 0).astype(int)  # 1=持仓,0=空仓
    df['ret'] = df['Close'].pct_change()
    df['strategy_ret'] = df['signal'].shift(1) * df['ret']  # 滞后一个周期执行交易
    # 模拟手续费
    df['trade'] = df['signal'].diff().abs()
    df['strategy_ret_after_fee'] = df['strategy_ret'] - df['trade'] * fee
    df['cum_strategy'] = (1 + df['strategy_ret_after_fee'].fillna(0)).cumprod()
    df['cum_benchmark'] = (1 + df['ret'].fillna(0)).cumprod()
    return df


def calc_metrics(df):
    """计算绩效指标"""
    df = df.dropna()
    total_days = len(df)
    years = total_days / 252
    ann_ret = df['cum_strategy'].iloc[-1] ** (1 / years) - 1
    ann_vol = df['strategy_ret_after_fee'].std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else np.nan
    running_max = df['cum_strategy'].cummax()
    drawdown = (df['cum_strategy'] / running_max) - 1
    max_dd = drawdown.min()
    win_rate = (df['strategy_ret_after_fee'] > 0).mean()
    return {
        "年化收益率": f"{ann_ret * 100:.2f}%",
        "年化波动率": f"{ann_vol * 100:.2f}%",
        "Sharpe": f"{sharpe:.2f}",
        "最大回撤": f"{max_dd * 100:.2f}%",
        "胜率": f"{win_rate * 100:.2f}%"
    }


if __name__ == "__main__":
    df = load_data()
    df = backtest_momentum(df, window=20, fee=0.001)
    metrics = calc_metrics(df)
    print("策略绩效指标：")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['cum_strategy'], label='动量策略')
    plt.plot(df.index, df['cum_benchmark'], label='基准（持有）', linestyle='--')
    plt.title("A股动量策略 vs 基准收益曲线")
    plt.legend()
    plt.tight_layout()
    plt.show()
