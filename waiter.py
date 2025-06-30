# waiter.py
from flask import Flask
from collector.input import InputCollector

def create_app():
    app = Flask(__name__)

    # 创建输入采集器并注册路由
    collector = InputCollector(app)
    collector.register_routes()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
