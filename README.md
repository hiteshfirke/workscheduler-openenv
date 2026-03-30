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

A real-world AI agent environment for task scheduling, built on the OpenEnv framework.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/info` | GET | Environment info |
| `/reset` | POST | Start new episode |
| `/step` | POST | Take an action |
| `/grade` | POST | Run full grader |
| `/docs` | GET | Interactive API docs |

## Quick Example
```python
import requests
BASE = "https://hiteshfirke-workscheduler-openenv.hf.space"

r = requests.post(f"{BASE}/reset", json={"difficulty": "easy"})
session_id = r.json()["session_id"]

r = requests.post(f"{BASE}/step", json={
    "session_id": session_id,
    "task_id": "t1",
    "worker_id": "w1"
})
print(r.json()["reward"])
```