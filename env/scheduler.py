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
    Worker(id="w1",  name="Alice",   capacity=3, skills=["backend", "devops"],      hourly_rate=80.0),
    Worker(id="w2",  name="Bob",     capacity=3, skills=["testing", "backend"],     hourly_rate=70.0),
    Worker(id="w3",  name="Charlie", capacity=2, skills=["writing", "testing"],     hourly_rate=50.0),
    Worker(id="w4",  name="Diana",   capacity=3, skills=["frontend", "writing"],    hourly_rate=65.0),
    Worker(id="w5",  name="Eve",     capacity=2, skills=["security", "backend"],    hourly_rate=90.0),
    Worker(id="w6",  name="Frank",   capacity=3, skills=["devops", "testing"],      hourly_rate=75.0),
    Worker(id="w7",  name="Grace",   capacity=2, skills=["frontend", "security"],   hourly_rate=70.0),
    Worker(id="w8",  name="Henry",   capacity=3, skills=["backend", "writing"],     hourly_rate=60.0),
    Worker(id="w9",  name="Iris",    capacity=2, skills=["testing", "frontend"],    hourly_rate=55.0),
    Worker(id="w10", name="Jack",    capacity=3, skills=["devops", "security"],     hourly_rate=85.0),
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
    Worker(id="w1", name="Alice",   capacity=3, skills=["backend", "security"],  hourly_rate=80.0),
    Worker(id="w2", name="Bob",     capacity=3, skills=["devops", "testing"],    hourly_rate=70.0),
    Worker(id="w3", name="Charlie", capacity=2, skills=["frontend", "testing"],  hourly_rate=60.0),
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
    Worker(id="w1", name="Alice",   capacity=3, skills=["backend", "management"], hourly_rate=80.0),
    Worker(id="w2", name="Bob",     capacity=3, skills=["devops", "testing"],     hourly_rate=70.0),
    Worker(id="w3", name="Charlie", capacity=2, skills=["frontend", "security"],  hourly_rate=65.0),
    Worker(id="w4", name="Diana",   capacity=2, skills=["backend", "security"],   hourly_rate=90.0),
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
    Worker(id="w1", name="Alice",   capacity=3, skills=["backend", "management"], hourly_rate=80.0),
    Worker(id="w2", name="Bob",     capacity=3, skills=["devops", "testing"],     hourly_rate=70.0),
    Worker(id="w3", name="Charlie", capacity=2, skills=["frontend", "testing"],   hourly_rate=60.0),
    Worker(id="w4", name="Diana",   capacity=2, skills=["security", "backend"],   hourly_rate=90.0),
    Worker(id="w5", name="Eve",     capacity=2, skills=["frontend", "management"],hourly_rate=75.0),
]
# Expert mode events: Bob leaves at step 3, urgent task injected at step 5
EXPERT_LEAVE   = {"w2": 3}
EXPERT_URGENT  = Task(
    id="t11", name="URGENT: Fix prod outage",
    duration=2, deadline=7, priority=3,
    required_skill="devops"
)
MULTI_WORKERS = [
    Worker(id="w1", name="Alice",   capacity=6, skills=["backend",  "management"], hourly_rate=80.0),
    Worker(id="w2", name="Bob",     capacity=5, skills=["devops",   "testing"],    hourly_rate=70.0),
    Worker(id="w3", name="Charlie", capacity=5, skills=["frontend", "writing"],    hourly_rate=60.0),
    Worker(id="w4", name="Diana",   capacity=5, skills=["security", "backend"],    hourly_rate=90.0),
    Worker(id="w5", name="Eve",     capacity=5, skills=["testing",  "frontend"],   hourly_rate=65.0),
]
# ── Multi-project mode ─────────────────────────────────────────

