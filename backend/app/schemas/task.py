from datetime import date, time, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator
from backend.app.schemas.category import CategoryOut
from backend.app.schemas.tag import TagOut

PriorityType = Literal["low", "medium", "high", "urgent"]
StatusType = Literal["pending", "in_progress", "completed"]


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task")
    description: Optional[str] = Field(None, max_length=5000, description="Task details or notes")
    status: StatusType = "pending"
    priority: PriorityType = "medium"
    category_id: Optional[int] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    is_important: bool = False
    tags: Optional[List[str]] = []

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Task title cannot be empty or only spaces.")
        return v


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[StatusType] = None
    priority: Optional[PriorityType] = None
    category_id: Optional[int] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    is_important: Optional[bool] = None
    is_archived: Optional[bool] = None
    sort_order: Optional[int] = None
    tags: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Task title cannot be empty.")
        return v


class TaskCompleteToggle(BaseModel):
    completed: Optional[bool] = None  # If None, toggles current status


class TaskOut(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    completed_at: Optional[datetime] = None
    is_important: bool
    is_archived: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryOut] = None
    tags: List[TagOut] = []

    class Config:
        from_attributes = True
