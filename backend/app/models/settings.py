from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, SmallInteger, Enum
from sqlalchemy.orm import relationship
from backend.app.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), unique=True, nullable=False)
    theme = Column(Enum("light", "dark", "system", name="theme_enum"), default="light", nullable=False)
    default_task_priority = Column(Enum("low", "medium", "high", "urgent", name="priority_enum"), default="medium", nullable=False)
    default_task_status = Column(Enum("pending", "in_progress", name="default_status_enum"), default="pending", nullable=False)
    tasks_per_page = Column(Integer, default=20, nullable=False)
    show_completed_tasks = Column(SmallInteger, default=1, nullable=False)
    email_notifications = Column(SmallInteger, default=1, nullable=False)
    reminder_notifications = Column(SmallInteger, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="settings")
