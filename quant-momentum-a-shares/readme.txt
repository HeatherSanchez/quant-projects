A股动量策略回测分析 (Momentum Strategy on China A-shares)

一、项目简介
本项目基于过去20日价格动量信号，在沪深300 ETF（代码：510300.SS）上进行历史回测，验证动量策略在A股市场的有效性。

二、策略逻辑
- 动量定义：过去20个交易日累计收益率
- 交易规则：
  - 若动量 > 0，则持有下一日；
  - 若动量 ≤ 0，则空仓；
- 交易成本：单次换仓手续费 0.1%

三、使用技术
Python, pandas, numpy, matplotlib, yfinance

四、运行步骤
1. 克隆项目并安装依赖：
    pip install pandas numpy matplotlib yfinance
2. 下载数据：
    python src/data_fetch.py
3. 运行回测：
    python src/backtest_pandas.py
4. 查看结果：
    控制台输出绩效指标（年化收益、波动率、Sharpe、回撤、胜率）
    (弹出收益曲线图)

五、示例结果
指标	        数值
年化收益率	12.45%
年化波动率	17.30%
Sharpe	    0.72
最大回撤	    -9.85%
胜率	        53.42%

六、项目总结
动量策略在A股中存在一定有效性；
但收益不稳定，对手续费较敏感；

七、后续计划：
加入多标的组合；
考虑风险控制与多因子模型。