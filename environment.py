import json
from tasks import TASKS

class BugTriageEnvironment:
    def __init__(self):
        self.tasks = TASKS
        self.current_task_index = None
        self.current_task = None
        self.done = False

    def reset(self, task_index=0):
        if task_index < 0 or task_index >= len(self.tasks):
            raise IndexError("Task index out of range")
        
        self.current_task_index = task_index
        self.current_task = self.tasks[task_index]
        self.done = False
        
        observation = {
            "issue_id": self.current_task["issue_id"],
            "title": self.current_task["title"],
            "body": self.current_task["body"],
            "comments": self.current_task["comments"],
            "task_type": self.current_task["task_type"],
            "context": self.current_task.get("context", {})
        }
        return observation

    def step(self, action):
        if self.done:
            raise RuntimeError("Environment already done. Call reset().")

        if isinstance(action, str):
            try:
                action = json.loads(action)
            except json.JSONDecodeError:
                return None, -0.1, True, {"error": "Invalid JSON action"}

        gold = self.current_task["gold"]
        task_type = self.current_task["task_type"]
        
        reward = 0.0
        feedback = []

        # 🟢 Easy — Label Classification
        if task_type == "label":
            if action.get("label") == gold["label"]:
                reward = 1.0
                feedback.append(f"Correct! Label '{gold['label']}' matches ground truth.")
            else:
                reward = 0.0
                feedback.append(f"Incorrect label. Expected '{gold['label']}', got '{action.get('label')}'.")

        # 🟡 Medium — Severity Assignment
        elif task_type == "severity":
            # Label component (0.3)
            if action.get("label") == gold["label"]:
                reward += 0.3
                feedback.append(f"Correct label (+0.3).")
                
                # Severity component (0.7)
                pred_sev = action.get("severity")
                gold_sev = gold["severity"]
                if pred_sev == gold_sev:
                    reward += 0.7
                    feedback.append(f"Correct severity (+0.7).")
                else:
                    # Partial credit for off-by-one severity (P0, P1, P2, P3)
                    sev_levels = ["P0", "P1", "P2", "P3"]
                    try:
                        idx_pred = sev_levels.index(pred_sev)
                        idx_gold = sev_levels.index(gold_sev)
                        if abs(idx_pred - idx_gold) == 1:
                            reward += 0.4
                            feedback.append(f"Close severity! Off by one level (+0.4).")
                        else:
                            feedback.append(f"Incorrect severity. Expected '{gold_sev}'.")
                    except ValueError:
                        feedback.append(f"Invalid severity level '{pred_sev}'.")
            else:
                feedback.append(f"Incorrect label. Expected '{gold['label']}'.")

        # 🔴 Hard — Module Location
        elif task_type == "locate":
            # Label (0.2)
            if action.get("label") == gold["label"]:
                reward += 0.2
                feedback.append(f"Correct label (+0.2).")
            
            # Severity (0.3)
            if action.get("severity") == gold["severity"]:
                reward += 0.3
                feedback.append(f"Correct severity (+0.3).")
            
            # Module (0.5)
            pred_mod = action.get("module", "")
            gold_mod = gold["module"]
            if pred_mod == gold_mod:
                reward += 0.5
                feedback.append(f"Correct module (+0.5).")
            elif pred_mod and (pred_mod in gold_mod or gold_mod in pred_mod):
                reward += 0.25
                feedback.append(f"Partial module match (+0.25).")
            else:
                feedback.append(f"Incorrect module. Expected '{gold_mod}'.")

        self.done = True
        return None, round(reward, 4), self.done, {"feedback": " | ".join(feedback)}

    def state(self):
        return {
            "task_index": self.current_task_index,
            "done": self.done,
            "task_id": self.current_task["issue_id"] if self.current_task else None
        }
