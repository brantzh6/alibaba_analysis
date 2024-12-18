# data_collector/market_data.py
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
from .base import BaseCollector
from config.config import STOCK_CONFIG, PROXY_CONFIG, ALPHA_VANTAGE_CONFIG
import time
import random

class MarketDataCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.symbol = STOCK_CONFIG['symbol']
        self.hk_symbol = STOCK_CONFIG['hk_symbol']
        self.proxies = PROXY_CONFIG
        self.api_key = ALPHA_VANTAGE_CONFIG['api_key']
        self.base_url = ALPHA_VANTAGE_CONFIG['base_url']
    
    async def collect(self):
        """收集市场数据"""
        market_data = None
        
        # 定义数据源优先级
        data_sources = [
            self._collect_from_alpha_vantage,  # Alpha Vantage 作为主要数据源
            self._collect_from_yfinance,       # YFinance 作为备选
            self._collect_from_basic_web       # 基础网页爬虫作为最后备选
        ]
        
        for source in data_sources:
            try:
                print(f"尝试从 {source.__name__} 获取数据...")
                # 添加随机延迟，避免请求过快
                time.sleep(random.uniform(1, 3))
                market_data = source()
                if market_data and self._validate_data(market_data):
                    print(f"成功从 {source.__name__} 获取数据")
                    break
                else:
                    print(f"{source.__name__} 返回的数据无效，尝试下一个数据源")
            except Exception as e:
                print(f"{source.__name__} 获取数据失败: {str(e)}")
                continue
        
        if market_data:
            try:
                print("正在保存市场数据...")
                self.save_data(market_data, 'market_data.json')
                print("市场数据保存完成")
            except Exception as e:
                print(f"保存数据失败: {str(e)}")
        
        return market_data
    
    def _collect_from_yfinance(self):
        """从 yfinance 获取数据"""
        us_ticker = yf.Ticker(self.symbol)
        hk_ticker = yf.Ticker(self.hk_symbol)
        
        us_hist = us_ticker.history(period="1y", proxy=self.proxies['https'])
        time.sleep(1)
        hk_hist = hk_ticker.history(period="1y", proxy=self.proxies['https'])
        
        us_info = us_ticker.info if hasattr(us_ticker, 'info') else {}
        
        return {
            'us_market': {
                'history': us_hist.reset_index().to_dict(orient='records') if not us_hist.empty else [],
                'info': {
                    'market_cap': us_info.get('marketCap'),
                    'pe_ratio': us_info.get('trailingPE'),
                    'price': us_info.get('regularMarketPrice'),
                    'volume': us_info.get('regularMarketVolume')
                } if us_info else {}
            },
            'hk_market': {
                'history': hk_hist.reset_index().to_dict(orient='records') if not hk_hist.empty else []
            },
            'collection_time': datetime.now().isoformat(),
            'data_source': 'yfinance'
        }
    
    def _collect_from_alpha_vantage(self):
        """从 Alpha Vantage 获取数据"""
        try:
            # 获取日线数据
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': self.symbol,
                'outputsize': 'full',
                'apikey': self.api_key
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                proxies=self.proxies,
                timeout=10  # 添加超时设置
            )
            response.raise_for_status()  # 检查响应状态
            us_data = response.json()
            
            time.sleep(12)  # Alpha Vantage API 限制
            
            # 获取公司概况
            params = {
                'function': 'OVERVIEW',
                'symbol': self.symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                proxies=self.proxies,
                timeout=10
            )
            response.raise_for_status()
            us_info = response.json()
            
            # 处理数据
            history_data = []
            if 'Time Series (Daily)' in us_data:
                for date, values in us_data['Time Series (Daily)'].items():
                    history_data.append({
                        'Date': date,
                        'Open': float(values['1. open']),
                        'High': float(values['2. high']),
                        'Low': float(values['3. low']),
                        'Close': float(values['4. close']),
                        'Volume': float(values['5. volume'])
                    })
                history_data = sorted(history_data, key=lambda x: x['Date'], reverse=True)[:365]
            
            return {
                'us_market': {
                    'history': history_data,
                    'info': {
                        'market_cap': us_info.get('MarketCapitalization'),
                        'pe_ratio': us_info.get('PERatio'),
                        'price_to_book': us_info.get('PriceToBookRatio'),
                        'dividend_yield': us_info.get('DividendYield'),
                        'profit_margin': us_info.get('ProfitMargin'),
                        'beta': us_info.get('Beta')
                    } if us_info else {}
                },
                'collection_time': datetime.now().isoformat(),
                'data_source': 'alpha_vantage'
            }
        except Exception as e:
            print(f"Alpha Vantage 数据获取错误: {str(e)}")
            return None
    
    def _collect_from_basic_web(self):
        """从基础网页获取数据（作为最后的备选）"""
        # 这里可以添加一个基础的网页爬虫作为备选
        # 例如从雅虎财经的网页直接爬取数据
        pass
    
    def _validate_data(self, data):
        """验证数据是否有效"""
        if not data:
            return False
        
        # 检查必要的字段
        if 'us_market' not in data:
            return False
        
        # 检查历史数据
        if not data['us_market'].get('history'):
            return False
        
        # 检查是否有最新价格
        latest_data = data['us_market'].get('info', {})
        if not latest_data.get('price') and not latest_data.get('market_cap'):
            return False
        
        return True