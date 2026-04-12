---
title: Bug Triage Env
emoji: 🐛
colorFrom: red
colorTo: purple
sdk: docker
pinned: false
---

# Bug Triage Environment

A benchmark environment where an AI agent triages GitHub-style bug reports — classifying issue type, assigning severity, and identifying the broken module. Built to the OpenEnv specification with typed Pydantic models, deterministic graders, and continuous reward shaping across 15 tasks.

---

## Why This Exists

Engineering teams at fast-moving companies receive hundreds of bug reports daily. Manually triaging each one — deciding what it is, how urgent it is, and where in the codebase it lives — consumes significant senior engineer time. This environment benchmarks how well an AI agent can automate that process, and measures performance at three levels of difficulty.

---

## Baseline Results

| Model | Easy (5) | Medium (5) | Hard (5) | Overall |
|---|---|---|---|---|
| llama-3.1-8b-instant | 1.00 | 0.88 | 0.94 | **0.94** |

---

## Environment

### Core API

| Method | Description |
|---|---|
| `reset(task_index)` | Start a task, returns `BugTriageObservation` |
| `step(action)` | Execute one action, returns `(obs, reward, done, info)` |
| `state()` | Inspect current state at any time |

All return types are Pydantic models — `BugTriageObservation`, `BugTriageAction`, `BugTriageReward`.

### Observation Space

```json
{
  "issue_id"  : "HARD-001",
  "title"     : "JWT tokens are not invalidated after logout",
  "body"      : "...",
  "comments"  : ["..."],
  "task_type" : "locate",
  "context"   : { "repo_structure": [...], "description": "..." }
}
```

### Action Space

| Task type | Required keys |
|---|---|
| `label` (easy) | `{"label": "bug"}` |
| `severity` (medium) | `{"label": "bug", "severity": "P1"}` |
| `locate` (hard) | `{"label": "bug", "severity": "P0", "module": "auth/logout.py"}` |

Valid labels: `bug`, `feature`, `question`, `documentation`, `duplicate`
Valid severities: `P0` (production down) → `P3` (cosmetic)

---

## Tasks

15 real-world GitHub-style issues across three difficulty levels.

### Easy — Label Classification (5 tasks)
The agent reads an issue and assigns the correct type label.
Grading: 1.0 for exact match, 0.0 otherwise. Penalty of -0.1 for invalid labels.

### Medium — Severity Assignment (5 tasks)
The agent assigns both a label and a P0–P3 severity based on business impact.
Grading: 0.3 for correct label + 0.7 for correct severity. Partial credit if severity is off by one level.

### Hard — Module Location (5 tasks)
The agent identifies the label, severity, and the specific source file responsible for the bug, given the repo structure.
Grading: 0.2 (label) + 0.3 (severity) + 0.5 (module). Partial credit if the module path partially overlaps.

---

## Reward Function

Rewards are continuous across the full trajectory, not just at episode end:

- Correct label → +0.2 to +0.3 depending on task type
- Severity correct → +0.7 (full) or +0.4 (off by one level) or +0.1 (off by two)
- Module exact match → +0.5
- Module partial match (substring) → +0.25
- Invalid action → -0.05 to -0.1 penalty
- All rewards clamped to [0.0, 1.0]

---

## Setup

```bash
git clone https://github.com/Eshal-Fathima/bug_triage_environment
cd bug_triage_environment
pip install -r requirements.txt

# Set your API key
export GROQ_API_KEY="gsk_..."        # Mac/Linux
$env:GROQ_API_KEY="gsk_..."          # Windows PowerShell

# Run all 15 tasks
python inference.py

# Run a single task by index
python inference.py --task 4

# Run with a different model
python inference.py --model llama-3.3-70b-versatile
```

### Environment Variables

| Variable | Description |
|---|---|
| `API_BASE_URL` | LLM API endpoint (default: HuggingFace router) |
| `MODEL_NAME` | Model identifier (default: Qwen/Qwen2.5-72B-Instruct) |
| `GROQ_API_KEY` | API key for Groq inference |

---

## Output Format

```
[START] task=EASY-001 env=bug-triage model=llama-3.1-8b-instant
[STEP] step=1 action={"label": "bug"} reward=1.00 done=true error=null
[END] success=true steps=1 score=1.00 rewards=1.00
```

---

## Docker

```bash
docker build -t bug-triage-env .
docker run -e GROQ_API_KEY=$GROQ_API_KEY bug-triage-env

# With all variables
docker run \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e API_BASE_URL=$API_BASE_URL \
  -e MODEL_NAME=$MODEL_NAME \
  bug-triage-env
```

---

## Project Structure

```
bug_triage_environment/
├── environment.py    # BugTriageEnvironment + Pydantic models
├── tasks.py          # 15 issues with gold labels across 3 difficulty levels
├── inference.py      # Agent loop with [START]/[STEP]/[END] logging
├── openenv.yaml      # OpenEnv spec metadata
├── requirements.txt
├── Dockerfile
└── README.md
```