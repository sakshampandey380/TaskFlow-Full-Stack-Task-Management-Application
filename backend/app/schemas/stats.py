from typing import Dict, List, Any
from pydantic import BaseModel


class PriorityCount(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0
    urgent: int = 0


class CategoryCount(BaseModel):
    id: int
    name: str
    color: str
    count: int


class TaskStatsOut(BaseModel):
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    in_progress_tasks: int = 0
    overdue_tasks: int = 0
    important_tasks: int = 0
    today_tasks: int = 0
    upcoming_tasks: int = 0
    completion_rate: float = 0.0
    by_priority: PriorityCount = PriorityCount()
    by_category: List[CategoryCount] = []
