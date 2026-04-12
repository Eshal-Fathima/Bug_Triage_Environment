TASKS = [
    {
        "issue_id": "EASY-001",
        "title": "Application crashes when uploading a file larger than 10MB",
        "body": "Steps to reproduce: 1. Go to upload page. 2. Select a 15MB file. 3. App freezes and crashes.",
        "comments": ["Maybe we should add a size limit check?", "I noticed this on the dev branch too."],
        "task_type": "label",
        "gold": {"label": "bug"},
        "difficulty": "EASY"
    },
    {
        "issue_id": "EASY-002",
        "title": "Request to add Dark Mode support",
        "body": "The current light theme is too bright for late-night coding. Dark mode would be highly appreciated.",
        "comments": ["+1", "We can use CSS variables for this."],
        "task_type": "label",
        "gold": {"label": "feature"},
        "difficulty": "EASY"
    },
    {
        "issue_id": "EASY-003",
        "title": "How do I regenerate my API key?",
        "body": "I lost my API key and need to regenerate it. I can't find the button in settings.",
        "comments": ["It's under Settings > Security."],
        "task_type": "label",
        "gold": {"label": "question"},
        "difficulty": "EASY"
    },
    {
        "issue_id": "MED-001",
        "title": "Payment gateway timeout on checkout",
        "body": "Users are reporting timeouts during checkout. This is preventing sales.",
        "comments": ["I see 504 errors in the logs.", "Critical: affecting revenue."],
        "task_type": "severity",
        "gold": {"label": "bug", "severity": "P0"},
        "difficulty": "MEDIUM"
    },
    {
        "issue_id": "MED-002",
        "title": "Broken link in footer of Home page",
        "body": "The 'Privacy Policy' link in the footer leads to a 404 page.",
        "comments": [],
        "task_type": "severity",
        "gold": {"label": "bug", "severity": "P2"},
        "difficulty": "MEDIUM"
    },
    {
        "issue_id": "MED-003",
        "title": "Missing examples in API documentation for /search endpoint",
        "body": "The search endpoint documentation doesn't show the expected response format.",
        "comments": [],
        "task_type": "severity",
        "gold": {"label": "documentation", "severity": "P3"},
        "difficulty": "MEDIUM"
    },
    {
        "issue_id": "HARD-001",
        "title": "JWT tokens are not invalidated after logout",
        "body": "Security audit found that old JWT tokens can still be used for 15 minutes after the user logs out.",
        "comments": ["This is high priority.", "Needs a blocklist in Redis."],
        "task_type": "locate",
        "gold": {"label": "bug", "severity": "P0", "module": "auth/logout.py"},
        "difficulty": "HARD",
        "context": {"repo_structure": ["auth/login.py", "auth/logout.py", "auth/utils.py", "main.py"]}
    },
    {
        "issue_id": "HARD-002",
        "title": "Memory leak in image processing worker",
        "body": "Worker nodes are running out of RAM after processing several high-res images.",
        "comments": ["Probably the 'Pillow' handles aren't being closed properly."],
        "task_type": "locate",
        "gold": {"label": "bug", "severity": "P1", "module": "workers/image_proc.py"},
        "difficulty": "HARD",
        "context": {"repo_structure": ["workers/image_proc.py", "workers/base.py", "utils/image.py"]}
    },
    {
        "issue_id": "HARD-003",
        "title": "SQL injection vulnerability in user search filter",
        "body": "Found a potential SQL injection when searching users by name and using special characters.",
        "comments": ["We need to use parameterized queries."],
        "task_type": "locate",
        "gold": {"label": "bug", "severity": "P0", "module": "db/queries.py"},
        "difficulty": "HARD",
        "context": {"repo_structure": ["db/schema.sql", "db/queries.py", "api/users.py"]}
    }
]
