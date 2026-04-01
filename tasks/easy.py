import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from env import WorkSchedulerEnv, Action

def grade(agent_fn) -> dict:
    env = WorkSchedulerEnv(difficulty="easy")
    obs = env.reset()
    total_tasks = len(obs.pending_tasks)   # ← get total dynamically

    steps = 0
    while not env.done:
        action = agent_fn(obs)
        obs, reward, done, info = env.step(action)
        steps += 1
        if steps > 50:                     # ← increased limit for 20 tasks
            break

    state = env.state()
    assigned_count = len(state["assigned"])
    score = round(assigned_count / total_tasks, 3)

    return {
        "task": "easy",
        "score": score,
        "assigned": assigned_count,
        "total": total_tasks,              # ← now dynamic
        "passed": score >= 0.8,
    }