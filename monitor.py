# monitor.py
from shared_tasks import monitor_tasks  # 确保 monitor_tasks 在 shared_tasks.py 中定义
from common_utils import connect_ib, get_price
from ibkr_trader import IBKRTrader
import logging
import asyncio
import pytz
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

### 核心监控逻辑（带时间区间判断）
async def monitor_prices():
    while True:
        try:
            # 每隔40秒查询一次所有委托单
            if asyncio.get_running_loop().time() % 40 == 0:
                # 这里暂时保留，后续可以根据实际情况调整
                pass

            eastern = pytz.timezone('US/Eastern')
            now_eastern = datetime.now(eastern)  # 获取当前美国东部时间

            for task in monitor_tasks.copy():
                if not task['active'] or task['order_status'] == '已成交':
                    monitor_tasks.remove(task)
                    continue

                # 解析任务时间并转换为美国东部时间
                start_time = datetime.fromisoformat(task['start_time']).replace(tzinfo=pytz.utc).astimezone(eastern)
                end_time = datetime.fromisoformat(task['end_time']).replace(tzinfo=pytz.utc).astimezone(eastern)

                if start_time <= now_eastern <= end_time:
                    try:
                        price = await get_price(None, task['symbol'])
                        if (task['action'] == 'BUY' and price >= task['trigger_price']) or \
                                (task['action'] == 'SELL' and price <= task['trigger_price']):
                            # 触发条件满足，进行下单操作
                            ib = await connect_ib()
                            if ib:
                                trader = IBKRTrader(task['symbol'], task['action'], task['quantity'])
                                trade_info = await trader.place_order()
                                if trade_info.get('status') == 'error':
                                    logging.error(f"任务 {task['symbol']} 下单出错: {trade_info['message']}")
                                else:
                                    task['order_id'] = trade_info['order_id']
                                    task['order_status'] = '已提交'
                                    logging.info(f"任务 {task['symbol']} 触发，下单信息: {trade_info}")
                                ib.disconnect()
                    except Exception as e:
                        logging.error(f"监控任务 {task['symbol']} 出错: {str(e)}")

            await asyncio.sleep(35)  # 每隔 35 秒检查一次

        except Exception as e:
            logging.error(f"监控价格逻辑出错: {str(e)}")

        await asyncio.sleep(35)  # 每隔 35 秒检查一次
