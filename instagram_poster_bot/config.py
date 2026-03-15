"""
Configuration for the Instagram Poster Bot.
All sensitive values are loaded from environment variables (GitHub Secrets).
"""

import os

# ─── Instagram Graph API ──────────────────────────────────────────
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# ─── Gemini AI (Free Tier) ────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"  # Free tier model

# ─── Posting Configuration ────────────────────────────────────────
MIN_POSTS_PER_DAY = 2
MAX_POSTS_PER_DAY = 4
MIN_DELAY_BETWEEN_POSTS_SECONDS = 1800   # 30 minutes minimum
MAX_DELAY_BETWEEN_POSTS_SECONDS = 5400   # 90 minutes maximum

# ─── Paths ────────────────────────────────────────────────────────
POSTERS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Eonpro_Ledgora_Posters")
POSTED_LOG_FILE = os.path.join(os.path.dirname(__file__), "posted_log.json")

# ─── Instagram Hashtags ──────────────────────────────────────────
BASE_HASHTAGS = [
    "#Ledgora", "#MoneyTracker", "#PersonalFinance", "#BudgetApp",
    "#ExpenseTracker", "#FinanceApp", "#MoneyManagement", "#Budgeting",
    "#SaveMoney", "#FinancialFreedom", "#MoneyGoals", "#SmartMoney",
    "#FinanceTracker", "#CashFlow", "#MobileApp", "#AndroidApp",
    "#ProductivityApp", "#OfflineApp", "#FinanceTips", "#MoneyMatters",
    "#LedgoraApp", "#TrackYourMoney", "#DigitalLedger", "#FinancePlanning",
    "#AppOfTheDay", "#TechStartup", "#IndianStartup", "#MadeInIndia",
    "#FinTech", "#SmartFinance"
]

# ─── Ledgora App Context for Caption Generation ──────────────────
APP_CONTEXT = """
Ledgora is an offline-first personal ledger app that helps users:
- Track income and expenses instantly
- Organize transactions by categories
- Monitor balance and cash flow in real-time
- Generate professional PDF reports
- Analyze spending patterns with beautiful charts
- Set payment reminders with notifications
- Securely backup & restore data to Google Drive (premium)
- Personalize with 3 premium themes
- Search transactions instantly
- Share transactions as designed screenshots

Key selling points:
- Works 100% offline - no internet needed
- No account required - complete privacy
- One-time premium purchase (no subscription!)
- Modern, smooth, beautiful UI
- Lightning fast transaction entry (2 taps)
- Smart analytics with weekly/monthly trends
- Professional PDF reports
- Google Drive backup (premium)

Available on Google Play Store.
Download link: https://play.google.com/store/apps/details?id=com.eonpro.ledgora
"""

# ─── Image Hosting (using GitHub raw content as free image host) ──
# We'll upload images to a public hosting service or use the repo itself
GITHUB_REPO_OWNER = os.environ.get("GITHUB_REPO_OWNER", "")
GITHUB_REPO_NAME = os.environ.get("GITHUB_REPO_NAME", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # Auto-provided by GitHub Actions

# ─── Image Upload Service ────────────────────────────────────────
# Using imgbb.com free tier (or fallback to GitHub raw content)
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")
