import os
import requests
from datetime import datetime, timedelta, timezone

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_API_URL = "https://api.twitch.tv/helix"

def _headers(token):
    return {
        "Client-ID": os.environ["TWITCH_CLIENT_ID"],
        "Authorization": f"Bearer {token}",
    }

def get_app_token(client_id, client_secret):
    r = requests.post(
        TWITCH_TOKEN_URL,
        params={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
    )
    r.raise_for_status()
    return r.json()["access_token"]

def get_game_id(game_name, token):
    r = requests.get(
        f"{TWITCH_API_URL}/games",
        headers=_headers(token),
        params={"name": game_name},
    )
    r.raise_for_status()
    return r.json()["data"][0]["id"]

def get_top_clip_for_game(game_id, token, lookback_hours=24, partner_only=True):
    started_at = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()

    r = requests.get(
        f"{TWITCH_API_URL}/clips",
        headers=_headers(token),
        params={"game_id": game_id, "first": 50, "started_at": started_at},
    )
    r.raise_for_status()
    clips = r.json()["data"]

    if partner_only:
        broadcaster_ids = list({c["broadcaster_id"] for c in clips})
        users = requests.get(
            f"{TWITCH_API_URL}/users",
            headers=_headers(token),
            params=[("id", uid) for uid in broadcaster_ids],
        ).json()["data"]

        partners = {u["id"] for u in users if u["broadcaster_type"] == "partner"}
        clips = [c for c in clips if c["broadcaster_id"] in partners]

    clips.sort(key=lambda c: c["view_count"], reverse=True)
    top = clips[0]

    return {
        "url": top["url"],
        "title": top["title"],
        "views": top["view_count"],
        "broadcaster": top["broadcaster_name"],
    }
