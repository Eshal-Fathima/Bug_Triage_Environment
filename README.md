<div align="center">

# 🐛 Bug Triage Environment

**An AI agent benchmark for automated GitHub issue triage**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square)](https://docs.pydantic.dev)
[![OpenEnv](https://img.shields.io/badge/Spec-OpenEnv-6C63FF?style=flat-square)](https://openenv.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

*Built to the OpenEnv specification · 15 real-world tasks · Continuous reward shaping · Model-agnostic*

</div>

---

## Overview

Engineering teams at fast-moving companies receive hundreds of bug reports daily. Manually triaging each one — deciding *what it is*, *how urgent it is*, and *where in the codebase it lives* — burns significant senior engineer time.

**Bug Triage Environment** is a structured benchmark where an AI agent reads GitHub-style issue reports and makes these decisions automatically. It evaluates agent performance across three escalating difficulty levels, using deterministic graders and a continuous reward signal so you can measure and improve model behavior with precision.

> **Why it matters for AI internship applicants:** This project demonstrates the ability to design agentic AI systems from scratch — not just call an API, but define observation spaces, action schemas, reward functions, and evaluation loops — skills directly applicable to ML engineering and AI research roles.

---

## What the Agent Does

Given a GitHub-style bug report (title, body, comments, and optional repo context), the agent must:

| Level | Task | Example |
|-------|------|---------|
| **Easy** | Classify issue type | Is this a `bug`, `feature`, `question`, `documentation`, or `duplicate`? |
| **Medium** | Assign severity | How urgent? `P0` (production down) → `P3` (cosmetic) |
| **Hard** | Locate broken module | Which source file is responsible? e.g. `auth/logout.py` |

---

## Baseline Results

| Model | Easy (5 tasks) | Medium (5 tasks) | Hard (5 tasks) | Overall |
|-------|---------------|-----------------|----------------|---------|
| `llama-3.1-8b-instant` | 1.00 | 0.88 | 0.94 | **0.94** |

> Achieved **0.94 overall score** using an 8B parameter model — demonstrating the environment's accessibility to lightweight inference while maintaining meaningful difficulty at harder levels.

---

## Architecture

```
bug_triage_environment/
├── environment.py    # Core OpenEnv-compliant environment + Pydantic models
├── tasks.py          # 15 hand-crafted issues with gold labels
├── inference.py      # Agent loop with structured [START]/[STEP]/[END] logging
├── app.py            # Flask/API entry point
├── openenv.yaml      # OpenEnv spec metadata
├── Dockerfile        # Containerised deployment
└── requirements.txt
```

### Key Design Decisions

**Typed Pydantic models throughout** — Every input and output is schema-validated. `BugTriageObservation`, `BugTriageAction`, and `BugTriageReward` are all Pydantic models, not raw dicts. This enforces correctness at runtime and makes the environment easy to extend.

**OpenEnv specification compliance** — The environment follows the `reset()` / `step()` / `state()` contract, making it plug-and-play compatible with any OpenEnv-compatible agent runner.

**Strictly bounded rewards** — All reward values are clamped to `(0.01, 0.99)` exclusive as required by the OpenEnv spec. No silent pass/fail — the grader always returns a meaningful signal.

---

## Environment API

### Core Methods

```python
env = BugTriageEnvironment()

obs = env.reset(task_index=0)       # → BugTriageObservation
obs, reward, done, info = env.step(action)  # → (obs, BugTriageReward, bool, dict)
current = env.state()               # → BugTriageObservation (inspect anytime)
```

### Observation Space

```json
{
  "issue_id":  "HARD-001",
  "title":     "JWT tokens are not invalidated after logout",
  "body":      "...",
  "comments":  ["..."],
  "task_type": "locate",
  "context":   { "repo_structure": [...], "description": "..." },
  "step":      0,
  "score":     0.0,
  "done":      false,
  "feedback":  "Task started. Analyse the issue and take an action."
}
```

### Action Space

```python
# Easy — label only
BugTriageAction(label="bug")

# Medium — label + severity
BugTriageAction(label="bug", severity="P1")

# Hard — label + severity + module path
BugTriageAction(label="bug", severity="P0", module="auth/logout.py")
```

---

## Reward Function

Rewards are **continuous and granular**, not binary — the agent receives partial credit for partially correct answers, making gradient-based improvement tractable.

### Easy (label classification)
| Outcome | Reward |
|---------|--------|
| Exact label match | `0.99` |
| Invalid label | `0.02` |
| Wrong label | `0.01` |

### Medium (label + severity)
| Component | Correct | Off by 1 | Off by 2+ |
|-----------|---------|----------|-----------|
| Label (weight 0.30) | `+0.30` | — | `+0.02` |
| Severity (weight 0.68) | `+0.68` | `+0.38` | `+0.10` |

### Hard (label + severity + module)
| Component | Correct | Partial | Wrong |
|-----------|---------|---------|-------|
| Label (0.20) | `+0.20` | — | `+0.02` |
| Severity (0.29) | `+0.29` | `+0.14` | `+0.02` |
| Module (0.49) | `+0.49` | `+0.24` (substring) | `+0.02` |

> All raw scores pass through `clamp()` to stay strictly within `(0.01, 0.99)`.

---

## Tasks

15 real-world GitHub-style issues, hand-crafted across three difficulty tiers:

**Easy (5 tasks) — Label Classification**
The agent reads the issue and assigns the correct type. No severity or code knowledge needed. Grading is binary — right or wrong.

**Medium (5 tasks) — Severity Assignment**
The agent assigns both label and P0–P3 priority based on business impact signals in the text. Partial credit for being one severity level off.

**Hard (5 tasks) — Module Location**
The agent receives the repo directory structure as context and must identify not just what the bug is and how urgent it is, but *which file is responsible*. Partial credit for correct path prefixes.

Sample task (Hard):
```
Issue:  "JWT tokens are not invalidated after logout"
Body:   Users remain logged in after clicking logout. Tokens persist in Redis.
Context: { "repo_structure": ["auth/", "auth/logout.py", "auth/tokens.py", ...] }
Gold:   { label: "bug", severity: "P0", module: "auth/logout.py" }
```

---

## Quickstart

```bash
git clone https://github.com/Eshal-Fathima/Bug_Triage_Environment
cd Bug_Triage_Environment
pip install -r requirements.txt

# Set your API key
export GROQ_API_KEY="gsk_..."        # Mac/Linux
$env:GROQ_API_KEY="gsk_..."          # Windows PowerShell

# Run all 15 tasks
python inference.py

# Run a single task
python inference.py --task 4

# Swap the model
python inference.py --model llama-3.3-70b-versatile
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | API key for Groq inference |
| `API_BASE_URL` | HuggingFace router | LLM API endpoint |
| `MODEL_NAME` | `Qwen/Qwen2.5-72B-Instruct` | Model identifier |

---

## Output Format

Each run produces structured, machine-readable logs:

```
[START] task=EASY-001 env=bug-triage model=llama-3.1-8b-instant
[STEP]  step=1 action={"label": "bug"} reward=0.99 done=true error=null
[END]   success=true steps=1 score=0.99 rewards=0.99
```

```
[START] task=HARD-001 env=bug-triage model=llama-3.1-8b-instant
[STEP]  step=1 action={"label":"bug","severity":"P0","module":"auth/logout.py"} reward=0.98 done=true
[END]   success=true steps=1 score=0.98
```

---

## Docker

```bash
docker build -t bug-triage-env .

# Run with API key
docker run -e GROQ_API_KEY=$GROQ_API_KEY bug-triage-env

# Run with all variables
docker run \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e API_BASE_URL=$API_BASE_URL \
  -e MODEL_NAME=$MODEL_NAME \
  bug-triage-env
```

---

## Skills Demonstrated

- **Agentic AI system design** — Built a full observe → act → reward loop from scratch
- **Pydantic & schema validation** — All I/O is type-safe and runtime-validated
- **Reward engineering** — Designed a multi-component, continuous reward function with partial credit
- **Benchmark design** — 15 curated tasks across 3 difficulty tiers with deterministic grading
- **OpenEnv specification** — Followed an open standard for environment interoperability
- **Docker & deployment** — Containerised for reproducible, portable execution
- **Model-agnostic inference** — Supports any LLM via configurable API endpoints

---

## Extending the Environment

**Add new tasks** — Append to `tasks.py` with any issue_id, title, body, comments, task_type, and gold labels.

**Add a new task type** — Extend the `_evaluate()` method in `environment.py` with a new grader branch.

**Plug in a new model** — Pass `--model <model_name>` or set `MODEL_NAME` — no code changes needed.

---

## About

Built as part of an exploration into AI agent benchmarking and evaluation. The environment follows the [OpenEnv specification](https://openenv.dev) and is designed to be a reproducible, extensible testbed for evaluating how well LLMs can perform structured classification tasks that mirror real engineering workflows.

**Author:** [Eshal Fathima](https://github.com/Eshal-Fathima) · CS Undergrad, Big Data Analytics · SRM University
