# data_collector/financial_data.py
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime
from .base import BaseCollector
from config.config import STOCK_CONFIG, PROXY_CONFIG, ALPHA_VANTAGE_CONFIG
import time
import random

class FinancialDataCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.symbol = STOCK_CONFIG['symbol']
        self.proxies = PROXY_CONFIG
        self.api_key = ALPHA_VANTAGE_CONFIG['api_key']
        self.base_url = ALPHA_VANTAGE_CONFIG['base_url']
    
    async def collect(self):
        """收集财务数据"""
        all_financial_data = []
        
        data_sources = [
            self._collect_from_alpha_vantage,
            self._collect_from_yfinance
        ]
        
        for source in data_sources:
            try:
                print(f"尝试从 {source.__name__} 获取财务数据...")
                time.sleep(random.uniform(1, 3))
                financial_data = source()
                if financial_data and self._validate_data(financial_data):
                    print(f"成功从 {source.__name__} 获取财务数据")
                    all_financial_data.append(financial_data)
                else:
                    print(f"{source.__name__} 返回的数据无效")
            except Exception as e:
                print(f"{source.__name__} 获取财务数据失败: {str(e)}")
                continue
        
        if all_financial_data:
            merged_data = self._merge_financial_data(all_financial_data)
            try:
                print("正在保存合并后的财务数据...")
                self.save_data(merged_data, 'financial_data.json')
                print("财务数据保存完成")
                return merged_data
            except Exception as e:
                print(f"保存数据失败: {str(e)}")
        
        return None

    def _collect_from_yfinance(self):
        """从 yfinance 获取财务数据（包括季度数据）"""
        try:
            ticker = yf.Ticker(self.symbol)
            
            # 获取季度财务报表
            quarterly_financials = ticker.quarterly_financials
            quarterly_balance_sheet = ticker.quarterly_balance_sheet
            quarterly_cashflow = ticker.quarterly_cashflow
            
            # 获取年度财务报表
            annual_financials = ticker.financials
            annual_balance_sheet = ticker.balance_sheet
            annual_cashflow = ticker.cashflow
            
            # 获取收益预估
            earnings = ticker.earnings
            earnings_dates = ticker.earnings_dates
            
            return {
                'quarterly_data': {
                    'income_statement': quarterly_financials.reset_index().to_dict(orient='records') if not quarterly_financials.empty else [],
                    'balance_sheet': quarterly_balance_sheet.reset_index().to_dict(orient='records') if not quarterly_balance_sheet.empty else [],
                    'cash_flow': quarterly_cashflow.reset_index().to_dict(orient='records') if not quarterly_cashflow.empty else []
                },
                'annual_data': {
                    'income_statement': annual_financials.reset_index().to_dict(orient='records') if not annual_financials.empty else [],
                    'balance_sheet': annual_balance_sheet.reset_index().to_dict(orient='records') if not annual_balance_sheet.empty else [],
                    'cash_flow': annual_cashflow.reset_index().to_dict(orient='records') if not annual_cashflow.empty else []
                },
                'earnings': {
                    'historical': earnings.to_dict(orient='records') if not earnings.empty else [],
                    'upcoming': earnings_dates.reset_index().to_dict(orient='records') if not earnings_dates.empty else []
                },
                'key_metrics': self._calculate_key_metrics(ticker),
                'collection_time': datetime.now().isoformat(),
                'data_source': 'yfinance'
            }
        except Exception as e:
            print(f"YFinance 数据获取错误: {str(e)}")
            return None

    def _collect_from_alpha_vantage(self):
        """从 Alpha Vantage 获取财务数据（包括季度数据）"""
        try:
            # 获取季度收入报表
            income_stmt_q = self._get_alpha_vantage_data('INCOME_STATEMENT', period='quarterly')
            time.sleep(12)
            
            # 获取季度资产负债表
            balance_sheet_q = self._get_alpha_vantage_data('BALANCE_SHEET', period='quarterly')
            time.sleep(12)
            
            # 获取季度现金流量表
            cash_flow_q = self._get_alpha_vantage_data('CASH_FLOW', period='quarterly')
            time.sleep(12)
            
            # 获取年度数据
            income_stmt = self._get_alpha_vantage_data('INCOME_STATEMENT')
            time.sleep(12)
            balance_sheet = self._get_alpha_vantage_data('BALANCE_SHEET')
            time.sleep(12)
            cash_flow = self._get_alpha_vantage_data('CASH_FLOW')
            
            return {
                'quarterly_data': {
                    'income_statement': income_stmt_q.get('quarterlyReports', []),
                    'balance_sheet': balance_sheet_q.get('quarterlyReports', []),
                    'cash_flow': cash_flow_q.get('quarterlyReports', [])
                },
                'annual_data': {
                    'income_statement': income_stmt.get('annualReports', []),
                    'balance_sheet': balance_sheet.get('annualReports', []),
                    'cash_flow': cash_flow.get('annualReports', [])
                },
                'collection_time': datetime.now().isoformat(),
                'data_source': 'alpha_vantage'
            }
        except Exception as e:
            print(f"Alpha Vantage 数据获取错误: {str(e)}")
            return None

    def _get_alpha_vantage_data(self, function, period='annual'):
        """从 Alpha Vantage 获取特定类型的数据"""
        params = {
            'function': function,
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
        return response.json()

    def _merge_financial_data(self, data_list):
        """合并来自不同数据源的财务数据"""
        merged_data = {
            'quarterly_data': {
                'income_statement': [],
                'balance_sheet': [],
                'cash_flow': []
            },
            'annual_data': {
                'income_statement': [],
                'balance_sheet': [],
                'cash_flow': []
            },
            'earnings': {
                'historical': [],
                'upcoming': []
            },
            'key_metrics': {},
            'collection_time': datetime.now().isoformat(),
            'data_sources': []
        }
        
        # 合并数据
        for data in data_list:
            source = data.get('data_source', 'unknown')
            merged_data['data_sources'].append(source)
            
            # 合并季度数据
            if 'quarterly_data' in data:
                for report_type in ['income_statement', 'balance_sheet', 'cash_flow']:
                    if report_type in data['quarterly_data']:
                        merged_data['quarterly_data'][report_type].extend(
                            data['quarterly_data'][report_type]
                        )
            
            # 合并年度数据
            if 'annual_data' in data:
                for report_type in ['income_statement', 'balance_sheet', 'cash_flow']:
                    if report_type in data['annual_data']:
                        merged_data['annual_data'][report_type].extend(
                            data['annual_data'][report_type]
                        )
            
            # 合并收益数据
            if 'earnings' in data:
                merged_data['earnings']['historical'].extend(
                    data['earnings'].get('historical', [])
                )
                merged_data['earnings']['upcoming'].extend(
                    data['earnings'].get('upcoming', [])
                )
            
            # 合并关键指标
            if 'key_metrics' in data:
                merged_data['key_metrics'].update(data['key_metrics'])
        
        # 去重和排序
        for period in ['quarterly_data', 'annual_data']:
            for report_type in ['income_statement', 'balance_sheet', 'cash_flow']:
                # 使用 fiscalDateEnding 或 Date 作为唯一标识
                unique_reports = {}
                for report in merged_data[period][report_type]:
                    date = report.get('fiscalDateEnding') or report.get('Date')
                    if date:
                        unique_reports[date] = report
                merged_data[period][report_type] = sorted(
                    unique_reports.values(),
                    key=lambda x: x.get('fiscalDateEnding') or x.get('Date'),
                    reverse=True
                )
        
        # 添加数据质量指标
        merged_data['data_quality'] = {
            'number_of_sources': len(data_list),
            'sources': merged_data['data_sources'],
            'quarterly_data_points': {
                'income_statement': len(merged_data['quarterly_data']['income_statement']),
                'balance_sheet': len(merged_data['quarterly_data']['balance_sheet']),
                'cash_flow': len(merged_data['quarterly_data']['cash_flow'])
            },
            'annual_data_points': {
                'income_statement': len(merged_data['annual_data']['income_statement']),
                'balance_sheet': len(merged_data['annual_data']['balance_sheet']),
                'cash_flow': len(merged_data['annual_data']['cash_flow'])
            },
            'last_update': datetime.now().isoformat()
        }
        
        return merged_data

    def _validate_data(self, data):
        """验证数据是否有效"""
        if not data:
            return False
        
        # 检查是否至少有一个季度或年度报表
        has_quarterly = False
        has_annual = False
        
        if 'quarterly_data' in data:
            for report_type in ['income_statement', 'balance_sheet', 'cash_flow']:
                if data['quarterly_data'].get(report_type):
                    has_quarterly = True
                    break
        
        if 'annual_data' in data:
            for report_type in ['income_statement', 'balance_sheet', 'cash_flow']:
                if data['annual_data'].get(report_type):
                    has_annual = True
                    break
        
        return has_quarterly or has_annual