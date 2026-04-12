"""
inference.py
============
Runs the AI agent through all tasks in the Bug Triage Environment.

Usage:
    python inference.py                          # run all tasks
    python inference.py --task 0                 # run single task by index
    python inference.py --model llama-3.1-8b-instant  # specify model

Output strictly follows the required format:
    [START]  ... task header
    [STEP]   ... each agent action + env response
    [END]    ... final score summary
"""

import os
import json
import argparse
from groq import Groq

from environment import BugTriageEnvironment

# ── Groq client (reads GROQ_API_KEY from environment) ─────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── System prompt ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert software engineering triage agent.
You will be shown a GitHub-style issue and must respond with a JSON object.

IMPORTANT — follow these JSON formats EXACTLY depending on task type:

task type = label
  {"label": "bug"}
  Valid label values: bug, feature, question, documentation, duplicate

task type = severity
  {"label": "bug", "severity": "P1"}
  Valid label values: bug, feature, question, documentation, duplicate
  Valid severity values: P0, P1, P2, P3
  Severity meaning:
    P0 = production down, security breach, or data loss
    P1 = major feature broken, significant user impact
    P2 = non-critical bug, workaround exists
    P3 = cosmetic or minor inconvenience

task type = locate
  {"label": "bug", "severity": "P0", "module": "auth/logout.py"}
  Same label and severity values as above.
  For module: pick exactly one file path from the repo_structure list provided.

RULES:
- Output ONLY the JSON object. No explanation, no markdown, no extra text.
- All keys and string values must be lowercase except severity (P0/P1/P2/P3).
- Never put descriptions inside the severity field — only P0, P1, P2, or P3.
"""

def build_user_prompt(obs: dict) -> str:
    lines = [
        f"Issue ID: {obs['issue_id']}",
        f"Title: {obs['title']}",
        f"",
        f"Description:",
        obs["body"],
    ]

    if obs.get("comments"):
        lines.append("\nComments:")
        for c in obs["comments"]:
            lines.append(f"  - {c}")

    if obs.get("context"):
        ctx = obs["context"]
        if ctx.get("repo_structure"):
            lines.append("\nRepo file structure (pick module from this list only):")
            for f in ctx["repo_structure"]:
                lines.append(f"  {f}")
        if ctx.get("description"):
            lines.append(f"\nArchitecture note: {ctx['description']}")

    lines.append(f"\nTask type: {obs['task_type']}")
    lines.append("Respond with JSON only.")
    return "\n".join(lines)


def query_agent(obs: dict, model: str) -> dict:
    user_prompt = build_user_prompt(obs)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=256,
    )

    raw = response.choices[0].message.content.strip()

    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw_response": raw, "parse_error": True}


def run_task(env: BugTriageEnvironment, task_index: int, model: str) -> dict:
    obs        = env.reset(task_index)
    tasks_meta = env.list_tasks()[task_index]

    print(f"\n[START]")
    print(f"  task_index : {task_index}")
    print(f"  issue_id   : {obs['issue_id']}")
    print(f"  difficulty : {tasks_meta['difficulty'].upper()}")
    print(f"  task_type  : {obs['task_type'].upper()}")
    print(f"  title      : {obs['title']}")

    action = query_agent(obs, model)

    new_obs, reward, done, info = env.step(action)

    print(f"\n[STEP]")
    print(f"  step       : {new_obs['step']}")
    print(f"  action     : {json.dumps(action)}")
    print(f"  reward     : {reward:.4f}")
    print(f"  feedback   : {new_obs['feedback']}")
    print(f"  done       : {done}")

    print(f"\n[END]")
    print(f"  final_score : {new_obs['score']:.4f} / 1.0")
    print(f"  task_type   : {tasks_meta['difficulty'].upper()} ({obs['task_type']})")
    print("-" * 60)

    return {
        "task_index": task_index,
        "issue_id"  : obs["issue_id"],
        "difficulty": tasks_meta["difficulty"],
        "task_type" : obs["task_type"],
        "action"    : action,
        "reward"    : reward,
        "feedback"  : new_obs["feedback"],
        "score"     : new_obs["score"],
    }


def main():
    parser = argparse.ArgumentParser(description="Bug Triage Environment — Inference Script")
    parser.add_argument("--task",  type=int, default=None,                   help="Run a single task by index (0-8)")
    parser.add_argument("--model", type=str, default="llama-3.1-8b-instant", help="Groq model to use")
    args = parser.parse_args()

    env     = BugTriageEnvironment()
    results = []

    if args.task is not None:
        results.append(run_task(env, args.task, args.model))
    else:
        for i in range(env.num_tasks()):
            results.append(run_task(env, i, args.model))

    if len(results) > 1:
        by_diff = {}
        for r in results:
            by_diff.setdefault(r["difficulty"], []).append(r["score"])

        print("\n" + "=" * 60)
        print("FINAL SUMMARY")
        print("=" * 60)
        for diff, scores in sorted(by_diff.items()):
            avg = sum(scores) / len(scores)
            print(f"  {diff.upper():8s}  avg={avg:.4f}  scores={[f'{s:.2f}' for s in scores]}")
        overall = sum(r["score"] for r in results) / len(results)
        print(f"\n  OVERALL AVERAGE SCORE : {overall:.4f} / 1.0")
        print("=" * 60)


if __name__ == "__main__":
    main()