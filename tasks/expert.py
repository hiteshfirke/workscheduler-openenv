import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from env import WorkSchedulerEnv, Action

def grade(agent_fn) -> dict:
    env = WorkSchedulerEnv(difficulty="expert")
    obs = env.reset()

    deadline_hits  = 0
    deadline_total = 0
    skill_matches  = 0
    skill_total    = 0
    urgent_handled = False
    worker_loads   = {}
    steps = 0

    while not env.done:
        action = agent_fn(obs)

        task_obj   = next((t for t in obs.pending_tasks if t.id == action.task_id), None)
        worker_obj = next((w for w in obs.workers       if w.id == action.worker_id), None)

        if task_obj and worker_obj:
            # Track skill matching
            if task_obj.required_skill:
                skill_total += 1
                if task_obj.required_skill in worker_obj.skills:
                    skill_matches += 1

            # Track deadlines
            if task_obj.deadline is not None:
                deadline_total += 1
                if obs.current_step + 1 <= task_obj.deadline:
                    deadline_hits += 1

            # Track if urgent task was handled quickly
            if task_obj.id == "t11":
                urgent_handled = obs.current_step <= 6

        obs, reward, done, info = env.step(action)

        if "worker" in info:
            wid = info["worker"]
            worker_loads[wid] = worker_loads.get(wid, 0) + 1

        steps += 1
        if steps > 50:
            break

    state      = env.state()
    completion = len(state["assigned"]) / max(state.get("total_tasks", 11), 1)
    deadlines  = deadline_hits  / max(deadline_total, 1)
    skills     = skill_matches  / max(skill_total, 1)

    if len(worker_loads) >= 2:
        loads    = list(worker_loads.values())
        avg      = sum(loads) / len(loads)
        variance = sum((l - avg) ** 2 for l in loads) / len(loads)
        balance  = max(0.0, 1.0 - variance / 10.0)
    else:
        balance = 0.0

    urgent_bonus   = 0.05 if urgent_handled else 0.0
    missed_penalty = state.get("missed_deadlines", 0) * 0.05

    score = round(
        completion * 0.35 +
        deadlines  * 0.30 +
        skills     * 0.20 +
        balance    * 0.10 +
        urgent_bonus - missed_penalty,
        3
    )
    score = max(0.0, min(1.0, score))

    return {
        "task": "expert",
        "score": score,
        "breakdown": {
            "completion":     round(completion, 3),
            "deadlines":      round(deadlines, 3),
            "skill_matching": round(skills, 3),
            "worker_balance": round(balance, 3),
            "urgent_handled": urgent_handled,
            "missed_deadlines": state.get("missed_deadlines", 0),
        },
        "passed": score >= 0.3,
    }