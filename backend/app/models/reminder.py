from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, SmallInteger, Enum
from sqlalchemy.orm import relationship
from backend.app.database import Base


class TaskReminder(Base):
    __tablename__ = "task_reminders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    reminder_at = Column(DateTime, nullable=False, index=True)
    reminder_type = Column(Enum("notification", "email", name="reminder_type_enum"), default="notification", nullable=False)
    is_sent = Column(SmallInteger, default=0, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    task = relationship("Task", back_populates="reminders")
    user = relationship("User", back_populates="reminders")
