# src/backtest_optimized.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


def load_akshare_data():
    """加载数据"""
    path = "D:\Projects\quant-momentum-a-shares\src\data\\510300_akshare.csv"
    if not os.path.exists(path):
        print("❌ 数据文件不存在")
        return pd.DataFrame()

    df = pd.read_csv(path)

    # 自动映射列名
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower()
        if '日期' in col or 'date' in col_lower:
            column_mapping[col] = 'Date'
        elif '收盘' in col or 'close' in col_lower:
            column_mapping[col] = 'Close'

    df = df.rename(columns=column_mapping)

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

    if 'Close' not in df.columns:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            df['Close'] = df[numeric_cols[0]]

    df = df[['Close']].dropna()
    df.sort_index(inplace=True)

    print(f"✅ 数据加载成功: {len(df)} 条记录")
    return df


def backtest_momentum(df, window=20, fee=0.001):
    """原始动量策略"""
    df = df.copy()
    df['momentum'] = df['Close'].pct_change(periods=window)
    df['signal'] = (df['momentum'] > 0).astype(int)
    df['ret'] = df['Close'].pct_change()
    df['strategy_ret'] = df['signal'].shift(1) * df['ret']

    df['trade'] = df['signal'].diff().abs()
    df['strategy_ret_after_fee'] = df['strategy_ret'] - df['trade'] * fee

    df['cum_strategy'] = (1 + df['strategy_ret_after_fee'].fillna(0)).cumprod()
    df['cum_benchmark'] = (1 + df['ret'].fillna(0)).cumprod()

    return df


def optimized_momentum_strategy(df, fast_window=10, slow_window=30, threshold=0.02):
    """
    优化版动量策略
    fast_window: 短期动量窗口
    slow_window: 长期动量窗口
    threshold: 动量阈值，避免微小波动产生信号
    """
    df = df.copy()

    # 计算不同周期的动量
    df['momentum_fast'] = df['Close'].pct_change(fast_window)
    df['momentum_slow'] = df['Close'].pct_change(slow_window)

    # 复合信号：短期和长期动量都为正，且超过阈值
    df['signal'] = ((df['momentum_fast'] > threshold) &
                    (df['momentum_slow'] > threshold)).astype(int)

    # 收益率计算
    df['ret'] = df['Close'].pct_change()
    df['strategy_ret'] = df['signal'].shift(1) * df['ret']

    # 交易成本
    df['trade'] = df['signal'].diff().abs()
    df['strategy_ret_after_fee'] = df['strategy_ret'] - df['trade'] * 0.001

    # 累计收益
    df['cum_strategy'] = (1 + df['strategy_ret_after_fee'].fillna(0)).cumprod()
    df['cum_benchmark'] = (1 + df['ret'].fillna(0)).cumprod()

    return df


def dual_momentum_strategy(df, price_window=20, volume_window=10):
    """
    双动量策略：价格动量 + 成交量动量
    """
    df = df.copy()

    # 价格动量
    df['price_momentum'] = df['Close'].pct_change(price_window)

    # 由于AKShare数据可能没有成交量，我们模拟一个成交量序列
    # 在实际应用中，你应该使用真实的成交量数据
    np.random.seed(42)
    df['Volume'] = np.random.randint(10000000, 50000000, len(df))
    df['volume_momentum'] = df['Volume'].pct_change(volume_window)

    # 复合信号：价格动量为正且成交量增加
    df['signal'] = ((df['price_momentum'] > 0.01) &
                    (df['volume_momentum'] > 0)).astype(int)

    # 收益率计算
    df['ret'] = df['Close'].pct_change()
    df['strategy_ret'] = df['signal'].shift(1) * df['ret']

    df['trade'] = df['signal'].diff().abs()
    df['strategy_ret_after_fee'] = df['strategy_ret'] - df['trade'] * 0.001

    df['cum_strategy'] = (1 + df['strategy_ret_after_fee'].fillna(0)).cumprod()
    df['cum_benchmark'] = (1 + df['ret'].fillna(0)).cumprod()

    return df


def mean_reversion_strategy(df, window=20, z_threshold=2.0):
    """
    均值回归策略 - 作为对比
    """
    df = df.copy()

    # 计算滚动均值和标准差
    df['rolling_mean'] = df['Close'].rolling(window=window).mean()
    df['rolling_std'] = df['Close'].rolling(window=window).std()

    # Z-score
    df['z_score'] = (df['Close'] - df['rolling_mean']) / df['rolling_std']

    # 信号：当价格显著低于均值时买入，显著高于时卖出
    df['signal'] = 0
    df.loc[df['z_score'] < -z_threshold, 'signal'] = 1  # 超卖，买入
    df.loc[df['z_score'] > z_threshold, 'signal'] = -1  # 超买，卖出

    # 收益率计算
    df['ret'] = df['Close'].pct_change()
    df['strategy_ret'] = df['signal'].shift(1) * df['ret']

    df['trade'] = df['signal'].diff().abs()
    df['strategy_ret_after_fee'] = df['strategy_ret'] - df['trade'] * 0.001

    df['cum_strategy'] = (1 + df['strategy_ret_after_fee'].fillna(0)).cumprod()
    df['cum_benchmark'] = (1 + df['ret'].fillna(0)).cumprod()

    return df


