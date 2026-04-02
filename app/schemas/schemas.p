from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.task import TaskStatus, TaskPriority


# ── User Schemas ──────────────────────────────────────────────
class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


# ── Auth Schemas ──────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str


# ── Task Schemas ──────────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
