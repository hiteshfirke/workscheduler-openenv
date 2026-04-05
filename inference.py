import os, sys, json, asyncio
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN",     "")

if not HF_TOKEN:
    print("ERROR: HF_TOKEN not set.", file=sys.stderr)
    sys.exit(1)

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import WorkSchedulerEnv, Action
from tasks.easy   import grade as grade_easy
from tasks.medium import grade as grade_medium
from tasks.hard   import grade as grade_hard


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error=None):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error or 'null'}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def llm_agent(obs) -> Action:
    pending = "\n".join(
        f"  {t.id}: '{t.name}' priority={t.priority}"
        + (f" deadline=step{t.deadline}" if t.deadline else "")
        + (f" needs={t.depends_on}" if t.depends_on else "")
        + (f" skill={t.required_skill}" if t.required_skill else "")
        for t in obs.pending_tasks
    )
    workers = "\n".join(
        f"  {w.id}: {w.name} [{len(w.assigned_task_ids)}/{w.capacity}]"
        + (" UNAVAILABLE" if not w.available else "")
        + f" skills={w.skills}"
        for w in obs.workers
    )
    prompt = f"""You are a project manager. Assign ONE task to ONE worker.

Step: {obs.current_step}
Already assigned: {list(obs.assigned.keys())}
Budget remaining: {obs.budget_remaining}

Pending tasks:
{pending}

Workers:
{workers}

Rules:
- Only assign if all 'needs' are already assigned
- Do not assign to UNAVAILABLE workers
- Match worker skill to task skill requirement
- Prefer high priority tasks

Reply with ONLY this JSON:
{{"task_id": "t1", "worker_id": "w1"}}"""

    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1,
        )
        text = resp.choices[0].message.content.strip()
        data = json.loads(text[text.index("{"):text.rindex("}")+1])
        return Action(task_id=data["task_id"], worker_id=data["worker_id"])
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", file=sys.stderr)
        return _fallback(obs)


def _fallback(obs) -> Action:
    assigned = set(obs.assigned.keys())
    for task in sorted(obs.pending_tasks, key=lambda t: -t.priority):
        if all(d in assigned for d in task.depends_on):
            for w in obs.workers:
                if w.available and len(w.assigned_task_ids) < w.capacity:
                    if not task.required_skill or task.required_skill in w.skills:
                        return Action(task_id=task.id, worker_id=w.id)
    return Action(
        task_id=obs.pending_tasks[0].id if obs.pending_tasks else "t1",
        worker_id=obs.workers[0].id if obs.workers else "w1"
    )


def run_task(difficulty: str, grade_fn):
    """Run one task, print [START]/[STEP]/[END], return score."""
    env   = WorkSchedulerEnv(difficulty=difficulty)
    obs   = env.reset()
    steps = 0
    rewards = []

    log_start(task=difficulty, env="workscheduler-openenv", model=MODEL_NAME)

    try:
        while not env.done:
            action = llm_agent(obs)
            obs, reward, done, info = env.step(action)
            rewards.append(reward.value)
            steps += 1
            action_str = f"{action.task_id}->{action.worker_id}"
            log_step(step=steps, action=action_str, reward=reward.value, done=done)
            if steps > 30:
                break

        result  = grade_fn(llm_agent)
        score   = result["score"]
        success = result["passed"]

    except Exception as e:
        print(f"[DEBUG] Error: {e}", file=sys.stderr)
        score, success = 0.0, False

    log_end(success=success, steps=steps, score=score, rewards=rewards)
    return score


def main():
    print("=" * 50, flush=True)
    print("  WorkScheduler-OpenEnv — Baseline Inference", flush=True)
    print(f"  Model: {MODEL_NAME}", flush=True)
    print("=" * 50, flush=True)

    results = {}
    for difficulty, grade_fn in [
        ("easy",   grade_easy),
        ("medium", grade_medium),
        ("hard",   grade_hard),
    ]:
        print(f"\n--- Task: {difficulty.upper()} ---", flush=True)
        score = run_task(difficulty, grade_fn)
        results[difficulty] = score

    avg = sum(results.values()) / len(results)
    print(f"\nAverage score: {avg:.3f}", flush=True)

    with open("scores.json", "w") as f:
        json.dump({
            "scores":  results,
            "average": round(avg, 3),
            "model":   MODEL_NAME,
        }, f, indent=2)
    print("Scores saved to scores.json", flush=True)


if __name__ == "__main__":
    main()