from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Task(BaseModel):
    id: str
    name: str
    duration: int
    deadline: Optional[int] = None
    priority: int = 1
    depends_on: List[str] = []
    is_assigned: bool = False

class Worker(BaseModel):
    id: str
    name: str
    capacity: int = 3
    assigned_task_ids: List[str] = []
    available: bool = True

class Observation(BaseModel):
    pending_tasks: List[Task]
    workers: List[Worker]
    current_step: int
    assigned: Dict[str, str] = {}
    total_tasks: int = 0
    missed_deadlines: int = 0

class Action(BaseModel):
    task_id: str
    worker_id: str

class Reward(BaseModel):
    value: float = Field(ge=0.0, le=1.0)
    reason: str