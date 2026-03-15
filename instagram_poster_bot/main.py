"""
Main Bot Script - Orchestrates the daily Instagram posting workflow.
This is the entry point called by GitHub Actions.
"""

import os
import sys
import time
import random
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from config import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_ACCOUNT_ID,
    GEMINI_API_KEY,
    IMGBB_API_KEY,
    MIN_DELAY_BETWEEN_POSTS_SECONDS,
    MAX_DELAY_BETWEEN_POSTS_SECONDS,
)
from poster_manager import select_posters_for_today, mark_as_posted, get_posting_stats
from caption_generator import generate_caption
from instagram_api import post_to_instagram, verify_token


def print_banner():
    """Print a nice banner for the bot."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   📸 Ledgora Instagram Poster Bot                        ║
║   ────────────────────────────────                        ║
║   Automated daily poster publishing with AI captions      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)


def validate_config():
    """Validate that all required configuration is present."""
    errors = []

    if not INSTAGRAM_ACCESS_TOKEN:
        errors.append("INSTAGRAM_ACCESS_TOKEN is not set")
    if not INSTAGRAM_ACCOUNT_ID:
        errors.append("INSTAGRAM_ACCOUNT_ID is not set")
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY is not set")
    if not IMGBB_API_KEY:
        errors.append("IMGBB_API_KEY is not set (needed for image hosting)")

    if errors:
        print("❌ Configuration errors:")
        for err in errors:
            print(f"   → {err}")
        return False

    print("✅ All required configuration is present")
    return True


def humanized_delay(post_number: int, total_posts: int):
    """
    Add a humanized random delay between posts.
    Makes the posting pattern look more natural.

    Args:
        post_number: Current post number (0-indexed)
        total_posts: Total posts planned for today
    """
    if post_number >= total_posts - 1:
        return  # No delay after last post

    # Random delay between min and max
    base_delay = random.randint(
        MIN_DELAY_BETWEEN_POSTS_SECONDS,
        MAX_DELAY_BETWEEN_POSTS_SECONDS,
    )

    # Add some jitter (+/- 5 minutes)
    jitter = random.randint(-300, 300)
    delay = max(60, base_delay + jitter)  # At least 1 minute

    next_time = datetime.now(timezone.utc).timestamp() + delay
    next_dt = datetime.fromtimestamp(next_time, tz=timezone.utc)

    print(f"\n⏰ Waiting {delay // 60} minutes {delay % 60} seconds before next post...")
    print(f"   Next post at: {next_dt.strftime('%H:%M:%S UTC')}")

    # Sleep with progress updates every 5 minutes
    elapsed = 0
    while elapsed < delay:
        chunk = min(300, delay - elapsed)  # 5-minute chunks
        time.sleep(chunk)
        elapsed += chunk
        remaining = delay - elapsed
        if remaining > 0:
            print(f"   ⏳ {remaining // 60}m {remaining % 60}s remaining...")


def run_daily_posting():
    """
    Main daily posting workflow:
    1. Validate configuration
    2. Verify Instagram token
    3. Select random posters
    4. Generate AI captions
    5. Post with humanized delays
    6. Report results
    """
    print_banner()
    run_time = datetime.now(timezone.utc)
    print(f"🕐 Run started at: {run_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Step 1: Validate
    if not validate_config():
        print("\n❌ Bot cannot run without proper configuration. Exiting.")
        sys.exit(1)

    # Step 2: Verify token
    print("\n🔐 Verifying Instagram access token...")
    if not verify_token():
        print("❌ Instagram token is invalid or expired!")
        print("   Please update the INSTAGRAM_ACCESS_TOKEN secret.")
        sys.exit(1)

    # Step 3: Show stats
    print("\n📊 Current Posting Stats:")
    stats = get_posting_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Step 4: Select posters
    print("\n🎯 Selecting posters for today...")
    selected = select_posters_for_today()

    if not selected:
        print("❌ No posters available to post!")
        sys.exit(1)

    # Step 5: Post each poster with delays
    results = []
    total = len(selected)

    for i, (filename, filepath) in enumerate(selected):
        print(f"\n{'='*60}")
        print(f"📮 Post {i + 1}/{total}: {filename}")
        print(f"{'='*60}")

        try:
            # Generate AI caption
            print("🤖 Generating AI caption...")
            caption = generate_caption(filename)
            print(f"📝 Caption preview: {caption[:150]}...")

            # Post to Instagram
            print(f"\n📸 Posting to Instagram...")
            media_id = post_to_instagram(filepath, caption)

            # Mark as posted
            mark_as_posted(filename, media_id=media_id, caption=caption)

            results.append({
                "filename": filename,
                "status": "success",
                "media_id": media_id,
            })
            print(f"✅ Successfully posted: {filename}")

        except Exception as e:
            print(f"❌ Failed to post {filename}: {e}")
            results.append({
                "filename": filename,
                "status": "failed",
                "error": str(e),
            })

        # Humanized delay between posts
        humanized_delay(i, total)

    # Step 6: Report results
    print(f"\n{'='*60}")
    print("📋 DAILY POSTING REPORT")
    print(f"{'='*60}")

    success_count = sum(1 for r in results if r["status"] == "success")
    fail_count = sum(1 for r in results if r["status"] == "failed")

    print(f"✅ Success: {success_count}/{total}")
    print(f"❌ Failed:  {fail_count}/{total}")

    for r in results:
        status_icon = "✅" if r["status"] == "success" else "❌"
        print(f"   {status_icon} {r['filename']} → {r.get('media_id', r.get('error', 'unknown'))}")

    # Updated stats
    print(f"\n📊 Updated Stats:")
    stats = get_posting_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    duration = (datetime.now(timezone.utc) - run_time).total_seconds()
    print(f"\n⏱️ Total run duration: {duration // 60:.0f}m {duration % 60:.0f}s")
    print(f"🏁 Bot run completed at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    if fail_count > 0:
        sys.exit(1)  # Signal failure to GitHub Actions


if __name__ == "__main__":
    run_daily_posting()
