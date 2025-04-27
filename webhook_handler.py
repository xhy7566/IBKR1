# webhook_handler.py
import asyncio
from ibkr_trader import IBKRTrader

def handle_webhook(data):
    # 从 webhook 请求中获取数据
    symbol = data.get('symbol', 'AAPL')
    action = data.get('action', 'BUY')
    quantity = data.get('quantity', 1)

    # 创建 IBKRTrader 实例
    trader = IBKRTrader(symbol, action, quantity)

    # 使用 asyncio.run() 来调用异步方法
    trade_info = asyncio.run(trader.place_order())

    # 返回订单信息
    if isinstance(trade_info, dict):
        # 如果 trade_info 是字典类型，表明下单失败
        return trade_info
    else:
        # 如果 trade_info 是 Trade 类型，返回相关的订单信息
        return {
            "symbol": trade_info['symbol'],
            "action": trade_info['action'],
            "quantity": trade_info['quantity'],
            "order_id": trade_info['order_id'],
            "status": trade_info['status'],
            "filled": trade_info['filled'],
            "remaining": trade_info['remaining'],
            "avg_fill_price": trade_info['avg_fill_price'],
            "last_fill_price": trade_info['last_fill_price'],
            "status_message": trade_info['status_message']
        }
