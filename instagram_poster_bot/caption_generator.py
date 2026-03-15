"""
AI Caption Generator using Google Gemini (Free Tier).
Generates engaging, humanized Instagram captions for Ledgora app posters.
"""

import random
from google import genai
from config import GEMINI_API_KEY, APP_CONTEXT, BASE_HASHTAGS


def initialize_gemini():
    """Initialize the Gemini AI model client."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    return client


def extract_poster_theme(filename: str) -> str:
    """
    Extract the theme/topic from the poster filename.
    e.g., 'p01_cash_in_cash_out.png' → 'cash in cash out'
          'poster03_analytics_insights.png' → 'analytics insights'
    """
    name = filename.rsplit(".", 1)[0]  # Remove extension

    # Remove prefix like p01_, poster03_, scene1_
    parts = name.split("_", 1)
    if len(parts) > 1:
        # Check if first part is a prefix (p01, poster03, scene1, etc.)
        first = parts[0].lower()
        if any(first.startswith(prefix) for prefix in ["p", "poster", "scene"]):
            name = parts[1]
        else:
            name = name

    # Replace underscores with spaces
    theme = name.replace("_", " ").strip()
    return theme


def get_random_hashtags(count: int = 15) -> str:
    """Select random hashtags from the base set for variety."""
    selected = random.sample(BASE_HASHTAGS, min(count, len(BASE_HASHTAGS)))
    return " ".join(selected)


def generate_caption(poster_filename: str, style: str = None) -> str:
    """
    Generate an engaging Instagram caption for a Ledgora poster.

    Args:
        poster_filename: Name of the poster image file
        style: Optional caption style override

    Returns:
        Generated caption with hashtags
    """
    client = initialize_gemini()
    theme = extract_poster_theme(poster_filename)

    # Randomly pick a caption style for humanization
    styles = [
        "casual and friendly, like talking to a friend",
        "professional yet approachable, like a tech founder",
        "inspirational and motivational about financial freedom",
        "educational, teaching about money management",
        "story-telling, sharing a relatable financial scenario",
        "question-based, engaging the audience with a thought-provoking question",
        "tip-based, sharing a quick money tip related to the feature",
        "humorous and witty, making finance fun",
    ]

    chosen_style = style or random.choice(styles)

    # Randomly vary caption length
    length_options = [
        "Keep it short and punchy (2-3 sentences max)",
        "Medium length (3-5 sentences with a call to action)",
        "Slightly longer storytelling style (4-6 sentences)",
    ]
    chosen_length = random.choice(length_options)

    prompt = f"""You are a social media manager for Ledgora, a personal finance/ledger mobile app.
Generate an Instagram caption for a poster about: "{theme}"

App Context:
{APP_CONTEXT}

Style: {chosen_style}
Length: {chosen_length}

RULES:
1. DO NOT use any markdown formatting (no *, **, #, etc.)
2. Use emojis naturally but don't overdo it (2-5 emojis max)
3. Include a call-to-action (download, try, check out, etc.)
4. Make it feel authentic and human - NOT like an AI wrote it
5. Vary sentence structure - don't start every sentence the same way
6. Sometimes use line breaks for readability
7. Reference the specific feature/theme shown in the poster
8. End with something engaging (question, CTA, or inspirational note)
9. Do NOT include hashtags - they will be added separately
10. Do NOT mention "poster" or "image" - write as if you're sharing a thought/tip
11. The app download link is: https://play.google.com/store/apps/details?id=com.eonpro.ledgora
12. Sometimes mention the link, sometimes don't - keep it natural

Return ONLY the caption text, nothing else.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        caption = response.text.strip()

        # Add hashtags
        hashtags = get_random_hashtags(random.randint(10, 18))
        full_caption = f"{caption}\n\n.\n.\n.\n{hashtags}"

        return full_caption

    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        # Fallback captions if AI fails
        return generate_fallback_caption(theme)


def generate_fallback_caption(theme: str) -> str:
    """Generate a fallback caption if AI is unavailable."""
    fallback_templates = [
        f"💰 Managing your money just got easier! Check out {theme} in Ledgora.\n\nTrack every rupee, analyze your spending, and take control of your finances - all offline!\n\nDownload now 👇\nhttps://play.google.com/store/apps/details?id=com.eonpro.ledgora",
        f"📊 Your finances deserve better than scattered notes. {theme.title()} makes it simple.\n\nLedgora - Your personal ledger, always with you.\n\nTry it free! Link in bio 🔗",
        f"🎯 Smart money management starts here. Discover {theme} with Ledgora.\n\nNo internet needed. No account required. Just pure simplicity.\n\nDownload Ledgora today! ⬇️\nhttps://play.google.com/store/apps/details?id=com.eonpro.ledgora",
        f"✨ Did you know? Ledgora's {theme} feature helps you stay on top of your finances effortlessly.\n\nYour money. Your control. Your privacy.\n\nGet it now 👉 Link in bio",
        f"🚀 Take charge of your financial journey! {theme.title()} is just one of the many ways Ledgora helps you.\n\nOffline-first. Privacy-focused. Beautiful design.\n\nFree download on Play Store! 📱",
    ]

    caption = random.choice(fallback_templates)
    hashtags = get_random_hashtags(random.randint(10, 15))
    return f"{caption}\n\n.\n.\n.\n{hashtags}"


if __name__ == "__main__":
    # Test caption generation
    test_files = [
        "p01_cash_in_cash_out.png",
        "poster03_analytics_insights.png",
        "p19_morning_routine.png",
    ]
    for f in test_files:
        print(f"\n{'='*60}")
        print(f"Poster: {f}")
        print(f"Theme: {extract_poster_theme(f)}")
        print(f"{'='*60}")
        caption = generate_caption(f)
        print(caption)
