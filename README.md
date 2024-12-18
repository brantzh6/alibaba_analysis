# 阿里巴巴财务数据分析系统

## 项目简介
这是一个用于收集和分析阿里巴巴（BABA/09988.HK）财务数据的系统。系统通过多个数据源收集数据，并提供 REST API 进行数据查询。

## 功能特点
- 多数据源采集(Alpha Vantage, Yahoo Finance)
- 自动数据更新
- REST API 支持
- 财务报表分析(年度/季度)
- 市场数据分析

## 安装部署
1. 克隆仓库
bash
git clone https://github.com/your-username/alibaba-analysis.git
cd alibaba-analysis
2. 安装依赖
bash
pip install -r requirements.txt
3. 配置环境变量
bash
cp .env.example .env
编辑 .env 文件，填入必要的 API keys
4. 运行服务
bash
python main.py
5. 访问 API
http://localhost:8000/


## API 文档
服务启动后访问 http://localhost:8000/docs 查看完整的 API 文档

### 主要接口
- GET /api/v1/financial/annual/{fiscal_year} - 获取年度财务数据
- GET /api/v1/financial/quarterly/{year_quarter} - 获取季度财务数据
- GET /api/v1/financial/available-periods - 获取可用的财务报告期间

## 配置说明
配置文件位于 `config/config.py`，主要配置项包括：
- API keys
- 数据更新频率
- 代理设置
- 数据源配置

## 开发说明
项目使用 Python 3.9+ 开发，主要依赖：
- FastAPI
- yfinance
- pandas
- aiohttp

## License
MIT
