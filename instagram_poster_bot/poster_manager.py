"""
Poster Manager - Handles poster selection, tracking, and rotation.
Ensures no poster is repeated until all have been posted.
"""

import os
import json
import random
from datetime import datetime, timezone
from config import POSTERS_DIR, POSTED_LOG_FILE


# Supported image formats
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def get_all_posters() -> list:
    """
    Get all poster image files from the posters directory.

    Returns:
        List of poster filenames
    """
    if not os.path.exists(POSTERS_DIR):
        print(f"❌ Posters directory not found: {POSTERS_DIR}")
        return []

    posters = []
    for f in os.listdir(POSTERS_DIR):
        ext = os.path.splitext(f)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            posters.append(f)

    posters.sort()
    print(f"📂 Found {len(posters)} posters in {POSTERS_DIR}")
    return posters


def load_posted_log() -> dict:
    """
    Load the posting history log.

    Returns:
        Dict with 'posted' list and metadata
    """
    if os.path.exists(POSTED_LOG_FILE):
        try:
            with open(POSTED_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "posted": [],
        "history": [],
        "last_run": None,
        "total_posts": 0,
        "cycle": 1,
    }


def save_posted_log(log: dict):
    """Save the posting history log."""
    with open(POSTED_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"💾 Posted log saved ({len(log.get('posted', []))} posters marked as used)")


def select_posters_for_today() -> list:
    """
    Select random posters for today's posting session.
    - Randomly picks 2 or 4 posters
    - Avoids repeats within a cycle
    - Resets cycle when all posters have been used

    Returns:
        List of (filename, full_path) tuples for selected posters
    """
    all_posters = get_all_posters()
    if not all_posters:
        print("❌ No posters available!")
        return []

    log = load_posted_log()
    posted = set(log.get("posted", []))

    # Find unposted posters
    available = [p for p in all_posters if p not in posted]

    # If all have been posted, reset the cycle
    if not available:
        print("🔄 All posters have been used! Starting new cycle...")
        log["cycle"] = log.get("cycle", 1) + 1
        log["posted"] = []
        available = all_posters.copy()

    # Randomly decide: 2 or 4 posts today (humanized)
    num_posts = random.choice([2, 2, 2, 4, 4, 3])  # Weighted: 2 is more common
    num_posts = min(num_posts, len(available))  # Don't exceed available

    print(f"🎲 Today's post count: {num_posts}")

    # Select random posters
    selected_filenames = random.sample(available, num_posts)

    # Shuffle the order for variety
    random.shuffle(selected_filenames)

    # Build full paths
    selected = [
        (filename, os.path.join(POSTERS_DIR, filename))
        for filename in selected_filenames
    ]

    print(f"🎯 Selected posters:")
    for fname, _ in selected:
        print(f"   → {fname}")

    return selected


def mark_as_posted(filename: str, media_id: str = None, caption: str = None):
    """
    Mark a poster as posted in the log.

    Args:
        filename: Poster filename
        media_id: Instagram media ID (if successfully posted)
        caption: Caption used (for reference)
    """
    log = load_posted_log()

    # Add to posted list
    if filename not in log.get("posted", []):
        log["posted"].append(filename)

    # Add to history with timestamp
    log["history"].append({
        "filename": filename,
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "media_id": media_id,
        "caption_preview": (caption[:100] + "...") if caption and len(caption) > 100 else caption,
        "cycle": log.get("cycle", 1),
    })

    log["total_posts"] = log.get("total_posts", 0) + 1
    log["last_run"] = datetime.now(timezone.utc).isoformat()

    save_posted_log(log)


def get_posting_stats() -> dict:
    """Get posting statistics."""
    log = load_posted_log()
    all_posters = get_all_posters()

    posted_count = len(log.get("posted", []))
    total_posters = len(all_posters)
    remaining = total_posters - posted_count

    return {
        "total_posters": total_posters,
        "posted_this_cycle": posted_count,
        "remaining": remaining,
        "total_posts_ever": log.get("total_posts", 0),
        "current_cycle": log.get("cycle", 1),
        "last_run": log.get("last_run"),
    }


if __name__ == "__main__":
    # Test poster selection
    print("\n📊 Poster Stats:")
    stats = get_posting_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n🎯 Test Selection:")
    selected = select_posters_for_today()
    for fname, fpath in selected:
        print(f"   {fname} → exists: {os.path.exists(fpath)}")
