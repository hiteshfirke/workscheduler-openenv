import os, sys, uuid
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import WorkSchedulerEnv, Action

app = FastAPI(
    title="WorkScheduler-OpenEnv",
    description="A real-world AI agent environment for task scheduling.",
    version="1.0.0",
)

sessions: Dict[str, WorkSchedulerEnv] = {}


class ResetRequest(BaseModel):
    difficulty: str = "easy"
    session_id: str = ""

class StepRequest(BaseModel):
    session_id: str
    task_id: str
    worker_id: str

class GradeRequest(BaseModel):
    difficulty: str = "easy"


@app.get("/")
def health_check():
    return {"status": "ok", "env": "workscheduler-openenv", "version": "1.0.0"}


@app.get("/info")
def info():
    return {
        "name": "workscheduler-openenv",
        "tasks": ["easy", "medium", "hard", "expert"],
        "action_space": {"task_id": "string", "worker_id": "string"},
        "observation_space": {
            "pending_tasks": "list of unassigned tasks",
            "workers": "list of workers with skills and capacity",
            "current_step": "int",
            "assigned": "dict task_id -> worker_id",
            "missed_deadlines": "int",
        },
    }


@app.post("/reset")
def reset(req: ResetRequest):
    if req.difficulty not in ("easy", "medium", "hard", "expert"):
        raise HTTPException(status_code=400, detail="difficulty must be easy, medium, hard or expert")

    if len(sessions) >= 50:
        del sessions[next(iter(sessions))]

    session_id = req.session_id or str(uuid.uuid4())[:8]
    env = WorkSchedulerEnv(difficulty=req.difficulty)
    obs = env.reset()
    sessions[session_id] = env

    return {"session_id": session_id, "observation": obs.model_dump()}


@app.get("/state")
def get_state(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Call /reset first.")
    return sessions[session_id].state()


@app.post("/step")
def step(req: StepRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Call /reset first.")

    env = sessions[req.session_id]
    if env.done:
        return {"done": True, "message": "Episode over. Call /reset to start again."}

    obs, reward, done, info = env.step(Action(task_id=req.task_id, worker_id=req.worker_id))
    return {"observation": obs.model_dump(), "reward": reward.model_dump(), "done": done, "info": info}


@app.post("/grade")
def grade(req: GradeRequest):
    from tasks.easy   import grade as grade_easy
    from tasks.medium import grade as grade_medium
    from tasks.hard   import grade as grade_hard
    from tasks.expert import grade as grade_expert

    def greedy(obs):
        assigned = set(obs.assigned.keys())
        for task in sorted(obs.pending_tasks, key=lambda t: (-t.priority, t.deadline or 999)):
            if all(d in assigned for d in task.depends_on):
                for w in sorted(obs.workers, key=lambda w: len(w.assigned_task_ids)):
                    if w.available and len(w.assigned_task_ids) < w.capacity:
                        if not task.required_skill or task.required_skill in w.skills:
                            return Action(task_id=task.id, worker_id=w.id)
        for task in obs.pending_tasks:
            for w in obs.workers:
                if w.available and len(w.assigned_task_ids) < w.capacity:
                    return Action(task_id=task.id, worker_id=w.id)

    graders = {
        "easy":   grade_easy,
        "medium": grade_medium,
        "hard":   grade_hard,
        "expert": grade_expert,
    }
    if req.difficulty not in graders:
        raise HTTPException(status_code=400, detail="difficulty must be easy, medium, hard or expert")

    return graders[req.difficulty](greedy)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)