import os, sys, json
from openai import OpenAI

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.environ.get("HF_TOKEN",     "")

if not HF_TOKEN:
    print("ERROR: HF_TOKEN not set.", file=sys.stderr)
    sys.exit(1)

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import WorkSchedulerEnv, Action
from tasks.easy   import grade as grade_easy
from tasks.medium import grade as grade_medium
from tasks.hard   import grade as grade_hard


def llm_agent(obs) -> Action:
    """Ask the LLM which task to assign to which worker."""

    pending = "\n".join(
        f"  {t.id}: '{t.name}' priority={t.priority}"
        + (f" deadline=step{t.deadline}" if t.deadline else "")
        + (f" needs={t.depends_on}"      if t.depends_on else "")
        for t in obs.pending_tasks
    )
    workers = "\n".join(
        f"  {w.id}: {w.name} [{len(w.assigned_task_ids)}/{w.capacity} tasks]"
        + (" UNAVAILABLE" if not w.available else "")
        for w in obs.workers
    )

    prompt = f"""You are a project manager. Assign ONE task to ONE worker.

Step: {obs.current_step}
Already assigned: {list(obs.assigned.keys())}

Pending tasks:
{pending}

Workers:
{workers}

Rules:
- Only assign a task if all its 'needs' are already assigned
- Do not assign to UNAVAILABLE workers
- Prefer high priority tasks (priority 3)
- Do not exceed worker capacity

Reply with ONLY this JSON, nothing else:
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
        print(f"  LLM error: {e} — using fallback", file=sys.stderr)
        return _fallback(obs)


def _fallback(obs) -> Action:
    """Greedy fallback if LLM fails."""
    assigned = set(obs.assigned.keys())
    for task in sorted(obs.pending_tasks, key=lambda t: -t.priority):
        if all(d in assigned for d in task.depends_on):
            for w in obs.workers:
                if w.available and len(w.assigned_task_ids) < w.capacity:
                    return Action(task_id=task.id, worker_id=w.id)
    return Action(
        task_id=obs.pending_tasks[0].id,
        worker_id=obs.workers[0].id
    )


def main():
    print("=" * 50)
    print("  WorkScheduler-OpenEnv — Baseline Inference")
    print(f"  Model: {MODEL_NAME}")
    print("=" * 50)

    results = {}
    for difficulty, grade_fn in [
        ("easy",   grade_easy),
        ("medium", grade_medium),
        ("hard",   grade_hard),
    ]:
        print(f"\nRunning: {difficulty.upper()}")
        result = grade_fn(llm_agent)
        results[difficulty] = result
        print(f"  Score: {result['score']} | Passed: {result['passed']}")

    avg = sum(r["score"] for r in results.values()) / 3
    print(f"\nAverage score: {avg:.3f}")
    print("=" * 50)

    with open("scores.json", "w") as f:
        json.dump({
            "scores":