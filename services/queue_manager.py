import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import queue
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from models.task import Task
from tools import logger


@dataclass
class QueueConfig:
    max_size: int = 100
    max_workers: int = 4
    timeout: int = 300
    retry_count: int = 3
    rate_limits: Dict[str, int] = None

    def __post_init__(self):
        if self.rate_limits is None:
            self.rate_limits = {'deepseek': 60, 'default': 60}


class QueueManager:
    _instance: Optional['QueueManager'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, max_size: int = 100, max_workers: int = 4):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        self.config = QueueConfig(max_size=max_size, max_workers=max_workers)
        self.review_queue: queue.Queue[tuple] = queue.Queue(maxsize=max_size)
        self.processing_lock = threading.RLock()
        self.processing_tasks: Dict[str, Task] = {}
        self.max_workers = max_workers
        self.workers: List[threading.Thread] = []
        self.running = False

    def add_task(self, task: Task) -> bool:
        try:
            with self.processing_lock:
                self.processing_tasks[task.task_id] = task

            if self.review_queue.qsize() >= int(self.review_queue.maxsize * 0.8):
                logger.warning(f"队列接近容量上限：{self.review_queue.qsize()}/{self.review_queue.maxsize}")

            self.review_queue.put((task.task_id, task.payload_data, task.object_kind), timeout=10)
            logger.info(f"添加任务成功：{task.task_id}")
            return True
        except queue.Full:
            logger.error(f"队列已满，无法添加任务：{task.task_id}")
            return False

    def get_queue_status(self) -> Dict[str, Any]:
        with self.processing_lock:
            status_counts: Dict[str, int] = {}
            worker_status: Dict[int, int] = {}

            for task in self.processing_tasks.values():
                status = task.status
                status_counts[status] = status_counts.get(status, 0) + 1

                if task.worker_id:
                    worker_id = task.worker_id
                    worker_status[worker_id] = worker_status.get(worker_id, 0) + 1

            queue_size = self.review_queue.qsize()
            max_size = self.review_queue.maxsize

            return {
                'queue_size': queue_size,
                'queue_max_size': max_size,
                'active_workers': len(worker_status),
                'task_statistics': status_counts,
                'worker_load': worker_status,
                'system_status': 'healthy' if queue_size < max_size * 0.9 else 'warning',
                'estimated_processing_rate': status_counts.get('processing', 0) * 2,
                'total_tasks': len(self.processing_tasks)
            }

    def get_task(self, task_id: str) -> Optional[Task]:
        with self.processing_lock:
            return self.processing_tasks.get(task_id)

    def list_tasks(self, limit: int = 50, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.processing_lock:
            if status:
                task_list = [task.to_dict() for task in self.processing_tasks.values() if task.status == status]
            else:
                task_list = [task.to_dict() for task in self.processing_tasks.values()]

        task_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return task_list[:limit]

    def remove_task(self, task_id: str) -> bool:
        with self.processing_lock:
            if task_id in self.processing_tasks:
                del self.processing_tasks[task_id]
                return True
            return False

    def start_workers(self, worker_function: Callable[[int, 'QueueManager'], None]) -> List[threading.Thread]:
        if self.running:
            logger.warning("工作线程已在运行中")
            return self.workers

        self.running = True
        self.workers = []

        for i in range(self.max_workers):
            worker = threading.Thread(
                target=worker_function,
                args=(i, self),
                name=f"Worker_{i}",
                daemon=True
            )
            self.workers.append(worker)
            worker.start()
            logger.debug(f"启动工作线程：Worker_{i}")

        return self.workers

    def adjust_worker_based_on_load(self) -> int:
        queue_size = self.review_queue.qsize()
        active_workers = len([w for w in self.workers if w.is_alive()])

        needed_workers = min(
            max(1, queue_size // 5),
            self.config.max_size
        )

        if active_workers < needed_workers and active_workers < self.max_workers:
            logger.info(f"当前负载较高：队列大小={queue_size}，活跃线程={active_workers}")
        elif active_workers > needed_workers * 2 and active_workers > 1:
            logger.info(f"当前负载较低：队列大小={queue_size}，活跃线程={active_workers}")

        return active_workers

    def stop_workers(self, timeout: float = 5.0):
        if not self.running:
            return

        self.running = False

        for _ in range(len(self.workers)):
            try:
                self.review_queue.put(None, timeout=timeout)
            except queue.Full:
                pass

        for worker in self.workers:
            worker.join(timeout=timeout)

        self.workers.clear()
        logger.info("所有工作线程已停止")

    def get_worker_count(self) -> int:
        return len([w for w in self.workers if w.is_alive()])

    def is_running(self) -> bool:
        return self.running