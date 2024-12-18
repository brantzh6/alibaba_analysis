import os
from datetime import datetime

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据存储目录
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Alpha Vantage配置
ALPHA_VANTAGE_CONFIG = {
    'api_key': os.getenv('ALPHA_VANTAGE_API_KEY', 'PERQZCBV3EKV20YI'),
    'base_url': 'https://www.alphavantage.co/query',
    'rate_limit': {
        'calls_per_minute': 5,
        'calls_per_day': 500
    }
}

TUSHARE_CONFIG = {
    'token': os.getenv('TUSHARE_TOKEN', 'fae5fa85c2af62ac68849cd2357b84c83e78345a98a265eb48c4f48a'),  # 请替换为你的token
    'api_url': 'http://api.tushare.pro'
}

# 股票代码配置
STOCK_CONFIG = {
    'symbol': 'BABA',  # 阿里巴巴美股代码
    'hk_symbol': '09988.HK'  # 阿里巴巴港股代码
}

# 数据采集配置
COLLECTION_CONFIG = {
    'market_data_days': 365,  # 市场数据收集天数
    'news_data_days': 30,     # 新闻数据收集天数
    'data_update_interval': 24 # 数据更新间隔（小时）
}

# 代理配置
PROXY_CONFIG = {
    'http': 'http://127.0.0.1:10809',  # 替换为你的代理地址
    'https': 'http://127.0.0.1:10809'  # 替换为你的代理地址
}
