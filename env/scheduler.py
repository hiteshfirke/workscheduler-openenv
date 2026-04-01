import copy
from typing import Tuple, Dict, Any, List
from .models import Observation, Action, Reward, Task, Worker

# ── The tasks and workers for each difficulty ──────────────────

EASY_TASKS = [
    Task(id="t1",  name="Write unit tests",       duration=2, priority=1, required_skill="testing"),
    Task(id="t2",  name="Fix login bug",           duration=3, priority=2, required_skill="backend"),
    Task(id="t3",  name="Update docs",             duration=1, priority=1, required_skill="writing"),
    Task(id="t4",  name="Code review PR",          duration=2, priority=2, required_skill="backend"),
    Task(id="t5",  name="Deploy staging build",    duration=4, priority=3, required_skill="devops"),
    Task(id="t6",  name="Fix payment bug",         duration=3, priority=3, required_skill="backend"),
    Task(id="t7",  name="Design landing page",     duration=4, priority=2, required_skill="frontend"),
    Task(id="t8",  name="Write API docs",          duration=2, priority=1, required_skill="writing"),
    Task(id="t9",  name="Setup monitoring",        duration=3, priority=2, required_skill="devops"),
    Task(id="t10", name="Database backup script",  duration=2, priority=2, required_skill="backend"),
    Task(id="t11", name="Fix mobile layout",       duration=3, priority=2, required_skill="frontend"),
    Task(id="t12", name="Security scan",           duration=2, priority=3, required_skill="security"),
    Task(id="t13", name="Optimize SQL queries",    duration=3, priority=2, required_skill="backend"),
    Task(id="t14", name="Setup error logging",     duration=2, priority=1, required_skill="devops"),
    Task(id="t15", name="Write release notes",     duration=1, priority=1, required_skill="writing"),
    Task(id="t16", name="Add dark mode",           duration=4, priority=2, required_skill="frontend"),
    Task(id="t17", name="Load test API",           duration=3, priority=2, required_skill="testing"),
    Task(id="t18", name="Fix email templates",     duration=2, priority=1, required_skill="frontend"),
    Task(id="t19", name="Review access controls",  duration=2, priority=3, required_skill="security"),
    Task(id="t20", name="Deploy production",       duration=3, priority=3, required_skill="devops"),
]

EASY_WORKERS = [
    Worker(id="w1",  name="Alice",   capacity=3, skills=["backend", "devops"]),
    Worker(id="w2",  name="Bob",     capacity=3, skills=["testing", "backend"]),
    Worker(id="w3",  name="Charlie", capacity=2, skills=["writing", "testing"]),
    Worker(id="w4",  name="Diana",   capacity=3, skills=["frontend", "writing"]),
    Worker(id="w5",  name="Eve",     capacity=2, skills=["security", "backend"]),
    Worker(id="w6",  name="Frank",   capacity=3, skills=["devops", "testing"]),
    Worker(id="w7",  name="Grace",   capacity=2, skills=["frontend", "security"]),
    Worker(id="w8",  name="Henry",   capacity=3, skills=["backend", "writing"]),
    Worker(id="w9",  name="Iris",    capacity=2, skills=["testing", "frontend"]),
    Worker(id="w10", name="Jack",    capacity=3, skills=["devops", "security"]),
]

MEDIUM_TASKS = [
    Task(id="t1", name="Design database",   duration=4, deadline=3, priority=3, required_skill="backend"),
    Task(id="t2", name="Setup CI pipeline", duration=3, deadline=4, priority=2, required_skill="devops"),
    Task(id="t3", name="Build API",         duration=5, deadline=6, priority=3, depends_on=["t1"], required_skill="backend"),
    Task(id="t4", name="Write tests",       duration=3, deadline=7, priority=2, depends_on=["t3"], required_skill="testing"),
    Task(id="t5", name="Frontend page",     duration=4, deadline=5, priority=2, required_skill="frontend"),
    Task(id="t6", name="Security audit",    duration=3, deadline=6, priority=3, required_skill="security"),
]
MEDIUM_WORKERS = [
    Worker(id="w1", name="Alice",   capacity=3, skills=["backend", "security"]),
    Worker(id="w2", name="Bob",     capacity=3, skills=["devops", "testing"]),
    Worker(id="w3", name="Charlie", capacity=2, skills=["frontend", "testing"]),
]

