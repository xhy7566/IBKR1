import asyncio
from ib_insync import Stock, MarketOrder, Trade
from common_utils import connect_ib  # 从新模块导入

class TradingBot:
    def __init__(self):
        self.ib = None
        self.connected = False

    async def connect(self):
        if not self.connected:
            self.ib = await connect_ib()
            if self.ib:
                self.connected = True

    async def place_buy_order(self, symbol, quantity):
        await self.connect()
        if not self.connected:
            return {"status": "error", "message": "连接失败"}

        contract = Stock(symbol, 'SMART', 'USD')
        order = MarketOrder('BUY', quantity)
        trade = self.ib.placeOrder(contract, order)
        await self.wait_for_order_fill(trade)
        order_status = trade.orderStatus
        result = {
            "symbol": symbol,
            "action": 'BUY',
            "quantity": quantity,
            "order_id": trade.order.orderId,
            "status": order_status.status,
            "filled": order_status.filled,
            "remaining": order_status.remaining,
            "avg_fill_price": order_status.avgFillPrice,
            "last_fill_price": order_status.lastFillPrice,
            "status_message": order_status.status
        }
        return result

    async def place_sell_order(self, symbol, quantity):
        await self.connect()
        if not self.connected:
            return {"status": "error", "message": "连接失败"}

        contract = Stock(symbol, 'SMART', 'USD')
        order = MarketOrder('SELL', quantity)
        trade = self.ib.placeOrder(contract, order)
        await self.wait_for_order_fill(trade)
        order_status = trade.orderStatus
        result = {
            "symbol": symbol,
            "action": 'SELL',
            "quantity": quantity,
            "order_id": trade.order.orderId,
            "status": order_status.status,
            "filled": order_status.filled,
            "remaining": order_status.remaining,
            "avg_fill_price": order_status.avgFillPrice,
            "last_fill_price": order_status.lastFillPrice,
            "status_message": order_status.status
        }
        return result

    async def wait_for_order_fill(self, trade, timeout=30):
        for _ in range(timeout):
            await asyncio.sleep(1)
            if trade.orderStatus.status in ['Filled', 'Cancelled', 'Inactive']:
                break

    async def is_order_filled(self, order_id):
        await self.connect()
        if not self.connected:
            return False

        for trade in self.ib.trades():
            if trade.order.orderId == order_id:
                return trade.orderStatus.status == 'Filled'
        return False

    def disconnect(self):
        if self.connected and self.ib.isConnected():
            self.ib.disconnect()
            self.connected = False
