"""
Task definitions for the Bug Triage Environment.

3 difficulty tiers × 3 issues each = 9 tasks total.

EASY   (task_type="label")    → classify the issue type
MEDIUM (task_type="severity") → label + assign P0–P3 severity
HARD   (task_type="locate")   → label + severity + identify the broken module
"""

TASKS = [

    # ══════════════════════════════════════════════════════════════════
    # EASY — Label classification
    # ══════════════════════════════════════════════════════════════════

    {
        "issue_id"  : "EASY-001",
        "difficulty": "easy",
        "task_type" : "label",
        "title"     : "App crashes when uploading a file larger than 10 MB",
        "body"      : (
            "Steps to reproduce:\n"
            "1. Log in to the app.\n"
            "2. Navigate to Settings > Upload.\n"
            "3. Select any file > 10 MB.\n"
            "Result: The app throws an unhandled exception and crashes.\n"
            "Expected: A user-friendly error message should appear."
        ),
        "comments"  : [
            "Confirmed on v2.3.1 and v2.4.0.",
            "Happens on both Chrome and Firefox.",
        ],
        "gold"      : {"label": "bug"},
    },

    {
        "issue_id"  : "EASY-002",
        "difficulty": "easy",
        "task_type" : "label",
        "title"     : "Add dark mode support to the dashboard",
        "body"      : (
            "Many users have requested a dark mode option.\n"
            "Currently the dashboard only supports light theme.\n"
            "Please add a toggle in user preferences to switch themes."
        ),
        "comments"  : [
            "+1 from design team, mocks already exist.",
            "This would also improve accessibility.",
        ],
        "gold"      : {"label": "feature"},
    },

    {
    "issue_id"  : "EASY-003",
    "difficulty": "easy",
    "task_type" : "label",
    "title"     : "How do I reset my password?",
    "body"      : (
        "Hi, I have a question about resetting my password.\n"
        "I cannot find the password reset option anywhere.\n"
        "I've checked the account settings and the login page.\n"
        "Can someone please help me? Where do I find this option?"
    ),
    "comments"  : [
        "This is covered in our docs at /docs/account/password-reset.",
    ],
    "gold" : {"label": "documentation"},
    },

    # ══════════════════════════════════════════════════════════════════
    # MEDIUM — Label + Severity
    # ══════════════════════════════════════════════════════════════════

    {
        "issue_id"  : "MED-001",
        "difficulty": "medium",
        "task_type" : "severity",
        "title"     : "Payment processing fails for all users — production down",
        "body"      : (
            "As of 14:32 UTC, no user can complete a checkout.\n"
            "The Stripe webhook returns 500 on every transaction.\n"
            "Revenue impact: ~$12,000/minute.\n"
            "All payment-related endpoints are affected."
        ),
        "comments"  : [
            "CEO has been notified.",
            "On-call engineer is investigating.",
            "Rollback to v3.1.2 did not help.",
        ],
        "gold"      : {"label": "bug", "severity": "P0"},
    },

    {
        "issue_id"  : "MED-002",
        "difficulty": "medium",
        "task_type" : "severity",
        "title"     : "Profile picture does not update immediately after upload",
        "body"      : (
            "After uploading a new profile picture, the old image\n"
            "is still displayed in the navbar for ~30 seconds.\n"
            "Refreshing the page shows the correct image.\n"
            "This seems to be a cache invalidation delay."
        ),
        "comments"  : [
            "Reproducible on all browsers.",
            "Does not affect functionality.",
        ],
        "gold"      : {"label": "bug", "severity": "P3"},
    },

    {
        "issue_id"  : "MED-003",
        "difficulty": "medium",
        "task_type" : "severity",
        "title"     : "Export to CSV silently drops rows with special characters",
        "body"      : (
            "When exporting data that contains Unicode characters (e.g., é, ñ, 中),\n"
            "those rows are missing from the downloaded CSV.\n"
            "No error is shown to the user.\n"
            "Affects ~15% of our enterprise customer data."
        ),
        "comments"  : [
            "Confirmed by 3 enterprise customers.",
            "Workaround: manually sanitize data before export.",
        ],
        "gold"      : {"label": "bug", "severity": "P1"},
    },

    # ══════════════════════════════════════════════════════════════════
    # HARD — Label + Severity + Module
    # ══════════════════════════════════════════════════════════════════

    {
        "issue_id"  : "HARD-001",
        "difficulty": "hard",
        "task_type" : "locate",
        "title"     : "JWT tokens are not invalidated after user logout",
        "body"      : (
            "After logging out, the old JWT token can still be used\n"
            "to make authenticated API requests.\n"
            "Tokens remain valid until their 24-hour expiry.\n"
            "This is a security vulnerability — stolen tokens cannot be revoked."
        ),
        "comments"  : [
            "Pen test team flagged this as high severity.",
            "No token blacklist or session store is implemented.",
        ],
        "context"   : {
            "repo_structure": [
                "auth/login.py",
                "auth/logout.py",
                "auth/token_validator.py",
                "auth/middleware.py",
                "users/profile.py",
                "users/settings.py",
                "api/routes.py",
                "api/middleware.py",
                "db/models.py",
                "db/session.py",
            ],
            "description": (
                "auth/ handles all authentication logic. "
                "api/middleware.py validates tokens on each request. "
                "db/session.py manages database sessions."
            ),
        },
        "gold"      : {
            "label"   : "bug",
            "severity": "P0",
            "modules" : ["auth/logout.py", "auth/token_validator.py"],
        },
    },

    {
        "issue_id"  : "HARD-002",
        "difficulty": "hard",
        "task_type" : "locate",
        "title"     : "Date picker ignores user's local timezone — shows UTC",
        "body"      : (
            "When scheduling a report, the date picker displays times in UTC\n"
            "regardless of the user's browser timezone setting.\n"
            "Users in GMT+5:30 are seeing events 5.5 hours off.\n"
            "Scheduled reports are then sent at the wrong time."
        ),
        "comments"  : [
            "Only affects the scheduling modal, not the dashboard calendar.",
            "Introduced in PR #441 three weeks ago.",
        ],
        "context"   : {
            "repo_structure": [
                "components/DatePicker.jsx",
                "components/Calendar.jsx",
                "components/ScheduleModal.jsx",
                "components/ReportForm.jsx",
                "utils/dateUtils.js",
                "utils/formatters.js",
                "api/scheduler.py",
                "api/reports.py",
            ],
            "description": (
                "components/ holds React UI. utils/dateUtils.js centralises "
                "all date/time conversion helpers. api/scheduler.py handles "
                "backend report scheduling."
            ),
        },
        "gold"      : {
            "label"   : "bug",
            "severity": "P1",
            "modules" : ["components/ScheduleModal.jsx", "utils/dateUtils.js"],
        },
    },

    {
        "issue_id"  : "HARD-003",
        "difficulty": "hard",
        "task_type" : "locate",
        "title"     : "Search returns duplicate results when pagination is used",
        "body"      : (
            "When browsing search results across multiple pages,\n"
            "the same items appear on page 1 and page 2.\n"
            "This happens when new records are inserted between page loads.\n"
            "The issue is consistent with a missing stable sort/cursor."
        ),
        "comments"  : [
            "Reproducible with any search query that returns > 20 results.",
            "Elasticsearch version: 8.9.0.",
        ],
        "context"   : {
            "repo_structure": [
                "search/engine.py",
                "search/indexer.py",
                "search/pagination.py",
                "search/filters.py",
                "api/search_routes.py",
                "api/middleware.py",
                "db/models.py",
                "db/query_builder.py",
            ],
            "description": (
                "search/ contains all search logic. search/pagination.py handles "
                "page offsets and cursors. search/engine.py sends queries to Elasticsearch."
            ),
        },
        "gold"      : {
            "label"   : "bug",
            "severity": "P2",
            "modules" : ["search/pagination.py", "search/engine.py"],
        },
    },
]