from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Time, DateTime, Enum, SmallInteger, func
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.tag import task_tags


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum("pending", "in_progress", "completed", name="task_status_enum"), default="pending", nullable=False, index=True)
    priority = Column(Enum("low", "medium", "high", "urgent", name="task_priority_enum"), default="medium", nullable=False, index=True)
    due_date = Column(Date, nullable=True, index=True)
    due_time = Column(Time, nullable=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    is_important = Column(SmallInteger, default=0, nullable=False, index=True)
    is_archived = Column(SmallInteger, default=0, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks", lazy="joined")
    reminders = relationship("TaskReminder", cascade="all, delete-orphan", back_populates="task")