PROJECT_FRONTEND = [
    Task(id="f1", name="Design homepage",      duration=3, deadline=5,  priority=2, required_skill="frontend",  project_id="frontend"),
    Task(id="f2", name="Build nav component",  duration=2, deadline=8,  priority=2, required_skill="frontend",  project_id="frontend", depends_on=["f1"]),
    Task(id="f3", name="Mobile responsive",    duration=3, deadline=11, priority=2, required_skill="frontend",  project_id="frontend", depends_on=["f2"]),
    Task(id="f4", name="Write UI tests",       duration=2, deadline=13, priority=1, required_skill=None,        project_id="frontend", depends_on=["f2"]),
    Task(id="f5", name="Deploy frontend",      duration=2, deadline=16, priority=3, required_skill="devops",    project_id="frontend", depends_on=["f3","f4"]),
]

PROJECT_BACKEND = [
    Task(id="b1", name="Design API schema",    duration=3, deadline=4,  priority=3, required_skill="backend",    project_id="backend"),
    Task(id="b2", name="Build auth endpoints", duration=4, deadline=8,  priority=3, required_skill="backend",    project_id="backend", depends_on=["b1"]),
    Task(id="b3", name="Build data endpoints", duration=4, deadline=8,  priority=2, required_skill="backend",    project_id="backend", depends_on=["b1"]),
    Task(id="b4", name="Security audit",       duration=2, deadline=11, priority=3, required_skill="security",   project_id="backend", depends_on=["b2"]),
    Task(id="b5", name="Deploy backend",       duration=2, deadline=14, priority=3, required_skill="devops",     project_id="backend", depends_on=["b3","b4"]),
]

PROJECT_INFRA = [
    Task(id="i1", name="Setup cloud env",      duration=3, deadline=4,  priority=3, required_skill="devops",    project_id="infra"),
    Task(id="i2", name="Configure CI/CD",      duration=3, deadline=8,  priority=2, required_skill="devops",    project_id="infra",   depends_on=["i1"]),
    Task(id="i3", name="Setup monitoring",     duration=2, deadline=10, priority=2, required_skill="devops",    project_id="infra",   depends_on=["i1"]),
    Task(id="i4", name="Load testing",         duration=3, deadline=13, priority=2, required_skill="testing",   project_id="infra",   depends_on=["i2","i3"]),
    Task(id="i5", name="Write runbooks",       duration=2, deadline=16, priority=1, required_skill="writing",   project_id="infra",   depends_on=["i4"]),
]
# ── The main environment class ─────────────────────────────────

