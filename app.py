import os, sys, uuid
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    rows = ""
    for session_id, env in sessions.items():
        state = env.state()
        assigned = state["assigned"]
        cancelled = state.get("cancelled_tasks", [])
        workers = state["workers"]
        pending = state["pending_tasks"]

        # Worker rows
        worker_html = ""
        for w in workers:
            load = len(w["assigned_task_ids"])
            cap  = w["capacity"]
            bar  = "█" * load + "░" * max(0, cap - load)
            status = "on leave" if not w["available"] else f"{load}/{cap}"
            color  = "#ff6b6b" if not w["available"] else ("#ffd93d" if load >= cap else "#6bcb77")
            worker_html += f"""
            <tr>
              <td>{w['name']}</td>
              <td>{', '.join(w['skills'])}</td>
              <td style='color:{color}'>{status} {bar}</td>
              <td>{', '.join(w['assigned_task_ids']) or '—'}</td>
            </tr>"""

        # Task summary
        task_html = ""
        for t in pending:
            deadline_str = f"step {t['deadline']}" if t.get('deadline') else "none"
            task_html += f"""
            <tr>
              <td>{t['id']}</td>
              <td>{t['name']}</td>
              <td>{'⭐' * t['priority']}</td>
              <td>{t.get('required_skill','—')}</td>
              <td>{deadline_str}</td>
              <td style='color:#ffd93d'>pending</td>
            </tr>"""

        for tid, wid in assigned.items():
            task_html += f"""
            <tr>
              <td>{tid}</td>
              <td>—</td>
              <td>—</td>
              <td>—</td>
              <td>—</td>
              <td style='color:#6bcb77'>assigned → {wid}</td>
            </tr>"""

        for tid in cancelled:
            task_html += f"""
            <tr>
              <td>{tid}</td>
              <td>—</td>
              <td>—</td>
              <td>—</td>
              <td>—</td>
              <td style='color:#ff6b6b'>cancelled</td>
            </tr>"""

        rows += f"""
        <div class='session'>
          <h2>Session: {session_id} 
              — {state['difficulty'].upper()} 
              — Step {state['current_step']}
              — Missed: {state['missed_deadlines']}
              {'— DONE' if state['done'] else ''}
          </h2>

          <h3>Workers</h3>
          <table>
            <tr>
              <th>Name</th><th>Skills</th><th>Load</th><th>Tasks</th>
            </tr>
            {worker_html}
          </table>

          <h3>Tasks</h3>
          <table>
            <tr>
              <th>ID</th><th>Name</th><th>Priority</th>
              <th>Skill</th><th>Deadline</th><th>Status</th>
            </tr>
            {task_html}
          </table>
        </div>"""

    if not rows:
        rows = "<p style='color:#888'>No active sessions. Call /reset first to start one.</p>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>WorkScheduler Dashboard</title>
      <meta http-equiv='refresh' content='5'>
      <style>
        body {{
          font-family: monospace;
          background: #1a1a2e;
          color: #eee;
          padding: 24px;
        }}
        h1 {{ color: #a78bfa; margin-bottom: 8px; }}
        h2 {{ color: #60a5fa; border-bottom: 1px solid #333; padding-bottom: 6px; }}
        h3 {{ color: #34d399; margin-top: 16px; }}
        table {{
          border-collapse: collapse;
          width: 100%;
          margin-bottom: 16px;
        }}
        th {{
          background: #2d2d44;
          padding: 8px 12px;
          text-align: left;
          color: #a78bfa;
        }}
        td {{
          padding: 6px 12px;
          border-bottom: 1px solid #2a2a3e;
        }}
        tr:hover td {{ background: #2a2a3e; }}
        .session {{
          background: #16213e;
          border: 1px solid #2d2d44;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 24px;
        }}
        .footer {{
          color: #555;
          font-size: 12px;
          margin-top: 24px;
        }}
      </style>
    </head>
    <body>
      <h1>WorkScheduler-OpenEnv Dashboard</h1>
      <p style='color:#888'>Auto-refreshes every 5 seconds</p>
      {rows}
      <div class='footer'>
        WorkScheduler-OpenEnv v1.0.0 — 
        <a href='/docs' style='color:#60a5fa'>API Docs</a>
      </div>
    </body>
    </html>"""

    return HTMLResponse(content=html)
    
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)