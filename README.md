---
title: WorkScheduler OpenEnv
emoji: 📅
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
tags:
  - openenv
  - reinforcement-learning
  - scheduling
---

# WorkScheduler-OpenEnv

A real-world AI agent environment for **task scheduling**, built on the
[OpenEnv](https://github.com/meta-pytorch/OpenEnv) framework by Meta and Hugging Face.

The agent acts as a project manager — assigning tasks to workers while
respecting deadlines, skill requirements, worker capacity, and task dependencies.
In harder modes, workers go on leave mid-episode and urgent tasks arrive unexpectedly.

---

## Baseline Scores

| Task | Score | Passed |
|---|---|---|
| Easy | 1.000 | ✅ |
| Medium | 1.000 | ✅ |
| Hard | 0.785 | ✅ |
| Expert | 0.668 | ✅ |

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/info` | GET | Environment metadata |
| `/reset` | POST | Start a new episode |
| `/step` | POST | Agent takes one action |
| `/grade` | POST | Run full grader |
| `/docs` | GET | Interactive API docs |

---

## Quick Example
```python
import requests

BASE = "https://hiteshfirke-workscheduler-openenv.hf.space"

# Start episode
r = requests.post(f"{BASE}/reset", json={"difficulty": "easy"})
session_id = r.json()["session_id"]

# Assign task t2 (Fix login bug) to worker w1 (Alice — has backend skill)
r = requests.post(f"{BASE}/step", json={
    "session_id": session_id,
    "task_id": "t2",
    "worker_id": "w1"
})
print(r.json()["reward"])
# {"value": 0.8, "reason": "Assigned 'Fix login bug' to Alice."}

# Run the full grader
r = requests.post(f"{BASE}/grade", json={"difficulty": "easy"})
print(r.json())
# {"task": "easy", "score": 1.0, "passed": true}
```

---

## Environment Design

### What makes this real-world

- Workers have specific skills — a frontend developer cannot do a security audit
- Tasks have dependencies — you cannot deploy before you test
- Deadlines create urgency — the reward increases for timely assignments
- Dynamic disruptions — workers go on leave, urgent tasks arrive unexpectedly

### Reward function

| Condition | Reward |
|---|---|
| Valid assignment | +0.5 base |
| Skill match | +0.1 |
| High priority task | +0.1 to +0.2 |
| Assigned just in time (≤1 step to deadline) | +0.2 |
| Assigned with buffer (≤3 steps) | +0.15 |
| Assigned early | +0.05 |
| Balanced worker load | +0.1 |
| Ignoring urgent tasks | −0.1 |
| Past deadline | −0.2 |
| Wrong skill | 0.2 (blocked) |
| Worker at capacity | 0.1 (blocked) |

### Difficulty levels

| Level | Tasks | Workers | Deadlines | Skills | Disruptions |
|---|---|---|---|---|---|
| Easy | 5 | 3 | None | Yes | None |
| Medium | 6 | 3 | Yes | Yes | None |
| Hard | 8 | 4 | Tight | Yes | Worker leaves at step 4 |
| Expert | 10+ | 5 | Very tight | Yes | Worker leaves + urgent task injected |

---

## Setup
```bash
git clone https://github.com/HiteshFirke/workscheduler-openenv
cd workscheduler-openenv
pip install -r requirements.txt
python inference.py
```

## Docker
```bash
docker build -t workscheduler-openenv .
docker run -e HF_TOKEN=hf_xxx -p 7860:7860 workscheduler-openenv
```

---

## Author

Hitesh Firke — Scaler OpenEnv Hackathon 2026