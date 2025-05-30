# webhook.py
import logging
from flask import Flask, render_template
import asyncio
from monitor import monitor_prices  # 修复：从 monitor.py 而非 app.py 导入

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# 存储所有监控任务的列表
monitor_tasks = []

@app.route('/')
def index():
    return render_template('main.html')

# 其他路由和业务逻辑保持不变

if __name__ == '__main__':
    asyncio.create_task(monitor_prices())
    app.run(port=5000)
