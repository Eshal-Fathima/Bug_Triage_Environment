"""
Task definitions for the Bug Triage Environment.
15 tasks total — 5 per difficulty level.
"""

TASKS = [

    # ══════════════════════════════════════════════════════════════════
    # EASY — Label classification (5 tasks)
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
        "gold"      : {"label": "documentation"},
    },

    {
        "issue_id"  : "EASY-004",
        "difficulty": "easy",
        "task_type" : "label",
        "title"     : "Login button unresponsive on Safari 17",
        "body"      : (
            "On Safari 17.2, clicking the login button does nothing.\n"
            "No error in console. Works fine on Chrome and Firefox.\n"
            "Tested on macOS Ventura and Sonoma — same result.\n"
            "Users on Safari cannot log in at all."
        ),
        "comments"  : [
            "Reproduced by 3 team members on Safari.",
            "Likely a JS compatibility issue.",
        ],
        "gold"      : {"label": "bug"},
    },

    {
        "issue_id"  : "EASY-005",
        "difficulty": "easy",
        "task_type" : "label",
        "title"     : "This issue was already reported in #1042",
        "body"      : (
            "I'm seeing the same crash as reported in issue #1042.\n"
            "The file upload crash happens for me too.\n"
            "Marking this as a repeat of the existing report."
        ),
        "comments"  : [
            "Confirmed — exact same stack trace as #1042.",
        ],
        "gold"      : {"label": "duplicate"},
    },

    # ══════════════════════════════════════════════════════════════════
    # MEDIUM — Label + Severity (5 tasks)
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

    {
        "issue_id"  : "MED-004",
        "difficulty": "medium",
        "task_type" : "severity",
        "title"     : "Admin dashboard shows incorrect user count",
        "body"      : (
            "The user count on the admin dashboard shows 1,240 users\n"
            "but the database query returns 1,312 users.\n"
            "The discrepancy appears to be due to a cached value\n"
            "that is only refreshed every 24 hours.\n"
            "No users are affected directly — admins only."
        ),
        "comments"  : [
            "Noticed during quarterly review.",
            "Not urgent but misleading for reporting.",
        ],
        "gold"      : {"label": "bug", "severity": "P2"},
    },

    {
        "issue_id"  : "MED-005",
        "difficulty": "medium",
        "task_type" : "severity",
        "title"     : "Database credentials exposed in error logs",
        "body"      : (
            "When a DB connection fails, the full connection string\n"
            "including username and password is printed to the logs.\n"
            "These logs are accessible to all engineers with log access.\n"
            "This is a security vulnerability that must be fixed immediately."
        ),
        "comments"  : [
            "Discovered during internal security audit.",
            "Logs are currently accessible to 40+ engineers.",
        ],
        "gold"      : {"label": "bug", "severity": "P0"},
    },

    # ══════════════════════════════════════════════════════════════════
    # HARD — Label + Severity + Module (5 tasks)
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

    {
        "issue_id"  : "HARD-004",
        "difficulty": "hard",
        "task_type" : "locate",
        "title"     : "Password reset emails are sent to wrong address after email change",
        "body"      : (
            "When a user changes their email and then requests a password reset,\n"
            "the reset link is sent to the OLD email address, not the new one.\n"
            "This locks users out of their accounts permanently.\n"
            "Reported by 5 users in the last week."
        ),
        "comments"  : [
            "Users who changed email recently are most affected.",
            "The new email is saved correctly in the DB.",
            "Issue seems to be in how the reset flow fetches the email.",
        ],
        "context"   : {
            "repo_structure": [
                "auth/password_reset.py",
                "auth/email_change.py",
                "auth/login.py",
                "users/profile.py",
                "users/settings.py",
                "notifications/email_sender.py",
                "notifications/templates.py",
                "db/models.py",
                "db/user_repository.py",
            ],
            "description": (
                "auth/password_reset.py handles the reset flow. "
                "notifications/email_sender.py sends all emails. "
                "db/user_repository.py fetches user data from the database."
            ),
        },
        "gold"      : {
            "label"   : "bug",
            "severity": "P1",
            "modules" : ["auth/password_reset.py", "db/user_repository.py"],
        },
    },

    {
        "issue_id"  : "HARD-005",
        "difficulty": "hard",
        "task_type" : "locate",
        "title"     : "API rate limiter blocks legitimate users after burst traffic",
        "body"      : (
            "Our rate limiter uses a fixed window counter.\n"
            "Users who make 100 requests at 11:59 PM and 100 at 12:00 AM\n"
            "are blocked even though they are within the hourly limit.\n"
            "This is the classic fixed-window boundary bug.\n"
            "Legitimate power users are being blocked daily."
        ),
        "comments"  : [
            "Sliding window algorithm would fix this.",
            "Affects ~200 API customers per day.",
            "Support tickets have tripled this week.",
        ],
        "context"   : {
            "repo_structure": [
                "api/rate_limiter.py",
                "api/middleware.py",
                "api/routes.py",
                "cache/redis_client.py",
                "cache/window_counter.py",
                "auth/token_validator.py",
                "db/models.py",
                "config/settings.py",
            ],
            "description": (
                "api/rate_limiter.py implements the rate limiting logic. "
                "cache/window_counter.py manages the counter storage in Redis. "
                "api/middleware.py applies rate limiting on every request."
            ),
        },
        "gold"      : {
            "label"   : "bug",
            "severity": "P1",
            "modules" : ["api/rate_limiter.py", "cache/window_counter.py"],
        },
    },
]