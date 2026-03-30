from services.queue_manager import QueueManager





def start_background_processing(worker_id: int, queue_manager: QueueManager):
    '''
    启动后台处理线程
    '''
    logger = __import__('tools').logger
    logger.info(f"后台处理线程 {worker_id} 启动")

    while queue_manager.running:
        