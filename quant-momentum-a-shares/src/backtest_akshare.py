# src/backtest_akshare.py - 适配AKShare数据格式
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


def load_akshare_data(path="D:\Projects\quant-momentum-a-shares\src\data\\510300_akshare.csv"):
    """加载AKShare生成的数据"""
    df = pd.read_csv(path)

    # AKShare数据的列名是中文，需要转换
    column_mapping = {
        '日期': 'Date',
        '开盘': 'Open',
        '最高': 'High',
        '最低': 'Low',
        '收盘': 'Close',
        '成交量': 'Volume'
    }

    # 重命名列
    df = df.rename(columns=column_mapping)

    # 转换日期格式并设为索引
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # 只保留Close列用于回测
    df = df[['Close']].dropna()
    df.sort_index(inplace=True)

    print(f"数据加载成功，时间范围: {df.index[0]} 至 {df.index[-1]}")
    print(f"数据行数: {len(df)}")

    return df


def compute_momentum(df, window=20):
    """计算动量指标"""
    return df['Close'].pct_change(periods=window)


def backtest_momentum(df, window=20, fee=0.001):
    """动量策略回测"""
    df = df.copy()
    df['momentum'] = compute_momentum(df, window)
    df['signal'] = (df['momentum'] > 0).astype(int)  # 1=持仓, 0=空仓
    df['ret'] = df['Close'].pct_change()
    df['strategy_ret'] = df['signal'].shift(1) * df['ret']  # 滞后一期执行

    # 考虑交易费用
    df['trade'] = df['signal'].diff().abs()
    df['strategy_ret_after_fee'] = df['strategy_ret'] - df['trade'] * fee

    # 计算累计收益
    df['cum_strategy'] = (1 + df['strategy_ret_after_fee'].fillna(0)).cumprod()
    df['cum_benchmark'] = (1 + df['ret'].fillna(0)).cumprod()

    return df


def calc_metrics(df):
    """计算策略绩效指标"""
    df = df.dropna()

    if len(df) == 0:
        return {"错误": "数据为空"}

    total_days = len(df)
    years = total_days / 252

    try:
        final_value = df['cum_strategy'].iloc[-1]
        ann_ret = final_value ** (1 / years) - 1
    except:
        return {"错误": "计算年化收益失败"}

    ann_vol = df['strategy_ret_after_fee'].std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else np.nan

    running_max = df['cum_strategy'].cummax()
    drawdown = (df['cum_strategy'] / running_max) - 1
    max_dd = drawdown.min()

    win_rate = (df['strategy_ret_after_fee'] > 0).mean()
    total_return = final_value - 1

    return {
        "数据天数": total_days,
        "总收益率": f"{total_return * 100:.2f}%",
        "年化收益率": f"{ann_ret * 100:.2f}%",
        "年化波动率": f"{ann_vol * 100:.2f}%",
        "夏普比率": f"{sharpe:.2f}",
        "最大回撤": f"{max_dd * 100:.2f}%",
        "胜率": f"{win_rate * 100:.2f}%",
        "最终净值": f"{final_value:.2f}"
    }


def plot_results(df):
    """绘制回测结果"""
    plt.figure(figsize=(12, 8))

    # 收益曲线
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df['cum_strategy'], label='动量策略', linewidth=2)
    plt.plot(df.index, df['cum_benchmark'], label='基准（持有）', linestyle='--', linewidth=2)
    plt.title('A股动量策略 vs 基准收益曲线', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 回撤曲线
    plt.subplot(2, 1, 2)
    running_max = df['cum_strategy'].cummax()
    drawdown = (df['cum_strategy'] / running_max) - 1
    plt.fill_between(df.index, drawdown * 100, 0, alpha=0.3, color='red', label='回撤')
    plt.title('策略回撤', fontsize=14)
    plt.ylabel('回撤 (%)')
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # 加载数据
    df = load_akshare_data()

    if len(df) > 0:
        # 运行回测
        df = backtest_momentum(df, window=20, fee=0.001)

        # 计算指标
        metrics = calc_metrics(df)

        print("=" * 50)
        print("A股动量策略回测结果")
        print("=" * 50)
        for k, v in metrics.items():
            print(f"{k}: {v}")

        # 绘制图表
        plot_results(df)
    else:
        print("❌ 数据加载失败")