from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class UserSettingsUpdate(BaseModel):
    theme: Optional[Literal["light", "dark", "system"]] = None
    default_task_priority: Optional[Literal["low", "medium", "high", "urgent"]] = None
    default_task_status: Optional[Literal["pending", "in_progress"]] = None
    tasks_per_page: Optional[int] = Field(None, ge=5, le=100)
    show_completed_tasks: Optional[bool] = None
    email_notifications: Optional[bool] = None
    reminder_notifications: Optional[bool] = None


class UserSettingsOut(BaseModel):
    id: int
    user_id: int
    theme: str
    default_task_priority: str
    default_task_status: str
    tasks_per_page: int
    show_completed_tasks: bool
    email_notifications: bool
    reminder_notifications: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
