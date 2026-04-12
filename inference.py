import os
import json
import argparse
from dotenv import load_dotenv
from environment import BugTriageEnvironment

# Load API key from .env if it exists
load_dotenv()

def mock_agent(obs):
    """A simple heuristic agent used if no API key is provided."""
    task_type = obs["task_type"]
    if task_type == "label":
        return {"label": "bug"}
    elif task_type == "severity":
        return {"label": "bug", "severity": "P1"}
    elif task_type == "locate":
        return {"label": "bug", "severity": "P0", "module": obs["context"].get("repo_structure", [""])[0]}
    return {"label": "bug"}

def call_llm(obs, model="gpt-3.5-turbo"):
    """Placeholder for actual LLM call using openai library."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        prompt = f"""
        Triage the following bug report:
        Title: {obs['title']}
        Body: {obs['body']}
        Comments: {obs['comments']}
        Task Type: {obs['task_type']}
        Available Context: {obs['context']}

        Return a JSON object with the following keys based on Task Type:
        - label: 'bug', 'feature', 'question', 'documentation', 'duplicate'
        - severity (if medium/hard): 'P0', 'P1', 'P2', 'P3'
        - module (if hard): fully qualified path from context
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return mock_agent(obs)

def run_inference(task_index=None, model="gpt-3.5-turbo"):
    env = BugTriageEnvironment()
    tasks_to_run = [task_index] if task_index is not None else range(len(env.tasks))
    
    total_score = 0.0
    num_tasks = 0

    print("="*60)
    print("Bug Triage Inference Loop")
    print("="*60)

    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found. Running in MOCK mode.\n")

    for i in tasks_to_run:
        obs = env.reset(i)
        
        print(f"[START]")
        print(f"  task_index : {i}")
        print(f"  issue_id   : {obs['issue_id']}")
        print(f"  difficulty : {env.tasks[i]['difficulty']}")
        print(f"  task_type  : {obs['task_type'].upper()}")
        print(f"  title      : {obs['title']}")
        
        # Action
        if os.environ.get("OPENAI_API_KEY"):
            action = call_llm(obs, model=model)
        else:
            action = mock_agent(obs)
            
        # Step
        _, reward, done, info = env.step(action)
        
        print(f"[STEP]")
        print(f"  step       : 1")
        print(f"  action     : {json.dumps(action)}")
        print(f"  reward     : {reward:.4f}")
        print(f"  feedback   : {info.get('feedback', 'No feedback provided.')}")
        print(f"  done       : {done}")
        
        print(f"[END]")
        print(f"  final_score : {reward:.4f} / 1.0")
        print(f"  task_type   : {env.tasks[i]['difficulty']} ({obs['task_type']})")
        print("-" * 60)
        
        total_score += reward
        num_tasks += 1

    avg_score = total_score / num_tasks if num_tasks > 0 else 0
    print(f"\n✅ Inference complete.")
    print(f"Final Average Accuracy: {avg_score * 100:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=int, default=None, help="Index of the task to run (0-8)")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo", help="OpenAI model to use")
    args = parser.parse_args()
    
    run_inference(task_index=args.task, model=args.model)
