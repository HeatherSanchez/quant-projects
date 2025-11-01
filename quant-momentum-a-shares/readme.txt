A股量化动量策略回测系统

一个基于Python的A股量化投资回测框架，专门用于测试和优化动量策略在A股市场的表现。

一、项目特性

- A股数据获取 - 支持AKShare获取真实的A股ETF数据
- 多策略回测 - 动量策略、均值回归策略等
- 可视化分析 - 收益曲线、回撤分析、策略对比
- 参数优化 - 自动寻找最优策略参数
- 详细指标 - 夏普比率、最大回撤、胜率等完整绩效评估

二、 项目结构
quant-momentum-a-shares/
├── src/ # 源代码目录
│ ├── data_fetch.py # 数据获取模块
│ ├── backtest_pandas.py # 基础回测框架
│ ├── backtest_akshare.py # AKShare数据回测
│ └── backtest_optimized.py # 优化策略回测
├── data/ # 数据存储目录
│ └── 510300_akshare.csv # A股ETF历史数据
├── requirements.txt # 项目依赖
└── README.md # 项目说明

三、安装指南

环境要求
- Python 3.9+
- PyCharm (推荐) 或 VS Code

1. 克隆项目
git clone <项目地址>
cd quant-momentum-a-shares

2. 创建虚拟环境
python -m venv .venv
# Windows激活
.venv\Scripts\activate
# Mac/Linux激活  
source .venv/bin/activate

3. 安装依赖
pip install -r requirements.txt

4. 在PyCharm中配置
-打开项目
-设置Python解释器为 .venv
-安装项目依赖

四、使用方法
1. 获取数据
python src/data_fetch.py
2. 运行基础回测
python src/backtest_akshare.py
3. 运行优化策略比较
python src/backtest_optimized.py

五、策略介绍
动量策略 (Momentum Strategy)
-原理: 追涨杀跌，认为过去表现好的资产未来会继续表现好
-信号: 过去N日收益率为正时买入，为负时空仓
-参数: 动量窗口(20日)、交易成本(0.1%)

均值回归策略 (Mean Reversion)
-原理: 价格围绕均值波动，偏离过多时会回归
-信号: Z-score超过阈值时反向交易
-参数: 滚动窗口(20日)、Z-score阈值(2.0)

双动量策略 (Dual Momentum)
-原理: 结合价格动量和成交量动量
-信号: 价格和成交量同时显示动量时交易
-参数: 价格窗口(20日)、成交量窗口(10日)

六、绩效指标
系统提供完整的绩效评估：
-总收益率 (Total Return)
-年化收益率 (Annual Return)
-年化波动率 (Annual Volatility)
-夏普比率 (Sharpe Ratio)
-最大回撤 (Max Drawdown)
-胜率 (Win Rate)
-交易次数 (Total Trades)
-Calmar比率 (Calmar Ratio)

七、自定义策略
在 backtest_optimized.py 中添加新策略：
def my_custom_strategy(df, param1=10, param2=20):
    df = df.copy()
    # 你的策略逻辑
    df['signal'] = ...  # 生成交易信号
    df['ret'] = df['Close'].pct_change()
    df['strategy_ret'] = df['signal'].shift(1) * df['ret']
    return df

八、 依赖包
项目主要依赖：
-pandas==1.5.3 - 数据处理
-numpy==1.24.3 - 数值计算
-matplotlib==3.7.1 - 数据可视化
-akshare - A股数据获取
-yfinance==0.2.18 - 备用数据源

完整依赖见 requirements.txt