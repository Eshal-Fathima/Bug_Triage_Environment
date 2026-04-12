"""
Bug Triage Environment
======================
A simulation environment where an AI agent triages GitHub-style issues.
The agent must label, prioritize, and locate bugs across 3 difficulty levels.
"""

import copy
from tasks import TASKS


class BugTriageEnvironment:
    """
    Simulates a GitHub issue tracker where an AI triages incoming bugs.

    Observation space:
        - issue_id     : str
        - title        : str
        - body         : str
        - comments     : list[str]
        - task_type    : "label" | "severity" | "locate"
        - context      : dict  (repo schema info for 'locate' tasks)

    Action space:
        - label        : str  ("bug" | "feature" | "question" | "documentation" | "duplicate")
        - severity     : str  ("P0" | "P1" | "P2" | "P3")
        - module       : str  (file/module path, for hard tasks)
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
    # Core API
    # ------------------------------------------------------------------

    def reset(self, task_index: int = 0) -> dict:
        """Start a new task. Returns the initial observation."""
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
        return copy.deepcopy(self._state)

    def step(self, action: dict):
        """
        Execute one action.

        Returns:
            (observation, reward, done, info)
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() first.")

        # Sanitize action — coerce all values to strings defensively
        action = self._sanitize_action(action)

        self._steps += 1
        reward, feedback, done = self._evaluate(action)

        self._state["step"]     = self._steps
        self._state["score"]   += reward
        self._state["done"]     = done
        self._state["feedback"] = feedback
        self._done              = done

        info = {
            "task_type"       : self._current_task["task_type"],
            "action_taken"    : action,
            "step_reward"     : reward,
            "cumulative_score": self._state["score"],
        }

        return copy.deepcopy(self._state), reward, done, info

    def state(self) -> dict:
        """Return current state snapshot."""
        return copy.deepcopy(self._state)

    # ------------------------------------------------------------------
    # Sanitizer — handles malformed LLM output gracefully
    # ------------------------------------------------------------------

    def _sanitize_action(self, action: dict) -> dict:
        """Coerce all action values to strings. Handles nested dicts from confused LLMs."""
        clean = {}
        for k, v in action.items():
            if isinstance(v, dict):
                # LLM sometimes returns {"severity": {"value": "P0"}} — flatten it
                inner = list(v.values())
                clean[k] = str(inner[0]) if inner else ""
            else:
                clean[k] = str(v) if v is not None else ""
        return clean

    # ------------------------------------------------------------------
    # Graders
    # ------------------------------------------------------------------

    def _evaluate(self, action: dict):
        task      = self._current_task
        task_type = task["task_type"]
        gold      = task["gold"]

        # ── EASY: Label classification ───────────────────────────────
        if task_type == "label":
            predicted = action.get("label", "").lower().strip()
            if predicted not in self.VALID_LABELS:
                return -0.1, f"Invalid label '{predicted}'. Valid: {self.VALID_LABELS}", True
            if predicted == gold["label"]:
                return 1.0, f"Correct! Label '{predicted}' matches ground truth.", True
            return 0.0, f"Wrong. You said '{predicted}', expected '{gold['label']}'.", True

        # ── MEDIUM: Severity assignment ──────────────────────────────
        if task_type == "severity":
            predicted_label = action.get("label", "").lower().strip()
            predicted_sev   = action.get("severity", "").upper().strip()
            reward, msgs    = 0.0, []

            if predicted_label not in self.VALID_LABELS:
                reward -= 0.05
                msgs.append(f"Invalid label '{predicted_label}'.")
            elif predicted_label == gold["label"]:
                reward += 0.3
                msgs.append("Label correct (+0.3).")
            else:
                msgs.append(f"Wrong label (got '{predicted_label}', expected '{gold['label']}').")

            sev_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
            if predicted_sev not in self.VALID_SEVERITIES:
                reward -= 0.1
                msgs.append(f"Invalid severity '{predicted_sev}'.")
            else:
                diff = abs(sev_order[predicted_sev] - sev_order[gold["severity"]])
                if diff == 0:
                    reward += 0.7; msgs.append("Severity correct (+0.7).")
                elif diff == 1:
                    reward += 0.4; msgs.append(f"Severity off by 1 (+0.4). Expected '{gold['severity']}'.")
                elif diff == 2:
                    reward += 0.1; msgs.append(f"Severity off by 2 (+0.1). Expected '{gold['severity']}'.")
                else:
                    msgs.append(f"Severity very wrong. Expected '{gold['severity']}'.")

            return max(0.0, min(1.0, reward)), " ".join(msgs), True

        # ── HARD: Module location ─────────────────────────────────────
        if task_type == "locate":
            predicted_label  = action.get("label", "").lower().strip()
            predicted_sev    = action.get("severity", "").upper().strip()
            predicted_module = action.get("module", "").lower().strip()
            reward, msgs     = 0.0, []

            # Label (20%)
            if predicted_label == gold["label"]:
                reward += 0.2; msgs.append("Label correct (+0.2).")
            else:
                msgs.append(f"Wrong label (got '{predicted_label}', expected '{gold['label']}').")

            # Severity (30%)
            sev_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
            if predicted_sev in self.VALID_SEVERITIES:
                diff = abs(sev_order.get(predicted_sev, 99) - sev_order[gold["severity"]])
                if diff == 0:
                    reward += 0.3; msgs.append("Severity correct (+0.3).")
                elif diff == 1:
                    reward += 0.15; msgs.append(f"Severity off by 1 (+0.15). Expected '{gold['severity']}'.")
            else:
                msgs.append(f"Invalid severity '{predicted_sev}'.")

            # Module (50%)
            gold_modules = [m.lower() for m in gold.get("modules", [gold.get("module", "")])]
            if predicted_module in gold_modules:
                reward += 0.5; msgs.append("Module exactly correct (+0.5).")
            elif any(predicted_module in gm or gm in predicted_module for gm in gold_modules):
                reward += 0.25; msgs.append(f"Module partially correct (+0.25). Full path: {gold_modules[0]}.")
            else:
                msgs.append(f"Wrong module. Expected one of: {gold_modules}.")

            return max(0.0, min(1.0, reward)), " ".join(msgs), True

        return 0.0, "Unknown task type.", True

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