HARD_TASKS = [
    Task(id="t1", name="Gather requirements", duration=2, deadline=2,  priority=3, required_skill="management"),
    Task(id="t2", name="System architecture", duration=5, deadline=4,  priority=3, depends_on=["t1"], required_skill="backend"),
    Task(id="t3", name="Database design",     duration=3, deadline=5,  priority=2, depends_on=["t2"], required_skill="backend"),
    Task(id="t4", name="Auth service",        duration=4, deadline=6,  priority=3, depends_on=["t2"], required_skill="security"),
    Task(id="t5", name="Payment integration", duration=6, deadline=8,  priority=3, depends_on=["t4"], required_skill="backend"),
    Task(id="t6", name="Admin dashboard",     duration=4, deadline=9,  priority=2, depends_on=["t3"], required_skill="frontend"),
    Task(id="t7", name="Load testing",        duration=3, deadline=9,  priority=2, depends_on=["t5","t6"], required_skill="testing"),
    Task(id="t8", name="Go-live deployment",  duration=2, deadline=11, priority=3, depends_on=["t7"], required_skill="devops"),
]
HARD_WORKERS = [
    Worker(id="w1", name="Alice",   capacity=3, skills=["backend", "management"]),
    Worker(id="w2", name="Bob",     capacity=3, skills=["devops", "testing"]),
    Worker(id="w3", name="Charlie", capacity=2, skills=["frontend", "security"]),
    Worker(id="w4", name="Diana",   capacity=2, skills=["backend", "security"]),
]
# In hard mode: Bob goes on leave after step 4
HARD_LEAVE = {"w2": 4}
EXPERT_TASKS = [
    Task(id="t1",  name="Client requirements",   duration=2, deadline=2,  priority=3, required_skill="management"),
    Task(id="t2",  name="System design",          duration=4, deadline=4,  priority=3, depends_on=["t1"], required_skill="backend"),
    Task(id="t3",  name="Database schema",        duration=3, deadline=5,  priority=2, depends_on=["t2"], required_skill="backend"),
    Task(id="t4",  name="Auth microservice",      duration=4, deadline=6,  priority=3, depends_on=["t2"], required_skill="security"),
    Task(id="t5",  name="Payment gateway",        duration=5, deadline=8,  priority=3, depends_on=["t4"], required_skill="backend"),
    Task(id="t6",  name="Frontend dashboard",     duration=4, deadline=7,  priority=2, depends_on=["t3"], required_skill="frontend"),
    Task(id="t7",  name="Mobile app",             duration=6, deadline=9,  priority=2, depends_on=["t3"], required_skill="frontend"),
    Task(id="t8",  name="Load testing",           duration=3, deadline=10, priority=2, depends_on=["t5","t6"], required_skill="testing"),
    Task(id="t9",  name="Security audit",         duration=3, deadline=10, priority=3, depends_on=["t5"], required_skill="security"),
    Task(id="t10", name="Production deployment",  duration=2, deadline=12, priority=3, depends_on=["t8","t9"], required_skill="devops"),
]
EXPERT_WORKERS = [
    Worker(id="w1", name="Alice",   capacity=3, skills=["backend", "management"]),
    Worker(id="w2", name="Bob",     capacity=3, skills=["devops", "testing"]),
    Worker(id="w3", name="Charlie", capacity=2, skills=["frontend", "testing"]),
    Worker(id="w4", name="Diana",   capacity=2, skills=["security", "backend"]),
    Worker(id="w5", name="Eve",     capacity=2, skills=["frontend", "management"]),
]
# Expert mode events: Bob leaves at step 3, urgent task injected at step 5
EXPERT_LEAVE   = {"w2": 3}
EXPERT_URGENT  = Task(
    id="t11", name="URGENT: Fix prod outage",
    duration=2, deadline=7, priority=3,
    required_skill="devops"
)
# ── The main environment class ─────────────────────────────────

