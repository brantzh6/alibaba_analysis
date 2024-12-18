# main.py
import asyncio
import os
from data_collector.market_data import MarketDataCollector
from data_collector.financial_data import FinancialDataCollector
from data_collector.news_data import NewsDataCollector
from datetime import datetime
import json
from config.config import DATA_DIR
from api.server import start_api_server
import threading

async def collect_data():
    """收集市场和财务数据"""
    print("开始收集数据...")
    
    # 创建数据收集器实例
    market_collector = MarketDataCollector()
    financial_collector = FinancialDataCollector()
    
    # 并行收集数据
    market_data, financial_data = await asyncio.gather(
        market_collector.collect(),
        financial_collector.collect()
    )
    
    print("数据收集完成")
    return market_data, financial_data

def run_api_server():
    """在单独的线程中运行 API 服务器"""
    start_api_server()

async def main():
    # 启动 API 服务器（在单独的线程中）
    api_thread = threading.Thread(target=run_api_server)
    api_thread.daemon = True  # 设置为守护线程，这样主程序退出时会自动结束
    api_thread.start()
    
    # 定期收集数据
    while True:
        try:
            await collect_data()
            # 等待 24 小时后再次收集
            await asyncio.sleep(24 * 60 * 60)
        except Exception as e:
            print(f"数据收集出错: {str(e)}")
            # 出错后等待 1 小时再试
            await asyncio.sleep(60 * 60)

if __name__ == "__main__":
    asyncio.run(main())