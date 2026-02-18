import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class TaskQueue:
    """Async task queue for orchestrator agent"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.tasks: Dict[str, Dict[str, Any]] = {}
    
    async def enqueue(self, task_type: str, payload: Dict[str, Any]) -> str:
        """
        Enqueue new task
        
        Args:
            task_type: Type of task (data_upload, paper_update, etc.)
            payload: Task payload
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "payload": payload,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        self.tasks[task_id] = task
        await self.queue.put(task)
        return task_id
    
    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """
        Dequeue next task
        
        Returns:
            Task dictionary or None if queue is empty
        """
        if self.queue.empty():
            return None
        task = await self.queue.get()
        task["status"] = "processing"
        task["updated_at"] = datetime.utcnow()
        self.tasks[task["task_id"]] = task
        return task
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get task status
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status or None if task not found
        """
        task = self.tasks.get(task_id)
        if task:
            return task["status"]
        return None
    
    def update_task_status(self, task_id: str, status: str, result: Optional[Any] = None):
        """
        Update task status
        
        Args:
            task_id: Task ID
            status: New status (pending, processing, completed, failed)
            result: Task result (optional)
        """
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = datetime.utcnow()
            if result is not None:
                self.tasks[task_id]["result"] = result
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()