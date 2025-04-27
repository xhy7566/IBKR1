# common_utils.py
import logging
import random
from ib_insync import IB
import yfinance as yf
import nest_asyncio

nest_asyncio.apply()

logger = logging.getLogger(__name__)

def connect_ib(max_retries=5):
    """
    同步版本的 IBKR 连接函数
    """
    ib = IB()
    retries = 0
    while retries < max_retries:
        clientId = random.randint(1, 1000)
        try:
            ib.connect('127.0.0.1', 4002, clientId=clientId)
            logger.info(f"成功连接到 IBKR，客户端 ID: {clientId}")
            return ib
        except Exception as e:
            logger.error(f"连接出错，客户端 ID {clientId} 可能被占用，具体错误信息: {str(e)}，重试 {retries + 1}/{max_retries}...")
            retries += 1
    logger.error("达到最大重试次数，连接失败。")
    return None

def get_price(symbol):
    """
    同步版本的获取股价函数
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1]
        return None
    except Exception as e:
        logger.error(f"获取股价出错: {e}")
        return None