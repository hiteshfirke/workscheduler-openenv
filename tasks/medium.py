import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from env import WorkSchedulerEnv, Action

def grade(agent_fn) -> dict:
    env = WorkSchedulerEnv(difficulty="medium")
    obs = env.reset()

    deadline_hits  = 0
    deadline_total = 0
    dep_violations = 0
    steps = 0

    while not env.done:
        action = agent_fn(obs)

        task_obj = next((t for t in obs.pending_tasks if t.id == action.task_id), None)
        if task_obj:
            if task_obj.deadline is not None:
                deadline_total += 1
                if obs.current_step + 1 <= task_obj.deadline:
                    deadline_hits += 1
            for dep in task_obj.depends_on:
                if dep not in obs.assigned:
                    dep_violations += 1

        obs, reward, done, info = env.step(action)
        steps += 1
        if steps > 30:
            break

    state       = env.state()
    completion  = len(state["assigned"]) / 6
    deadlines   = deadline_hits / max(deadline_total, 1)
    dep_score   = max(0.0, 1.0 - dep_violations * 0.2)

    score = round(completion * 0.5 + deadlines * 0.3 + dep_score * 0.2, 3)

    return {
        "task": "medium",
        "score": score,
        "breakdown": {
            "completion":   round(completion, 3),
            "deadlines":    round(deadlines, 3),
            "dependencies": round(dep_score, 3),
        },
        "passed": score >= 0.6,
    }