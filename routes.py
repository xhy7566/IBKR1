from flask import Flask, request, jsonify
import logging
from common_utils import connect_ib, get_price
from place_order import place_order

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/add_task', methods=['POST'])
def add_task():
    """
    添加任务的后端接口
    """
    try:
        # 从前端获取任务信息
        data = request.get_json()
        symbol = data.get('symbol')
        trigger_price = float(data.get('trigger_price'))
        action_type = data.get('action_type')
        quantity = int(data.get('quantity'))

        # 调用工具函数连接 IBKR
        ib = connect_ib()
        if not ib:
            return jsonify({"error": "无法连接到 IBKR"}), 500

        # 调用工具函数获取股票价格
        current_price = get_price(symbol)
        if current_price is None:
            return jsonify({"error": "无法获取股票价格"}), 500

        # 调用下单逻辑
        if action_type == 'buy' and current_price <= trigger_price:
            place_order(ib, symbol, 'BUY', quantity)
        elif action_type == 'sell' and current_price >= trigger_price:
            place_order(ib, symbol, 'SELL', quantity)

        return jsonify({"message": "任务添加成功"}), 200
    except Exception as e:
        logger.error(f"添加任务失败: {e}")
        return jsonify({"error": "添加任务失败"}), 500