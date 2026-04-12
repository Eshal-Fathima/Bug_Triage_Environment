---
title: Bug Triage Env
emoji: 🐛
colorFrom: red
colorTo: purple
sdk: docker
pinned: false
---

# 🐛 Bug Triage Environment

An AI agent evaluation environment where a language model triages GitHub-style issues across three difficulty levels — labelling, severity scoring, and localising the broken module.

## Problem

Software teams waste hours manually sorting incoming bug reports. An AI agent that can correctly classify, prioritise, and locate bugs accelerates developer workflows dramatically.

## Environment

### Core API

| Method | Description |
|---|---|
| `reset(task_index)` | Start a task, returns initial observation |
| `step(action)` | Execute one action, returns `(obs, reward, done, info)` |
| `state()` | Inspect current state at any time |

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
Valid severities: `P0` (critical) → `P3` (cosmetic)

## Tasks

### 🟢 Easy — Label Classification (3 tasks)
Agent reads an issue and assigns the correct label.  
Grading: 1.0 for exact match, 0.0 otherwise.

### 🟡 Medium — Severity Assignment (3 tasks)
Agent assigns label + severity.  
Grading: 0.3 for correct label + 0.7 for correct severity (partial credit within 1 level).

### 🔴 Hard — Module Location (3 tasks)
Agent assigns label + severity + identifies the broken source file.  
Grading: 0.2 (label) + 0.3 (severity) + 0.5 (module, partial credit for path overlap).

## Reward Function

Rewards are **continuous and step-wise**, not just final:

- Correct label always adds to score
- Severity off by 1 level → partial credit (0.4/0.7)
- Module partially matched (substring) → 0.25/0.5
- Invalid action → −0.05 to −0.1 penalty
- All rewards clamped to [0, 1]

## Setup

```bash
git clone https://github.com/Eshal-Fathima/bug_triage_environment
cd bug_triage_environment

pip install -r requirements.txt
export GROQ_API_KEY="gsk_..."   # Windows: $env:GROQ_API_KEY="gsk_..."

# Run all 9 tasks
python inference.py

# Run a single task
python inference.py --task 4

# Use a different model
python inference.py --model llama-3.3-70b-versatile
```

## Output Format

```
[START]
  task_index : 0
  issue_id   : EASY-001
  difficulty : EASY
  task_type  : LABEL
  title      : App crashes when uploading a file larger than 10 MB

[STEP]
  step       : 1
  action     : {"label": "bug"}
  reward     : 1.0000
  feedback   : Correct! Label 'bug' matches ground truth.
  done       : True

[END]
  final_score : 1.0000 / 1.0
  task_type   : EASY (label)
------------------------------------------------------------
```

## Docker

```bash
docker build -t bug-triage .
docker run -e GROQ_API_KEY=$GROQ_API_KEY bug-triage

# Single task
docker run -e GROQ_API_KEY=$GROQ_API_KEY bug-triage \
  python inference.py --task 6 --model llama-3.3-70b-versatile
```

## Project Structure

```
bug_triage_environment/
├── environment.py   # BugTriageEnvironment class (reset/step/state)
├── tasks.py         # 9 issues with gold labels (easy/medium/hard)
├── inference.py     # Agent loop + strict [START]/[STEP]/[END] logging
├── requirements.txt
├── Dockerfile
└── README.md
```
