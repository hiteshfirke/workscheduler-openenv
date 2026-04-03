import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from env import WorkSchedulerEnv, Action

def grade(agent_fn) -> dict:
    env = WorkSchedulerEnv(difficulty="multi")
    obs = env.reset()

    deadline_hits  = 0
    deadline_total = 0
    skill_matches  = 0
    skill_total    = 0
    project_done   = {"frontend": False, "backend": False, "infra": False}
    steps = 0

    while not env.done:
        action = agent_fn(obs)

        task_obj   = next((t for t in obs.pending_tasks if t.id == action.task_id), None)
        worker_obj = next((w for w in obs.workers       if w.id == action.worker_id), None)

        if task_obj and worker_obj:
            if task_obj.required_skill:
                skill_total += 1
                if task_obj.required_skill in worker_obj.skills:
                    skill_matches += 1
            if task_obj.deadline is not None:
                deadline_total += 1
                if obs.current_step + 1 <= task_obj.deadline:
                    deadline_hits += 1

        obs, reward, done, info = env.step(action)
        steps += 1
        if steps > 60:
            break

    state = env.state()
    assigned = state["assigned"]

    # Check which projects are fully complete
    frontend_ids = {"f1","f2","f3","f4","f5"}
    backend_ids  = {"b1","b2","b3","b4","b5"}
    infra_ids    = {"i1","i2","i3","i4","i5"}

    assigned_set = set(assigned.keys())
    project_done["frontend"] = frontend_ids.issubset(assigned_set)
    project_done["backend"]  = backend_ids.issubset(assigned_set)
    project_done["infra"]    = infra_ids.issubset(assigned_set)

    projects_completed = sum(project_done.values())
    completion  = len(assigned) / 15        # 15 total tasks
    deadlines   = deadline_hits / max(deadline_total, 1)
    skills      = skill_matches / max(skill_total, 1)
    proj_score  = projects_completed / 3    # bonus for full project completion

    score = round(
        completion * 0.35 +
        deadlines  * 0.25 +
        skills     * 0.20 +
        proj_score * 0.20,
        3
    )
    score = max(0.0, min(1.0, score))

    return {
        "task": "multi",
        "score": score,
        "breakdown": {
            "completion":          round(completion, 3),
            "deadlines":           round(deadlines, 3),
            "skill_matching":      round(skills, 3),
            "projects_completed":  f"{projects_completed}/3",
            "project_status":      project_done,
        },
        "passed": score >= 0.5,
    }