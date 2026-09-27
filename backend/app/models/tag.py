from sqlalchemy import Column, Integer, String, ForeignKey, Table, text, func, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column("created_at", DateTime, server_default=func.current_timestamp(), nullable=False)
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="tags")
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")
