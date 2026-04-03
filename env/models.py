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
    required_skill: Optional[str] = None
    project_id: str = "default"

class Worker(BaseModel):
    id: str
    name: str
    capacity: int = 3
    overtime_capacity: int = 1
    assigned_task_ids: List[str] = []
    available: bool = True
    skills: List[str] = []                 # NEW — e.g. ["backend", "testing"]

class Observation(BaseModel):
    pending_tasks: List[Task]
    workers: List[Worker]
    current_step: int
    assigned: Dict[str, str] = {}
    total_tasks: int = 0
    missed_deadlines: int = 0
    cancelled_tasks: List[str] = []
    projects: Dict[str, List[str]] = {}

class Action(BaseModel):
    task_id: str
    worker_id: str
    project_id: str = "default" 

class Reward(BaseModel):
    value: float = Field(ge=0.0, le=1.0)
    reason: str