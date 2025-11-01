# test_akshare.py - 不依赖虚拟环境，测试AKShare
import sys
import subprocess
import os


def setup_environment():
    """检查并安装必要的包"""
    try:
        import akshare as ak
        print("✅ AKShare 已安装")
        return True
    except ImportError:
        print("❌ AKShare 未安装，正在安装...")
        try:
            # 直接安装到用户目录
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "akshare", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple/",
                 "--user"])
            print("✅ AKShare 安装成功")
            return True
        except:
            print("❌ 安装失败")
            return False


def test_akshare():
    """测试AKShare数据获取"""
    try:
        import akshare as ak
        import pandas as pd

        print("测试AKShare获取A股数据...")

        # 获取沪深300ETF数据
        df = ak.fund_etf_hist_em(symbol="510300", period="daily", start_date="20230101", end_date="20231231")

        if len(df) > 0:
            print(f"✅ 成功获取数据，共 {len(df)} 条记录")
            print("\n数据预览:")
            print(df.head())

            # 保存数据
            os.makedirs("data", exist_ok=True)
            df.to_csv("data/510300_akshare.csv")
            print("✅ 数据已保存到 data/510300_akshare.csv")
            return True
        else:
            print("❌ 获取的数据为空")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    if setup_environment():
        test_akshare()