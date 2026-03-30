import copy
from typing import Tuple, Dict, Any, List
from .models import Observation, Action, Reward, Task, Worker

# ── The tasks and workers for each difficulty ──────────────────

EASY_TASKS = [
    Task(id="t1", name="Write unit tests",     duration=2, priority=1),
    Task(id="t2", name="Fix login bug",        duration=3, priority=2),
    Task(id="t3", name="Update docs",          duration=1, priority=1),
    Task(id="t4", name="Code review PR",       duration=2, priority=2),
    Task(id="t5", name="Deploy staging build", duration=4, priority=3),
]
EASY_WORKERS = [
    Worker(id="w1", name="Alice", capacity=3),
    Worker(id="w2", name="Bob",   capacity=2),
    Worker(id="w3", name="Charlie", capacity=2),
]

MEDIUM_TASKS = [
    Task(id="t1", name="Design database",    duration=4, deadline=3, priority=3),
    Task(id="t2", name="Setup CI pipeline",  duration=3, deadline=4, priority=2),
    Task(id="t3", name="Build API",          duration=5, deadline=6, priority=3, depends_on=["t1"]),
    Task(id="t4", name="Write tests",        duration=3, deadline=7, priority=2, depends_on=["t3"]),
    Task(id="t5", name="Frontend page",      duration=4, deadline=5, priority=2),
    Task(id="t6", name="Security audit",     duration=3, deadline=6, priority=3),
]
MEDIUM_WORKERS = [
    Worker(id="w1", name="Alice",   capacity=3),
    Worker(id="w2", name="Bob",     capacity=3),
    Worker(id="w3", name="Charlie", capacity=2),
]

HARD_TASKS = [
    Task(id="t1", name="Gather requirements", duration=2, deadline=2,  priority=3),
    Task(id="t2", name="System architecture", duration=5, deadline=4,  priority=3, depends_on=["t1"]),
    Task(id="t3", name="Database design",     duration=3, deadline=5,  priority=2, depends_on=["t2"]),
    Task(id="t4", name="Auth service",        duration=4, deadline=6,  priority=3, depends_on=["t2"]),
    Task(id="t5", name="Payment integration", duration=6, deadline=8,  priority=3, depends_on=["t4"]),
    Task(id="t6", name="Admin dashboard",     duration=4, deadline=9,  priority=2, depends_on=["t3"]),
    Task(id="t7", name="Load testing",        duration=3, deadline=9,  priority=2, depends_on=["t5","t6"]),
    Task(id="t8", name="Go-live deployment",  duration=2, deadline=11, priority=3, depends_on=["t7"]),
]
HARD_WORKERS = [
    Worker(id="w1", name="Alice",   capacity=3),
    Worker(id="w2", name="Bob",     capacity=3),
    Worker(id="w3", name="Charlie", capacity=2),
    Worker(id="w4", name="Diana",   capacity=2),
]
# In hard mode: Bob goes on leave after step 4
HARD_LEAVE = {"w2": 4}

# ── The main environment class ─────────────────────────────────

