"""
Bug Triage Environment
======================
Full OpenEnv-compliant environment with Pydantic typed models.
Scores are strictly within (0.0, 1.0) exclusive as required by OpenEnv spec.
"""

import copy
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from tasks import TASKS

SCORE_MIN = 0.01
SCORE_MAX = 0.99

def clamp(value: float) -> float:
    """Clamp score to strictly (0, 1) exclusive."""
    return max(SCORE_MIN, min(SCORE_MAX, round(value, 4)))


# ── Pydantic Models ────────────────────────────────────────────────────

class BugTriageObservation(BaseModel):
    issue_id:  str
    title:     str
    body:      str
    comments:  List[str] = []
    task_type: str
    context:   Dict[str, Any] = {}
    step:      int = 0
    score:     float = 0.0
    done:      bool = False
    feedback:  str = ""

class BugTriageAction(BaseModel):
    label:    Optional[str] = None
    severity: Optional[str] = None
    module:   Optional[str] = None

class BugTriageReward(BaseModel):
    value:    float = Field(..., gt=0.0, lt=1.0)
    feedback: str = ""
    done:     bool = False


# ── Environment ────────────────────────────────────────────────────────

class BugTriageEnvironment:
    """
    Simulates a GitHub issue tracker where an AI triages incoming bugs.

    Observation space : BugTriageObservation
    Action space      : BugTriageAction
    Reward            : BugTriageReward strictly in (0.0, 1.0)
    """

    VALID_LABELS     = {"bug", "feature", "question", "documentation", "duplicate"}
    VALID_SEVERITIES = {"P0", "P1", "P2", "P3"}

    def __init__(self):
        self._tasks         = copy.deepcopy(TASKS)
        self._current_task  = None
        self._current_index = 0
        self._state         = {}
        self._done          = False
        self._steps         = 0

    # ------------------------------------------------------------------
    # Core OpenEnv API
    # ------------------------------------------------------------------

    def reset(self, task_index: int = 0) -> BugTriageObservation:
        self._current_index = task_index
        self._current_task  = copy.deepcopy(self._tasks[task_index])
        self._done          = False
        self._steps         = 0

        self._state = {
            "issue_id" : self._current_task["issue_id"],
            "title"    : self._current_task["title"],
            "body"     : self._current_task["body"],
            "comments" : self._current_task.get("comments", []),
            "task_type": self._current_task["task_type"],
            "context"  : self._current_task.get("context", {}),
            "step"     : 0,
            "score"    : 0.0,
            "done"     : False,
            "feedback" : "Task started. Analyse the issue and take an action.",
        }
        return BugTriageObservation(**self._state)

    def step(self, action: BugTriageAction):
        if self._done:
            raise RuntimeError("Episode is done. Call reset() first.")

        action_dict = self._sanitize_action(action)

        self._steps += 1
        raw_reward, feedback, done = self._evaluate(action_dict)
        reward_val = clamp(raw_reward)

        self._state["step"]     = self._steps
        self._state["score"]   += reward_val
        self._state["done"]     = done
        self._state["feedback"] = feedback
        self._done              = done

        obs    = BugTriageObservation(**self._state)
        reward = BugTriageReward(value=reward_val, feedback=feedback, done=done)
        info   = {
            "task_type"       : self._current_task["task_type"],
            "action_taken"    : action_dict,
            "step_reward"     : reward_val,
            "cumulative_score": self._state["score"],
        }

        return obs, reward, done, info

    def state(self) -> BugTriageObservation:
        return BugTriageObservation(**self._state)

    # ------------------------------------------------------------------
    # Sanitizer
    # ------------------------------------------------------------------

    def _sanitize_action(self, action) -> dict:
        if isinstance(action, BugTriageAction):
            raw = {"label": action.label, "severity": action.severity, "module": action.module}
        elif isinstance(action, dict):
            raw = action
        else:
            raw = {}

        clean = {}
        for k, v in raw.items():
            if v is None:
                clean[k] = ""
            elif isinstance(v, dict):
                inner = list(v.values())
                clean[k] = str(inner[0]) if inner else ""
            else:
                clean[k] = str(v)
        return clean

    # ------------------------------------------------------------------
    # Graders — all raw scores mapped through clamp()
    # ------------------------------------------------------------------

    def _evaluate(self, action: dict):
        task      = self._current_task
        task_type = task["task_type"]
        gold      = task["gold"]

        # EASY
        if task_type == "label":
            predicted = action.get("label", "").lower().strip()
            if predicted not in self.VALID_LABELS:
                return 0.02, f"Invalid label '{predicted}'.", True
            if predicted == gold["label"]:
                return 0.99, f"Correct! Label '{predicted}' matches ground truth.", True
            return 0.01, f"Wrong. You said '{predicted}', expected '{gold['label']}'.", True

        # MEDIUM
        if task_type == "severity":
            predicted_label = action.get("label", "").lower().strip()
            predicted_sev   = action.get("severity", "").upper().strip()
            reward, msgs    = 0.0, []

            if predicted_label not in self.VALID_LABELS:
                reward += 0.02
                msgs.append(f"Invalid label '{predicted_label}'.")
            elif predicted_label == gold["label"]:
                reward += 0.30
                msgs.append("Label correct (+0.30).")
            else:
                reward += 0.02
                msgs.append(f"Wrong label (got '{predicted_label}', expected '{gold['label']}').")

            sev_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
            if predicted_sev not in self.VALID_SEVERITIES:
                reward += 0.02
                msgs.append(f"Invalid severity '{predicted_sev}'.")
            else:
                diff = abs(sev_order[predicted_sev] - sev_order[gold["severity"]])
                if diff == 0:
                    reward += 0.68; msgs.append("Severity correct (+0.68).")
                elif diff == 1:
                    reward += 0.38; msgs.append(f"Severity off by 1 (+0.38). Expected '{gold['severity']}'.")
                elif diff == 2:
                    reward += 0.10; msgs.append(f"Severity off by 2 (+0.10). Expected '{gold['severity']}'.")
                else:
                    reward += 0.02; msgs.append(f"Severity very wrong. Expected '{gold['severity']}'.")

            return clamp(reward), " ".join(msgs), True

        # HARD
        if task_type == "locate":
            predicted_label  = action.get("label", "").lower().strip()
            predicted_sev    = action.get("severity", "").upper().strip()
            predicted_module = action.get("module", "").lower().strip()
            reward, msgs     = 0.0, []

            if predicted_label == gold["label"]:
                reward += 0.20; msgs.append("Label correct (+0.20).")
            else:
                reward += 0.02; msgs.append(f"Wrong label (got '{predicted_label}', expected '{gold['label']}').")

            sev_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
            if predicted_sev in self.VALID_SEVERITIES:
                diff = abs(sev_order.get(predicted_sev, 99) - sev_order[gold["severity"]])
                if diff == 0:
                    reward += 0.29; msgs.append("Severity correct (+0.29).")
                elif diff == 1:
                    reward += 0.14; msgs.append(f"Severity off by 1 (+0.14). Expected '{gold['severity']}'.")
                else:
                    reward += 0.02; msgs.append(f"Severity wrong. Expected '{gold['severity']}'.")
            else:
                reward += 0.02; msgs.append(f"Invalid severity '{predicted_sev}'.")

            gold_modules = [m.lower() for m in gold.get("modules", [gold.get("module", "")])]
            if predicted_module in gold_modules:
                reward += 0.49; msgs.append("Module exactly correct (+0.49).")
            elif any(predicted_module in gm or gm in predicted_module for gm in gold_modules):
                reward += 0.24; msgs.append(f"Module partially correct (+0.24). Full path: {gold_modules[0]}.")
            else:
                reward += 0.02; msgs.append(f"Wrong module. Expected one of: {gold_modules}.")

            return clamp(reward), " ".join(msgs), True

        return 0.05, "Unknown task type.", True

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def list_tasks(self):
        return [
            {
                "index"     : i,
                "issue_id"  : t["issue_id"],
                "title"     : t["title"],
                "task_type" : t["task_type"],
                "difficulty": t["difficulty"],
            }
            for i, t in enumerate(self._tasks)
        ]

    def num_tasks(self):
        return len(self._tasks)