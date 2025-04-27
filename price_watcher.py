import asyncio
import time
import json
from trading_bot import TradingBot
from common_utils import connect_ib, get_price  # 从新模块导入

STATE_FILE = 'state.json'

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"state": "idle", "buy_order_id": None, "sell_order_id": None}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

async def monitor_price():
    trader = TradingBot()
    state = load_state()
    ib = await connect_ib()
    if not ib:
        return

    while True:
        price = await get_price(ib, "AAPL")
        print(f"[{time.ctime()}] 当前 AAPL 价格：{price:.2f}")

        if state["state"] == "idle":
            if price < 205:
                print("📉 价格低于 205，准备买入...")
                buy_order = await trader.place_buy_order("AAPL", 1)
                state["state"] = "waiting_sell"
                state["buy_order_id"] = buy_order["order_id"]
                save_state(state)

        elif state["state"] == "waiting_sell":
            if await trader.is_order_filled(state["buy_order_id"]):
                print("📈 买入订单已成交，准备卖出...")
                sell_order = await trader.place_sell_order("AAPL", 1)
                state["state"] = "waiting_done"
                state["sell_order_id"] = sell_order["order_id"]
                save_state(state)

        elif state["state"] == "waiting_done":
            if await trader.is_order_filled(state["sell_order_id"]):
                print("📊 卖出订单已成交，进入空闲状态...")
                state["state"] = "idle"
                state["buy_order_id"] = None
                state["sell_order_id"] = None
                save_state(state)

        await asyncio.sleep(30)

    ib.disconnect()

if __name__ == '__main__':
    asyncio.run(monitor_price())