def calc_detailed_metrics(df, strategy_name):
    """详细绩效指标"""
    df = df.dropna()

    if len(df) == 0:
        return {}

    total_days = len(df)
    years = max(total_days / 252, 0.1)

    try:
        final_value = df['cum_strategy'].iloc[-1]
        ann_ret = final_value ** (1 / years) - 1
        total_ret = final_value - 1
    except:
        return {}

    # 收益率统计
    returns = df['strategy_ret_after_fee'].dropna()
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else np.nan

    # 回撤分析
    running_max = df['cum_strategy'].cummax()
    drawdown = (df['cum_strategy'] / running_max) - 1
    max_dd = drawdown.min()

    # 交易统计
    win_rate = (returns > 0).mean()
    total_trades = df['trade'].sum()

    # Calmar比率
    calmar = ann_ret / abs(max_dd) if max_dd != 0 else np.nan

    return {
        "Strategy": strategy_name,
        "Total Return": f"{total_ret * 100:.2f}%",
        "Annual Return": f"{ann_ret * 100:.2f}%",
        "Annual Volatility": f"{ann_vol * 100:.2f}%",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Max Drawdown": f"{max_dd * 100:.2f}%",
        "Win Rate": f"{win_rate * 100:.2f}%",
        "Total Trades": int(total_trades),
        "Calmar Ratio": f"{calmar:.2f}" if not np.isnan(calmar) else "N/A"
    }


def compare_strategies():
    """比较不同策略"""
    df = load_akshare_data()

    if len(df) == 0:
        print("❌ 数据加载失败")
        return

    print("=" * 60)
    print("A股量化策略比较 (2023年)")
    print("=" * 60)

    # 测试不同策略
    strategies = [
        ("Original Momentum (20 days)", lambda x: backtest_momentum(x, window=20)),
        ("Optimized Momentum (10/30 days)", lambda x: optimized_momentum_strategy(x, 10, 30)),
        ("Dual Momentum", lambda x: dual_momentum_strategy(x)),
        ("Mean Reversion (20 days)", lambda x: mean_reversion_strategy(x, 20)),
    ]

    all_metrics = []

    for name, strategy_func in strategies:
        print(f"测试策略: {name}")
        result_df = strategy_func(df)
        metrics = calc_detailed_metrics(result_df, name)
        if metrics:
            all_metrics.append(metrics)
            print(f"✅ {name} 测试完成")

    # 显示比较结果
    if all_metrics:
        metrics_df = pd.DataFrame(all_metrics)
        print("\n策略绩效比较:")
        print(metrics_df.to_string(index=False))

        # 找出最佳策略
        best_strategy = max(all_metrics, key=lambda x: float(x['Total Return'].rstrip('%')))
        print(f"\n🎯 最佳策略: {best_strategy['Strategy']}")
        print(f"📈 最佳总收益: {best_strategy['Total Return']}")
    else:
        print("❌ 所有策略测试失败")
        return

    # 绘制策略对比图
    plt.figure(figsize=(14, 10))

    # 绘制所有策略的收益曲线
    for name, strategy_func in strategies:
        result_df = strategy_func(df)
        plt.plot(result_df.index, result_df['cum_strategy'], label=name, linewidth=2)

    # 基准曲线
    benchmark_returns = (1 + df['Close'].pct_change().fillna(0)).cumprod()
    plt.plot(df.index, benchmark_returns,
             label='Buy & Hold', linestyle='--', linewidth=2, color='black')

    plt.title('A Share Quantitative Strategies Comparison', fontsize=16)
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 显示基准表现
    benchmark_total_return = (benchmark_returns.iloc[-1] - 1) * 100
    print(f"\n📊 基准(买入持有)总收益: {benchmark_total_return:.2f}%")


def parameter_optimization():
    """参数优化"""
    df = load_akshare_data()
    if len(df) == 0:
        return

    print("\n" + "=" * 50)
    print("动量策略参数优化")
    print("=" * 50)

    # 测试不同的动量窗口
    windows = [5, 10, 20, 30, 50]
    results = []

    for window in windows:
        result_df = backtest_momentum(df, window=window)
        metrics = calc_detailed_metrics(result_df, f"Momentum_{window}days")
        if metrics:
            metrics['Window'] = window
            results.append(metrics)
            print(f"窗口 {window} 天: 总收益 {metrics['Total Return']}")

    if results:
        best_param = max(results, key=lambda x: float(x['Total Return'].rstrip('%')))
        print(f"\n🎯 最佳参数: {best_param['Window']} 天窗口")
        print(f"📈 最佳收益: {best_param['Total Return']}")


if __name__ == "__main__":
    compare_strategies()
    parameter_optimization()