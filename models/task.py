"""任务模型定义"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass(slots=True)
class Task:
    """任务模型"""
    task_id: str
    object_kind: str  # 'push' or 'merge_request'
    payload_data: Dict[str, Any]
    status: str = 'queued'  # queued, processing, completed, failed, retrying
    project_id: Optional[int] = None
    worker_id: Optional[int] = None
    retry_count: int = 0
    timestamp: str = ""
    start_time: Optional[str] = None
    queue_position: int = 0
    estimated_wait_time: int = 0
    success: bool = False
    review_length: int = 0
    error: Optional[str] = None
    last_error: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        """将对象转换为字典"""
        # return {
        #     'task_id': self.task_id,
        #     'status': self.status,
        #     'object_kind': self.object_kind,
        #     'timestamp': self.timestamp,
        #     'project_id': self.project_id,
        #     'worker_id': self.worker_id,
        #     'retry_count': self.retry_count,
        #     'queue_position': self.queue_position,
        #     'estimated_wait_time': self.estimated_wait_time,
        #     'success': self.success,
        #     'review_length': self.review_length,
        #     'error': self.error
        # }
        return asdict(self)