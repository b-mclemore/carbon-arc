"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")

    @field_validator('title')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading and trailing whitespace from title."""
        return v.strip()

    @field_validator('title')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure title is not empty after stripping."""
        if not v:
            raise ValueError('Title cannot be empty or whitespace only')
        return v


class TaskResponse(BaseModel):
    """Schema for task responses."""
    id: int = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    completed: bool = Field(..., description="Task completion status")

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    """Schema for task statistics."""
    total: int = Field(..., ge=0, description="Total number of tasks")
    completed: int = Field(..., ge=0, description="Number of completed tasks")
    pending: int = Field(..., ge=0, description="Number of pending tasks")