class WorkSchedulerEnv:

    def __init__(self, difficulty: str = "easy"):
        assert difficulty in ("easy", "medium", "hard", "expert", "multi")
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
            "total_cost":      round(self.total_cost, 2),
            "budget_limit":    self.budget_limit,
            "budget_remaining": round(self.budget_limit - self.total_cost, 2),
            "projects": self._get_project_summary(),
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
        elif self.difficulty == "expert":
            self.pending_tasks = copy.deepcopy(EXPERT_TASKS)
            self.workers       = copy.deepcopy(EXPERT_WORKERS)
            self._urgent_injected = False
        else:   # ← this is where you add multi
            self.pending_tasks = (
                copy.deepcopy(PROJECT_FRONTEND) +
                copy.deepcopy(PROJECT_BACKEND)  +
                copy.deepcopy(PROJECT_INFRA)
            )
            self.workers = copy.deepcopy(MULTI_WORKERS)
            self._urgent_injected = False

        self.current_step      = 0
        self.assigned          = {}
        self.missed_deadlines  = 0
        self.done              = False
        self.total_tasks       = len(self.pending_tasks)
        self.cancelled_tasks   = []
        self._cancel_step      = max(3, len(self.pending_tasks) // 3)
        self._cancelled_already = False
        self.total_cost   = 0.0
        # Budget = sum of all task durations × average hourly rate × 1.3 buffer
        avg_rate = sum(w.hourly_rate for w in self.workers) / len(self.workers)
        self.budget_limit = round(
            sum(t.duration for t in self.pending_tasks) * avg_rate * 1.3, 2
        )

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

        # Track cost
        task_cost = task.duration * worker.hourly_rate
        self.total_cost += task_cost

        # Budget penalty
        budget_ratio = self.total_cost / max(self.budget_limit, 1)
        if budget_ratio > 1.0:
            budget_penalty = min(0.2, (budget_ratio - 1.0) * 0.5)
        else:
            budget_penalty = 0.0

        # Base score
        score = 0.5

        # Skill match bonus
        if task.required_skill and task.required_skill in worker.skills:
            score += 0.1

        # Priority bonus
        score += (task.priority - 1) * 0.1

        # Deadline bonus/penalty
        if task.deadline is not None:
            steps_remaining = task.deadline - self.current_step
            if steps_remaining < 0:
                score -= 0.2
            elif steps_remaining <= 1:
                score += 0.2
            elif steps_remaining <= 3:
                score += 0.15
            else:
                score += 0.05

        # Workload balance
        load = len(worker.assigned_task_ids) / worker.capacity
        if load <= 0.5:
            score += 0.1
        elif load > 1.0:
            score -= 0.15

        # Penalize ignoring urgent tasks
        high_priority_pending = [
            t for t in self.pending_tasks
            if t.priority == 3
            and all(d in self.assigned for d in t.depends_on)
        ]
        if high_priority_pending and task.priority == 1:
            score -= 0.1

        # Apply budget penalty
        score = round(min(1.0, max(0.0, score - budget_penalty)), 3)

        return Reward(value=score, reason=f"Assigned '{task.name}' to {worker.name}."), \
               {"task": task.id, "worker": worker.id}

    def _apply_hard_events(self):
        for wid, leave_step in HARD_LEAVE.items():
            if self.current_step == leave_step:
                w = next((w for w in self.workers if w.id == wid), None)
                if w:
                    w.available = False
    def _apply_cancellation(self):
        if self.difficulty == "multi":   # ← ADD THIS LINE
            return
        """Cancel one pending task once, at a fixed step."""
        if self._cancelled_already:
            return
        if self.current_step != self._cancel_step:
            return
        if not self.pending_tasks:
            return

        # Get all task IDs that other tasks depend on
        depended_on = set()
        for t in self.pending_tasks:
            for d in t.depends_on:
                depended_on.add(d)

        # Also protect assigned tasks' dependents
        all_task_ids = set(t.id for t in self.pending_tasks)

        # Only cancel tasks that:
        # 1. Nothing else depends on them
        # 2. Are not the only remaining task in their project
        project_counts = {}
        for t in self.pending_tasks:
            pid = t.project_id
            project_counts[pid] = project_counts.get(pid, 0) + 1

        safe_to_cancel = [
            t for t in self.pending_tasks
            if t.id not in depended_on
            and project_counts.get(t.project_id, 0) > 1
        ]

        if not safe_to_cancel:
            self._cancelled_already = True
            return  # nothing safe — skip cancellation this episode

        # Cancel lowest priority safe task
        candidate = sorted(
            safe_to_cancel,
            key=lambda t: (t.priority, t.deadline or 999)
        )[0]

        self.cancelled_tasks.append(candidate.id)
        self.pending_tasks = [
            t for t in self.pending_tasks if t.id != candidate.id
        ]
        self.total_tasks -= 1
        self._cancelled_already = True
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
                if not w.available:
                    continue
                if len(w.assigned_task_ids) >= w.capacity + w.overtime_capacity:
                    continue
                if task.required_skill and task.required_skill not in w.skills:
                    continue
                return False  # valid move exists
        return True

    def _build_observation(self) -> Observation:
        return Observation(
            pending_tasks     = copy.deepcopy(self.pending_tasks),
            workers           = copy.deepcopy(self.workers),
            current_step      = self.current_step,
            assigned          = dict(self.assigned),
            total_tasks       = self.total_tasks,
            missed_deadlines  = self.missed_deadlines,
            cancelled_tasks   = list(self.cancelled_tasks),
            projects          = self._get_project_summary(),
            total_cost        = round(self.total_cost, 2),
            budget_limit      = self.budget_limit,
            budget_remaining  = round(self.budget_limit - self.total_cost, 2),
        )
    def _get_project_summary(self) -> Dict[str, List[str]]:
        """Returns dict of project_id → list of pending task IDs."""
        summary = {}
        for task in self.pending_tasks:
            pid = task.project_id
            if pid not in summary:
                summary[pid] = []
            summary[pid].append(task.id)
        return summary