import os
import requests
from datetime import datetime, timedelta, timezone

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_API_URL = "https://api.twitch.tv/helix"

def _headers(token: str) -> dict:
    return {
        "Client-ID": os.environ["TWITCH_CLIENT_ID"],
        "Authorization": f"Bearer {token}",
    }

def get_app_token(client_id: str, client_secret: str) -> str:
    r = requests.post(
        TWITCH_TOKEN_URL,
        params={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]

def get_game_id(game_name: str, token: str) -> str:
    r = requests.get(
        f"{TWITCH_API_URL}/games",
        headers=_headers(token),
        params={"name": game_name},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json().get("data", [])
    if not data:
        raise RuntimeError(f"Game not found on Twitch: {game_name}")
    return data[0]["id"]

def _fetch_users(user_ids: list[str], token: str) -> dict:
    # Bulk fetch /users?id=...&id=...
    params = [("id", uid) for uid in user_ids]
    r = requests.get(
        f"{TWITCH_API_URL}/users",
        headers=_headers(token),
        params=params,
        timeout=30,
    )
    r.raise_for_status()
    users = r.json().get("data", [])
    return {u["id"]: u for u in users}

def get_top_clip_for_game(
    game_id: str,
    token: str,
    lookback_hours: int = 24,
    partner_only: bool = True,
    fetch_first: int = 50,
) -> dict:
    started_at = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()

    r = requests.get(
        f"{TWITCH_API_URL}/clips",
        headers=_headers(token),
        params={
            "game_id": game_id,
            "first": min(max(fetch_first, 1), 100),
            "started_at": started_at,
        },
        timeout=30,
    )
    r.raise_for_status()
    clips = r.json().get("data", [])
    if not clips:
        raise RuntimeError("No clips returned for this window.")

    if partner_only:
        broadcaster_ids = list({c["broadcaster_id"] for c in clips if c.get("broadcaster_id")})
        users = _fetch_users(broadcaster_ids, token)

        filtered = []
        for c in clips:
            u = users.get(c.get("broadcaster_id", ""))
            if not u:
                continue
            if u.get("broadcaster_type") == "partner":
                c["_broadcaster_type"] = u.get("broadcaster_type")
                filtered.append(c)

        if not filtered:
            raise RuntimeError("No partner clips found in this time window.")
        clips = filtered

    clips.sort(key=lambda c: c.get("view_count", 0), reverse=True)
    top = clips[0]

    return {
        "id": top.get("id"),
        "url": top.get("url"),
        "title": (top.get("title") or "").strip(),
        "views": top.get("view_count", 0),
        "broadcaster_name": top.get("broadcaster_name"),
        "created_at": top.get("created_at"),
    }
