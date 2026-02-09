"""
Telegram Public OSINT Tool
Brand    : Dark Tech Zone
Telegram : https://t.me/DarkTechZone
Purpose  : Educational & Research Use Only
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import json

BASE_URL = "https://t.me/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DarkTechZone-OSINT/1.0)"
}

BRANDING = {
    "brand": "Dark Tech Zone",
    "telegram_channel": "https://t.me/DarkTechZone",
    "tool": "Telegram Public OSINT",
    "scope": "Public data only",
    "note": "No authentication. No private access."
}

def normalize_members(text):
    if not text:
        return None

    text = text.lower().replace(",", "").strip()
    match = re.search(r"([\d\.]+)\s*([km]?)", text)
    if not match:
        return None

    value = float(match.group(1))
    suffix = match.group(2)

    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000

    return int(value)

def detect_profile_type(html):
    if "tgme_channel_info" in html:
        return "channel"
    if "tgme_group_info" in html:
        return "group"
    if "tgme_page_title" in html:
        return "user"
    return "unknown"

def scrape(username):
    url = BASE_URL + username

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except requests.RequestException:
        return {"error": "request failed"}

    if r.status_code != 200:
        return {"error": "username not accessible or not public"}

    if "og:site_name" not in r.text:
        return {"error": "blocked or invalid response"}

    soup = BeautifulSoup(r.text, "html.parser")
    profile_type = detect_profile_type(r.text)

    title = soup.find("div", class_="tgme_page_title")
    bio = soup.find("div", class_="tgme_page_description")
    photo = soup.find("img", class_="tgme_page_photo_image")
    extra = soup.find("div", class_="tgme_page_extra")

    members_raw = extra.text if extra else None

    return {
        "username": f"@{username}",
        "profile_type": profile_type,
        "name": title.text.strip() if title else None,
        "bio": bio.text.strip() if bio else None,
        "has_photo": bool(photo),
        "photo_url": photo["src"] if photo else None,
        "verified": "tgme_icon_verified" in r.text,
        "members_raw": members_raw,
        "members_count": normalize_members(members_raw),
        "public_url": url,
        "scraped_at": int(time.time())
    }

def handler(event, context):
    query = event.get("queryStringParameters") or {}
    username = query.get("username")

    if not username:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "success": False,
                "error": "username parameter required",
                "branding": BRANDING
            })
        }

    data = scrape(username.strip().lstrip("@"))

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "success": "error" not in data,
            "branding": BRANDING,
            "result": data
        }, ensure_ascii=False)
    }
