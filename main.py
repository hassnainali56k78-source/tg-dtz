"""
Telegram OSINT Public Tool
Powered by Dark Tech Zone
Educational Purpose Only
"""

import requests
from bs4 import BeautifulSoup
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ================= CONFIG =================
BASE_URL = "https://t.me/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

BRAND = "Dark Tech Zone"
TELEGRAM = "https://t.me/DarkTechZone"

# ================= HELPERS =================
def detect_profile_type(html):
    if "tgme_channel_info" in html:
        return "📢 Channel"
    elif "tgme_group_info" in html:
        return "👥 Group"
    else:
        return "👤 User"

def scrape_members(soup, profile_type):
    if profile_type in ["📢 Channel", "👥 Group"]:
        counter = soup.find("div", class_="tgme_page_extra")
        if counter:
            return counter.text.strip()
    return "Not Public"

def scrape_telegram(username):
    url = BASE_URL + username

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except requests.RequestException:
        return {"error": "Request failed"}

    if r.status_code != 200:
        return {"error": "Invalid or private username"}

    soup = BeautifulSoup(r.text, "html.parser")
    profile_type = detect_profile_type(r.text)

    title = soup.find("div", class_="tgme_page_title")
    bio = soup.find("div", class_="tgme_page_description")
    photo = soup.find("img", class_="tgme_page_photo_image")

    return {
        "📛 Name": title.text.strip() if title else f"@{username}",
        "📝 Bio": bio.text.strip() if bio else "Not available",
        "🖼️ Profile Photo": "Yes" if photo else "No",
        "🖼️ Photo URL": photo["src"] if photo else None,
        "✅ Verified": "Yes" if "tgme_icon_verified" in r.text else "No",
        "💎 Premium": "Unknown",
        "📌 Profile Type": profile_type,
        "👥 Members": scrape_members(soup, profile_type),
        "🌐 Public Link": url,
        "✉️ Direct Chat": f"tg://resolve?domain={username}",
        "👁️ Public Username": "Yes"
    }

def analysis_block(profile_type):
    return {
        "📊 Profile Visibility": "Public",
        "🧠 Data Reliability": (
            "High" if profile_type in ["📢 Channel", "👥 Group"]
            else "Limited (Privacy)"
        )
    }

# ================= API ROUTES =================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "tool": "Telegram OSINT Public Tool",
        "brand": BRAND,
        "telegram": TELEGRAM,
        "usage": "/telegram?username=example",
        "status": "online"
    })

@app.route("/telegram", methods=["GET"])
def telegram_api():
    username = request.args.get("username")

    if not username:
        return jsonify({"error": "Missing ?username parameter"}), 400

    start = time.time()
    base = scrape_telegram(username)

    if "error" in base:
        return jsonify(base), 400

    return jsonify({
        "success": True,
        "🔎 Username": f"@{username}",
        "🏷️ Brand": BRAND,
        "🕒 Timestamp": int(time.time()),
        "📂 Profile": base,
        "🧠 Analysis": analysis_block(base["📌 Profile Type"]),
        "⚡ Processing Time": f"{round(time.time() - start, 2)}s"
    })

# ================= START =================
if __name__ == "__main__":
    app.run()
