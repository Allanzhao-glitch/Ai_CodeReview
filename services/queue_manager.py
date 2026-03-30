"""队列管理服务"""
import queue
import threading
from typing import Dict, List, Optional
from models.task import Task
from tools import logger


class QueueManager:
    """队列管理服务"""
    def __init__(self, max_size: int, max_workers: int):
        self.review_queue = queue.Queue(maxsize=max_size)
        self.processing_lock = threading.Lock()
        self.processing_task: Dict[str, Task] = {}
        self.max_workers = max_workers
        self.workers: List[threading.Thread] = []
        self.running = False

        self.MAX_CONCURRENT_WORKERS = 1
        self.QUEUE_TIMEOUT = 300
        self.TASK_RETRY_COUNT = 3
        self.MODEL_RATE_LIMIT = {
            'deepseek': 60,
            'default': 60
        }
        