class WorkSchedulerEnv:

    def __init__(self, difficulty: str = "easy"):
        assert difficulty in ("easy", "medium", "hard", "expert")
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
            "cancelled_tasks":  self.cancelled_tasks,
            "total_tasks":      self.total_tasks,
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

        if self.difficulty == "expert":
            self._apply_expert_events()
        self._apply_cancellation()   

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
        elif self.difficulty == "hard":
            self.pending_tasks = copy.deepcopy(HARD_TASKS)
            self.workers       = copy.deepcopy(HARD_WORKERS)
        else:   # expert
            self.pending_tasks = copy.deepcopy(EXPERT_TASKS)
            self.workers       = copy.deepcopy(EXPERT_WORKERS)
            self._urgent_injected = False

        self.current_step      = 0
        self.assigned          = {}
        self.missed_deadlines  = 0
        self.done              = False
        self.total_tasks       = len(self.pending_tasks)
        self.cancelled_tasks   = []        # NEW — tracks cancelled task IDs
        self._cancel_step      = max(3, len(self.pending_tasks) // 3)  # cancel at 1/3 through
        self._cancelled_already = False    # NEW

    def _apply_action(self, action: Action) -> Tuple[Reward, Dict]:
        task   = next((t for t in self.pending_tasks if t.id == action.task_id), None)
        worker = next((w for w in self.workers       if w.id == action.worker_id), None)

        if task is None:
            return Reward(value=0.0, reason="Task not found or already assigned."), {}
        if worker is None:
            return Reward(value=0.0, reason="Worker not found."), {}
        if not worker.available:
            return Reward(value=0.1, reason=f"{worker.name} is on leave."), {}
        total_allowed = worker.capacity + worker.overtime_capacity
        if len(worker.assigned_task_ids) >= total_allowed:
            return Reward(value=0.1, reason=f"{worker.name} is at full capacity including overtime."), {}
        for dep in task.depends_on:
            if dep not in self.assigned:
                return Reward(value=0.1, reason=f"Dependency {dep} not yet assigned."), {}
        if task.required_skill and task.required_skill not in worker.skills:
            return Reward(
                value=0.2,
                reason=f"{worker.name} lacks skill '{task.required_skill}' for '{task.name}'."
            ), {}

        # Valid assignment — do it
        worker.assigned_task_ids.append(task.id)
        self.assigned[task.id] = worker.id
        self.pending_tasks = [t for t in self.pending_tasks if t.id != task.id]

        # Calculate reward
        # Base score
        score = 0.5

        # Skill match bonus
        if task.required_skill and task.required_skill in worker.skills:
            score += 0.1

        # Priority bonus
        score += (task.priority - 1) * 0.1   # +0.0, +0.1, or +0.2

        # Deadline bonus/penalty
        if task.deadline is not None:
            steps_remaining = task.deadline - self.current_step
            if steps_remaining < 0:
                score -= 0.2                  # already past deadline
            elif steps_remaining <= 1:
                score += 0.2                  # urgent — assigned just in time
            elif steps_remaining <= 3:
                score += 0.15                 # assigned with a little buffer
            else:
                score += 0.05                 # assigned early, small bonus

        # Workload balance — bonus for normal load, penalty for overtime
        load = len(worker.assigned_task_ids) / worker.capacity
        if load <= 0.5:
            score += 0.1                      # well balanced
        elif load > 1.0:
            score -= 0.15                     # overtime penalty — hurts quality

        # Penalty for assigning a low priority task when high priority ones exist
        high_priority_pending = [
            t for t in self.pending_tasks
            if t.priority == 3 and t.id != task.id
            and all(d in self.assigned for d in t.depends_on)
        ]
        if high_priority_pending and task.priority == 1:
            score -= 0.1                      # penalize ignoring urgent tasks

        score = round(min(1.0, max(0.0, score)), 3)
        return Reward(value=score, reason=f"Assigned '{task.name}' to {worker.name}."), \
               {"task": task.id, "worker": worker.id}

    def _apply_hard_events(self):
        for wid, leave_step in HARD_LEAVE.items():
            if self.current_step == leave_step:
                w = next((w for w in self.workers if w.id == wid), None)
                if w:
                    w.available = False
    def _apply_cancellation(self):
        """Cancel one pending task once, at a fixed step."""
        if self._cancelled_already:
            return
        if self.current_step != self._cancel_step:
            return
        if not self.pending_tasks:
            return

        candidate = sorted(
            self.pending_tasks,
            key=lambda t: (t.priority, t.deadline or 999)
        )[0]

        self.cancelled_tasks.append(candidate.id)
        self.pending_tasks = [
            t for t in self.pending_tasks if t.id != candidate.id
        ]
        self.total_tasks -= 1
        self._cancelled_already = True     # NEW — never run again
    def _apply_expert_events(self):
        # Worker goes on leave
        for wid, leave_step in EXPERT_LEAVE.items():
            if self.current_step == leave_step:
                w = next((w for w in self.workers if w.id == wid), None)
                if w:
                    w.available = False

        # Inject urgent task mid-episode at step 5
        if self.current_step == 5 and not self._urgent_injected:
            self.pending_tasks.append(copy.deepcopy(EXPERT_URGENT))
            self.total_tasks += 1
            self._urgent_injected = True
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
            cancelled_tasks  = list(self.cancelled_tasks),
        )