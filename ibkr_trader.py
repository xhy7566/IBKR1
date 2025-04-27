import asyncio
from ib_insync import Stock, MarketOrder, Trade
from common_utils import connect_ib  # 从新模块导入

class IBKRTrader:
    def __init__(self, symbol, action, quantity):
        self.symbol = symbol
        self.action = action
        self.quantity = quantity
        self.ib = None
        self.connected = False

    async def connect(self):
        if not self.connected:
            self.ib = await connect_ib()
            if self.ib:
                self.connected = True

    async def place_order(self, timeout=30):
        await self.connect()
        if not self.connected:
            return {"status": "error", "message": "连接失败"}

        contract = Stock(self.symbol, 'SMART', 'USD')
        order = MarketOrder(self.action, self.quantity)

        try:
            trade = self.ib.placeOrder(contract, order)

            print(f"Trade 类型: {type(trade)}")
            print(f"初始状态: {trade.orderStatus}")

            # 持续等待成交或被拒绝（最多等待指定时间）
            for _ in range(timeout):  # 每秒检查一次
                await asyncio.sleep(1)
                if trade.orderStatus.status in ['Filled', 'Cancelled', 'Inactive']:
                    break

            order_status = trade.orderStatus
            print(f"最终状态: {order_status}")

            result = {
                "symbol": self.symbol,
                "action": self.action,
                "quantity": self.quantity,
                "order_id": trade.order.orderId,
                "status": order_status.status,
                "filled": order_status.filled,
                "remaining": order_status.remaining,
                "avg_fill_price": order_status.avgFillPrice,
                "last_fill_price": order_status.lastFillPrice,
                "status_message": order_status.status
            }
            return result

        except Exception as e:
            print(f"下单出错: {e}")
            return {"status": "error", "message": str(e)}

    async def get_order_status(self, order_id):
        await self.connect()
        if not self.connected:
            return {"status": "error", "message": "连接失败"}

        for trade in self.ib.trades():
            if trade.order.orderId == order_id:
                order_status = trade.orderStatus
                result = {
                    "order_id": order_id,
                    "status": order_status.status,
                    "filled": order_status.filled,
                    "remaining": order_status.remaining,
                    "avg_fill_price": order_status.avgFillPrice,
                    "last_fill_price": order_status.lastFillPrice,
                    "status_message": order_status.status
                }
                return result
        return {"status": "未找到订单", "message": f"未找到订单 ID 为 {order_id} 的订单"}

    def disconnect(self):
        if self.connected and self.ib.isConnected():
            self.ib.disconnect()
            self.connected = False