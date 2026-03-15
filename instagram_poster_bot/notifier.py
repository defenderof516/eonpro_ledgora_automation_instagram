"""
Discord webhook notifications for the Instagram Poster Bot.
Sends start/end/error embeds. Silently fails if webhook URL is not set.
"""

import requests
from datetime import datetime, timezone, timedelta

from config import DISCORD_WEBHOOK_URL

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


def send_discord_notification(embed: dict):
    """POST a Discord embed to the webhook URL. Silently fails on any error."""
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(
            DISCORD_WEBHOOK_URL,
            json={"embeds": [embed]},
            timeout=10,
        )
    except Exception:
        pass


def notify_start(run_time: datetime, stats: dict, selected_posters: list):
    """Send a notification when the bot starts a run."""
    ist_time = run_time.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S IST")
    cycle = stats.get("current_cycle", 1)
    posted = stats.get("posted_this_cycle", 0)
    total = stats.get("total_posters", 0)

    poster_lines = "\n".join(f"   → {name}" for name, _ in selected_posters)

    description = (
        f"🕐 Started: {ist_time}\n"
        f"📊 Cycle: {cycle} | Posted: {posted}/{total}\n"
        f"🎯 Today's posts: {len(selected_posters)}\n"
        f"{poster_lines}"
    )

    send_discord_notification({
        "title": "📸 Ledgora Bot Started",
        "description": description,
        "color": 0x2ECC71,  # green
    })


def notify_end(run_time: datetime, results: list, stats: dict):
    """Send a notification when the bot finishes a run."""
    success = sum(1 for r in results if r["status"] == "success")
    total = len(results)
    all_ok = success == total

    result_lines = "\n".join(
        f"   {'✅' if r['status'] == 'success' else '❌'} {r['filename']}"
        for r in results
    )

    duration = (datetime.now(timezone.utc) - run_time).total_seconds()
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    dur_str = f"{hours}h {minutes}m" if hours else f"{minutes}m"

    total_ever = stats.get("total_posts_ever", 0)
    cycle = stats.get("current_cycle", 1)

    description = (
        f"{'✅' if all_ok else '❌'} Success: {success}/{total}\n"
        f"{result_lines}\n"
        f"⏱️ Duration: {dur_str}\n"
        f"📊 Total posts ever: {total_ever} | Cycle: {cycle}"
    )

    send_discord_notification({
        "title": f"{'✅' if all_ok else '❌'} Ledgora Bot Completed",
        "description": description,
        "color": 0x2ECC71 if all_ok else 0xE74C3C,
    })


def notify_error(run_time: datetime, error_message: str):
    """Send a notification when the bot encounters a fatal error."""
    ist_time = datetime.now(timezone.utc).astimezone(IST).strftime("%Y-%m-%d %H:%M:%S IST")

    description = (
        f"{error_message}\n"
        f"🕐 Time: {ist_time}"
    )

    send_discord_notification({
        "title": "❌ Ledgora Bot Error",
        "description": description,
        "color": 0xE74C3C,  # red
    })
