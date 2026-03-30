from config.settings import get_config
from flask import Flask
from tools import logger
from services.queue_manager import QueueManager

app = Flask(__name__)
queue_manager = QueueManager(max_size=100, max_workers=1)



if __name__ == '__main__':
    current_config = get_config()
    flask_host = current_config.get('FLASK', {}).get('HOST', '0.0.0.0')
    flask_port = current_config.get('FLASK', {}).get('PORT', 5000)
    logger.info("=" * 60)
    logger.info("GitHub代码审查服务启动")
    logger.info("=" * 60)
    logger.info(f"服务地址：http://{flask_host}:{flask_port}")
    logger.info(f"Webhook URL: http://{flask_host}:{flask_port}/webhook/gitlab")
    logger.info(f"健康检查：http://{flask_host}:{flask_port}/health")
    logger.info(f"任务列表：http://{flask_host}:{flask_port}/tasks")
    logger.info(f"状态查询：http://{flask_host}:{flask_port}/model/update/status")
    logger.info(f"配置刷新：http://{flask_host}:{flask_port}/config/refresh")
    logger.info("-" * 60)
    workers = queue_manager.start_workers(start_background_processing)
