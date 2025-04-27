from flask import Flask
from routes import app
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    app.run(debug=True)