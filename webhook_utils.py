import logging
from flask import jsonify
from common_utils import connect_ib

logger = logging.getLogger(__name__)

def handle_webhook_request(data):
    from webhook_handler import handle_webhook  # 延迟导入
    logger.debug("收到Webhook数据：%s", data)

    try:
        trade = handle_webhook(data)  # 处理 webhook 数据并下单
        if isinstance(trade, dict):
            logger.info('下单成功：%s', trade["status"])
            return jsonify({
                'status': 'order scheduled',
                'trade_id': trade["order_id"],
                'action': data.get('action'),
                'symbol': data.get('symbol'),
                'quantity': data.get('quantity')
            })
        else:
            logger.info('下单成功：%s', trade.orderStatus.status)
            return jsonify({
                'status': 'order scheduled',
                'trade_id': trade.orderId,
                'action': data.get('action'),
                'symbol': data.get('symbol'),
                'quantity': data.get('quantity')
            })
    except Exception as e:
        logger.error("下单出错: %s", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500