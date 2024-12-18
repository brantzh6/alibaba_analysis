from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

app = FastAPI(
    title="阿里巴巴财务数据 API",
    description="提供阿里巴巴历史财务数据查询服务",
    version="1.0.0"
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
FINANCIAL_DATA_PATH = DATA_DIR / "financial_data.json"

def load_financial_data() -> Dict[str, Any]:
    """加载财务数据"""
    try:
        with open(FINANCIAL_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"无法加载财务数据: {str(e)}")

@app.get("/")
async def root():
    """API 根路径"""
    return {"message": "阿里巴巴财务数据 API 服务正在运行"}

@app.get("/api/v1/financial/annual/{fiscal_year}")
async def get_annual_financial_data(fiscal_year: str):
    """获取指定财年的财务数据"""
    try:
        # 加载数据
        financial_data = load_financial_data()
        
        # 获取年度数据
        annual_data = financial_data.get('annual_data', {})
        
        # 查找指定财年的数据
        result = {
            'income_statement': [],
            'balance_sheet': [],
            'cash_flow': []
        }
        
        # 处理每种报表
        for report_type in result.keys():
            for report in annual_data.get(report_type, []):
                if fiscal_year in report.get('fiscalDateEnding', ''):
                    result[report_type].append(report)
        
        if not any(result.values()):
            raise HTTPException(status_code=404, detail=f"未找到 {fiscal_year} 财年的数据")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/financial/quarterly/{year_quarter}")
async def get_quarterly_financial_data(year_quarter: str):
    """获取指定季度的财务数据"""
    try:
        # 加载数据
        financial_data = load_financial_data()
        
        # 获取季度数据
        quarterly_data = financial_data.get('quarterly_data', {})
        
        # 查找指定季度的数据
        result = {
            'income_statement': [],
            'balance_sheet': [],
            'cash_flow': []
        }
        
        # 处理每种报表
        for report_type in result.keys():
            for report in quarterly_data.get(report_type, []):
                if year_quarter in report.get('fiscalDateEnding', ''):
                    result[report_type].append(report)
        
        if not any(result.values()):
            raise HTTPException(status_code=404, detail=f"未找到 {year_quarter} 季度的数据")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/financial/available-periods")
async def get_available_periods():
    """获取可用的财务报告期间"""
    try:
        financial_data = load_financial_data()
        
        # 收集所有可用的报告期间
        annual_periods = set()
        quarterly_periods = set()
        
        # 处理年度数据
        annual_data = financial_data.get('annual_data', {})
        for report_type in ['income_statement', 'balance_sheet', 'cash_flow']:
            for report in annual_data.get(report_type, []):
                if 'fiscalDateEnding' in report:
                    annual_periods.add(report['fiscalDateEnding'])
        
        # 处理季度数据
        quarterly_data = financial_data.get('quarterly_data', {})
        for report_type in ['income_statement', 'balance_sheet', 'cash_flow']:
            for report in quarterly_data.get(report_type, []):
                if 'fiscalDateEnding' in report:
                    quarterly_periods.add(report['fiscalDateEnding'])
        
        return {
            'annual_periods': sorted(list(annual_periods), reverse=True),
            'quarterly_periods': sorted(list(quarterly_periods), reverse=True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_api_server():
    """启动 API 服务器"""
    print("启动 API 服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    start_api_server()