class WorkSchedulerEnv:

    def __init__(self, difficulty: str = "easy"):
        assert difficulty in ("easy", "medium", "hard")
        self.difficulty = difficulty
        self._reset_state()

    def reset(self) -> Observation:
        """Start a fresh episode. Always call this first."""
        self._reset_state()
        return self._build_observation()

    def state(self) -> Dict[str, Any]:
        """Return full current state as a plain dict."""
        return {
            "difficulty":       self.difficulty,
            "current_step":     self.current_step,
            "done":             self.done,
            "assigned":         self.assigned,
            "missed_deadlines": self.missed_deadlines,
            "pending_tasks":    [t.model_dump() for t in self.pending_tasks],
            "workers":          [w.model_dump() for w in self.workers],
        }

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict]:
        """Agent takes one action. Returns (observation, reward, done, info)."""
        if self.done:
            raise RuntimeError("Episode over. Call reset() first.")

        self.current_step += 1
        reward, info = self._apply_action(action)

        if self.difficulty == "hard":
            self._apply_hard_events()

        self._check_missed_deadlines()
        self.done = self._check_done()

        return self._build_observation(), reward, self.done, info

    # ── Internal helpers ───────────────────────────────────────

    def _reset_state(self):
        if self.difficulty == "easy":
            self.pending_tasks = copy.deepcopy(EASY_TASKS)
            self.workers       = copy.deepcopy(EASY_WORKERS)
        elif self.difficulty == "medium":
            self.pending_tasks = copy.deepcopy(MEDIUM_TASKS)
            self.workers       = copy.deepcopy(MEDIUM_WORKERS)
        else:
            self.pending_tasks = copy.deepcopy(HARD_TASKS)
            self.workers       = copy.deepcopy(HARD_WORKERS)

        self.current_step     = 0
        self.assigned         = {}
        self.missed_deadlines = 0
        self.done             = False
        self.total_tasks      = len(self.pending_tasks)

    def _apply_action(self, action: Action) -> Tuple[Reward, Dict]:
        task   = next((t for t in self.pending_tasks if t.id == action.task_id), None)
        worker = next((w for w in self.workers       if w.id == action.worker_id), None)

        if task is None:
            return Reward(value=0.0, reason="Task not found or already assigned."), {}
        if worker is None:
            return Reward(value=0.0, reason="Worker not found."), {}
        if not worker.available:
            return Reward(value=0.1, reason=f"{worker.name} is on leave."), {}
        if len(worker.assigned_task_ids) >= worker.capacity:
            return Reward(value=0.1, reason=f"{worker.name} is at full capacity."), {}
        for dep in task.depends_on:
            if dep not in self.assigned:
                return Reward(value=0.1, reason=f"Dependency {dep} not yet assigned."), {}

        # Valid assignment — do it
        worker.assigned_task_ids.append(task.id)
        self.assigned[task.id] = worker.id
        self.pending_tasks = [t for t in self.pending_tasks if t.id != task.id]

        # Calculate reward
        score = 0.5
        score += (task.priority - 1) * 0.1          # +0.1 or +0.2 for higher priority

        if task.deadline is not None:
            if self.current_step <= task.deadline:
                score += 0.2                         # met deadline
            else:
                score -= 0.2                         # missed deadline

        load = len(worker.assigned_task_ids) / worker.capacity
        if load <= 0.5:
            score += 0.1                             # bonus for spreading work

        score = round(min(1.0, max(0.0, score)), 3)
        return Reward(value=score, reason=f"Assigned '{task.name}' to {worker.name}."), \
               {"task": task.id, "worker": worker.id}

    def _apply_hard_events(self):
        for wid, leave_step in HARD_LEAVE.items():
            if self.current_step == leave_step:
                w = next((w for w in self.workers if w.id == wid), None)
                if w:
                    w.available = False

    def _check_missed_deadlines(self):
        expired = [t for t in self.pending_tasks
                   if t.deadline is not None and self.current_step > t.deadline]
        self.missed_deadlines += len(expired)
        self.pending_tasks = [t for t in self.pending_tasks if t not in expired]

    def _check_done(self) -> bool:
        if not self.pending_tasks:
            return True
        for task in self.pending_tasks:
            if not all(d in self.assigned for d in task.depends_on):
                continue
            for w in self.workers:
                if w.available and len(w.assigned_task_ids) < w.capacity:
                    return False
        return True

    def _build_observation(self) -> Observation:
        return Observation(
            pending_tasks     = copy.deepcopy(self.pending_tasks),
            workers           = copy.deepcopy(self.workers),
            current_step      = self.current_step,
            assigned          = dict(self.assigned),
            total_tasks       = self.total_tasks,
            missed_deadlines  = self.missed_deadlines,
        )