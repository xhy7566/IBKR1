from ib_insync import MarketOrder, Stock
import logging

logger = logging.getLogger(__name__)

def place_order(ib, symbol, action, quantity):
    """
    下单函数
    """
    try:
        stock = Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(stock)
        order = MarketOrder(action, quantity)
        trade = ib.placeOrder(stock, order)
        logger.info(f"成功下单: {trade}")
    except Exception as e:
        logger.error(f"下单失败: {e}")