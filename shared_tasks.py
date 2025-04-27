# shared_tasks.py
import time
import logging
monitor_tasks = []  # 定义一个空列表用于存储监控任务

logger = logging.getLogger(__name__)

def monitor_orders(ib, interval=30):
    """
    定时监控 IBKR 的委托单状态
    """
    while True:
        try:
            # 获取所有委托单
            orders = ib.orders()
            for order in orders:
                status = ib.orderStatus(order)
                logger.info(f"委托单: {order}, 状态: {status.status}")
                # 在这里处理委托单状态逻辑
                if status.status == 'Filled':  # 如果成交
                    logger.info(f"委托单 {order} 已成交，移除监控")
                    # 删除已成交的委托单
                    orders.remove(order)
        except Exception as e:
            logger.error(f"监控委托单失败: {e}")

        # 等待下一个周期
        time.sleep(interval)
