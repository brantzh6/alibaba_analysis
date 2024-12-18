# data_collector/base.py
from abc import ABC, abstractmethod
import aiohttp
import asyncio
from datetime import datetime
import json
import os
from config.config import DATA_DIR

class BaseCollector(ABC):
    def __init__(self):
        self.session = None
        
    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    def save_data(self, data, filename):
        """保存数据到JSON文件"""
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_data(self, filename):
        """从JSON文件加载数据"""
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    @abstractmethod
    async def collect(self):
        """收集数据的抽象方法"""
        pass