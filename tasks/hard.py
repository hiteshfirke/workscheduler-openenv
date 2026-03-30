import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from env import WorkSchedulerEnv, Action

def grade(agent_fn) -> dict:
    env = WorkSchedulerEnv(difficulty="hard")
    obs = env.reset()

    deadline_hits  = 0
    deadline_total = 0
    priority_sum   = 0.0
    worker_loads   = {}
    steps = 0

    while not env.done:
        action = agent_fn(obs)

        task_obj = next((t for t in obs.pending_tasks if t.id == action.task_id), None)
        if task_obj:
            priority_sum += task_obj.priority / 3.0
            if task_obj.deadline is not None:
                deadline_total += 1
                if obs.current_step + 1 <= task_obj.deadline:
                    deadline_hits += 1

        obs, reward, done, info = env.step(action)

        if "worker" in info:
            wid = info["worker"]
            worker_loads[wid] = worker_loads.get(wid, 0) + 1

        steps += 1
        if steps > 40:
            break

    state      = env.state()
    completion = len(state["assigned"]) / 8
    deadlines  = deadline_hits / max(deadline_total, 1)
    priority   = priority_sum / max(steps, 1)

    if len(worker_loads) >= 2:
        loads    = list(worker_loads.values())
        avg      = sum(loads) / len(loads)
        variance = sum((l - avg) ** 2 for l in loads) / len(loads)
        balance  = max(0.0, 1.0 - variance / 10.0)
    else:
        balance = 0.0

    missed_penalty = state.get("missed_deadlines", 0) * 0.05
    score = round(
        completion * 0.40 + deadlines * 0.35 +
        priority   * 0.15 + balance   * 0.10 - missed_penalty,
        3
    )
    score = max(0.0, min(1.0, score))

    return {
        "task": "hard",
        "score": score,
        "breakdown": {
            "completion": round(completion, 3),
            "deadlines":  round(deadlines, 3),
            "priority":   round(priority, 3),
            "balance":    round(balance, 3),
        },
        "passed": score >= 0.4,
    }