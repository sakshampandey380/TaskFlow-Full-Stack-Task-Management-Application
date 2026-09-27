from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = v.strip().lstrip("#")
        if not v:
            raise ValueError("Tag name cannot be empty.")
        return v.lower()


class TagOut(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
