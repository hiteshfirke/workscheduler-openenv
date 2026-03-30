import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from env import WorkSchedulerEnv, Action

def grade(agent_fn) -> dict:
    env = WorkSchedulerEnv(difficulty="easy")
    obs = env.reset()

    steps = 0
    while not env.done:
        action = agent_fn(obs)
        obs, reward, done, info = env.step(action)
        steps += 1
        if steps > 20:
            break

    state = env.state()
    assigned_count = len(state["assigned"])
    score = round(assigned_count / 5, 3)   # 5 total tasks

    return {
        "task": "easy",
        "score": score,
        "assigned": assigned_count,
        "total": 5,
        "passed": score >= 0.8,
    }