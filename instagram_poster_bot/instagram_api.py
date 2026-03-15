"""
Instagram Graph API integration for publishing posts.
Handles image upload and post creation via the Instagram Graph API.
"""

import time
import requests
from config import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_ACCOUNT_ID,
    GRAPH_API_BASE,
    IMGBB_API_KEY,
)
import base64


def upload_image_to_imgbb(image_path: str) -> str:
    """
    Upload an image to ImgBB (free image hosting) and return the public URL.
    Instagram Graph API requires a publicly accessible image URL.

    Args:
        image_path: Local path to the image file

    Returns:
        Public URL of the uploaded image
    """
    print(f"📤 Uploading image to ImgBB: {image_path}")

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": image_data,
        "expiration": 86400,  # 24 hours (we only need it temporarily)
    }

    response = requests.post(url, data=payload, timeout=120)
    response.raise_for_status()
    result = response.json()

    if result.get("success"):
        image_url = result["data"]["url"]
        print(f"✅ Image uploaded: {image_url}")
        return image_url
    else:
        raise Exception(f"ImgBB upload failed: {result}")


def upload_image_via_github_raw(image_path: str, repo_owner: str, repo_name: str, github_token: str) -> str:
    """
    Alternative: Upload image to GitHub repo and use raw URL.
    This is a fallback if ImgBB is not configured.

    Args:
        image_path: Local path to the image file
        repo_owner: GitHub repo owner
        repo_name: GitHub repo name
        github_token: GitHub token for authentication

    Returns:
        Raw GitHub URL for the image
    """
    import os
    filename = os.path.basename(image_path)
    upload_path = f"temp_uploads/{filename}"

    with open(image_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{upload_path}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Check if file already exists (get SHA for update)
    existing = requests.get(url, headers=headers, timeout=30)
    payload = {
        "message": f"Upload poster: {filename}",
        "content": content,
        "branch": "main",
    }
    if existing.status_code == 200:
        payload["sha"] = existing.json()["sha"]

    response = requests.put(url, json=payload, headers=headers, timeout=120)
    response.raise_for_status()

    # Use raw.githubusercontent.com URL
    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{upload_path}"
    print(f"✅ Image uploaded to GitHub: {raw_url}")
    return raw_url


def create_instagram_media_container(image_url: str, caption: str) -> str:
    """
    Step 1 of Instagram publishing: Create a media container.

    Args:
        image_url: Publicly accessible URL of the image
        caption: Post caption text

    Returns:
        Creation ID (container ID)
    """
    print("📦 Creating Instagram media container...")

    url = f"{GRAPH_API_BASE}/{INSTAGRAM_ACCOUNT_ID}/media"
    params = {
        "image_url": image_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }

    response = requests.post(url, data=params, timeout=60)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Graph API Error Data: {e.response.text}")
        raise e
    result = response.json()

    container_id = result.get("id")
    if not container_id:
        raise Exception(f"Failed to create media container: {result}")

    print(f"✅ Media container created: {container_id}")
    return container_id


def check_container_status(container_id: str) -> str:
    """
    Check if the media container is ready for publishing.

    Args:
        container_id: The media container ID

    Returns:
        Status string: 'FINISHED', 'IN_PROGRESS', 'ERROR'
    """
    url = f"{GRAPH_API_BASE}/{container_id}"
    params = {
        "fields": "status_code,status",
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    result = response.json()
    return result.get("status_code", "UNKNOWN")


def publish_media(container_id: str) -> str:
    """
    Step 2 of Instagram publishing: Publish the media container.

    Args:
        container_id: The media container ID from step 1

    Returns:
        Published media ID
    """
    print("🚀 Publishing to Instagram...")

    # Wait for container to be ready (max 60 seconds)
    for attempt in range(12):
        status = check_container_status(container_id)
        if status == "FINISHED":
            break
        elif status == "ERROR":
            raise Exception(f"Media container error. Status: {status}")
        print(f"⏳ Container status: {status}. Waiting... (attempt {attempt + 1}/12)")
        time.sleep(5)

    url = f"{GRAPH_API_BASE}/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    params = {
        "creation_id": container_id,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }

    response = requests.post(url, data=params, timeout=60)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Graph API Error Data: {e.response.text}")
        raise e
    result = response.json()

    media_id = result.get("id")
    if not media_id:
        raise Exception(f"Failed to publish media: {result}")

    print(f"✅ Published! Media ID: {media_id}")
    return media_id


def post_to_instagram(image_path: str, caption: str) -> str:
    """
    Full flow: Upload image → Create container → Publish.

    Args:
        image_path: Local path to the poster image
        caption: Generated caption text

    Returns:
        Published media ID
    """
    from config import GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_TOKEN

    # Step 1: Upload image to get a public URL
    if IMGBB_API_KEY:
        image_url = upload_image_to_imgbb(image_path)
    elif GITHUB_REPO_OWNER and GITHUB_REPO_NAME and GITHUB_TOKEN:
        image_url = upload_image_via_github_raw(
            image_path, GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_TOKEN
        )
    else:
        raise Exception(
            "No image hosting configured! Set IMGBB_API_KEY or GitHub repo details."
        )

    # Step 2: Create media container
    container_id = create_instagram_media_container(image_url, caption)

    # Step 3: Publish
    media_id = publish_media(container_id)

    return media_id


def verify_token() -> bool:
    """Verify that the Instagram access token is valid."""
    url = f"{GRAPH_API_BASE}/me"
    params = {
        "fields": "id,name",
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Token valid. Account: {result.get('name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return False


def refresh_long_lived_token() -> str:
    """
    Refresh the long-lived access token.
    Long-lived tokens are valid for 60 days and can be refreshed
    when they have at least 24 hours left.

    Returns:
        New access token
    """
    url = f"{GRAPH_API_BASE}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": "",  # Will need FB App ID
        "client_secret": "",  # Will need FB App Secret
        "fb_exchange_token": INSTAGRAM_ACCESS_TOKEN,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    result = response.json()

    new_token = result.get("access_token")
    if new_token:
        print(f"✅ Token refreshed successfully")
        return new_token
    else:
        raise Exception(f"Token refresh failed: {result}")
