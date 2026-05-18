import os
import json
import argparse
from openai import OpenAI
from environment import BugTriageEnvironment, BugTriageAction

# Config from environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
API_KEY      = os.getenv("HF_TOKEN")     or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
BENCHMARK    = "bug-triage"

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL,
)

# System prompt 
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

def build_user_prompt(obs) -> str:
    lines = [
        f"Issue ID: {obs.issue_id}",
        f"Title: {obs.title}",
        "",
        "Description:",
        obs.body,
    ]
    if obs.comments:
        lines.append("\nComments:")
        for c in obs.comments:
            lines.append(f"  - {c}")
    if obs.context:
        if obs.context.get("repo_structure"):
            lines.append("\nRepo file structure (pick module from this list only):")
            for f in obs.context["repo_structure"]:
                lines.append(f"  {f}")
        if obs.context.get("description"):
            lines.append(f"\nArchitecture note: {obs.context['description']}")
    lines.append(f"\nTask type: {obs.task_type}")
    lines.append("Respond with JSON only.")
    return "\n".join(lines)


def query_agent(obs) -> BugTriageAction:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_user_prompt(obs)},
        ],
        temperature=0.0,
        max_tokens=256,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    return BugTriageAction(
        label    = data.get("label"),
        severity = data.get("severity"),
        module   = data.get("module"),
    )


def run_task(env: BugTriageEnvironment, task_index: int) -> dict:
    obs        = env.reset(task_index)
    tasks_meta = env.list_tasks()[task_index]
    task_name  = obs.issue_id
    rewards    = []
    error      = "null"
    success    = False
    step_count = 0

    # [START] line — strict format
    print(f"[START] task={task_name} env={BENCHMARK} model={MODEL_NAME}")

    try:
        action     = query_agent(obs)
        action_str = json.dumps({k: v for k, v in action.model_dump().items() if v is not None})

        new_obs, reward, done, info = env.step(action)

        step_count = new_obs.step
        rewards.append(reward.value)
        success = reward.value >= 0.5

        # [STEP] line — strict format
        print(f"[STEP] step={step_count} action={action_str} reward={reward.value:.2f} done={str(done).lower()} error={error}")

    except Exception as e:
        error   = str(e).replace("\n", " ")
        done    = True
        success = False
        rewards.append(0.0)
        step_count = step_count or 1
        print(f"[STEP] step={step_count} action=null reward=0.00 done=true error={error}")

    score        = rewards[-1] if rewards else 0.0
    rewards_str  = ",".join(f"{r:.2f}" for r in rewards)

    # [END] line — strict format
    print(f"[END] success={str(success).lower()} steps={step_count} score={score:.2f} rewards={rewards_str}")

    return {
        "task_index": task_index,
        "issue_id"  : task_name,
        "difficulty": tasks_meta["difficulty"],
        "task_type" : obs.task_type,
        "score"     : score,
        "success"   : success,
    }


def main():
    parser = argparse.ArgumentParser(description="Bug Triage Environment — Inference Script")
    parser.add_argument("--task", type=int, default=None, help="Run a single task by index (0-8)")
    args = parser.parse_args()

    env     = BugTriageEnvironment()
    results = []

    if args.task is not None:
        results.append(run_task(env, args.task))
    else:
        for i in range(env.num_tasks()):
            results.append(run_task(env, i))

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
