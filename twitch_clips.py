import os
import requests
from collections import defaultdict
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
        raise RuntimeError(f"Game not found: {game_name}")
    return data[0]["id"]

def _fetch_users(ids: list[str], token: str) -> dict:
    if not ids:
        return {}
    r = requests.get(
        f"{TWITCH_API_URL}/users",
        headers=_headers(token),
        params=[("id", i) for i in ids],
        timeout=30,
    )
    r.raise_for_status()
    return {u["id"]: u for u in r.json().get("data", [])}

def _fetch_channels(ids: list[str], token: str) -> dict:
    if not ids:
        return {}
    r = requests.get(
        f"{TWITCH_API_URL}/channels",
        headers=_headers(token),
        params=[("broadcaster_id", i) for i in ids],
        timeout=30,
    )
    r.raise_for_status()
    return {c["broadcaster_id"]: c for c in r.json().get("data", [])}

def get_top_clip_for_game(
    game_id: str,
    token: str,
    lookback_hours: int = 168,
    fetch_first: int = 100,
    partner_only: bool = True,
    english_only: bool = True,
    min_clips_per_creator: int = 2,
    creator_clip_bonus: float = 0.35,
) -> dict:
    """
    Selects a trending creator by requiring multiple high-performing clips.
    """

    started_at = (
        datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    ).isoformat()

    r = requests.get(
        f"{TWITCH_API_URL}/clips",
        headers=_headers(token),
        params={
            "game_id": game_id,
            "first": min(fetch_first, 100),
            "started_at": started_at,
        },
        timeout=30,
    )
    r.raise_for_status()
    clips = r.json().get("data", [])
    if not clips:
        raise RuntimeError("No clips returned")

    broadcaster_ids = list({c["broadcaster_id"] for c in clips})
    users = _fetch_users(broadcaster_ids, token)

    if partner_only:
        partners = {
            uid for uid, u in users.items()
            if u.get("broadcaster_type") == "partner"
        }
        clips = [c for c in clips if c["broadcaster_id"] in partners]

    if english_only:
        channels = _fetch_channels(broadcaster_ids, token)
        clips = [
            c for c in clips
            if channels.get(c["broadcaster_id"], {}).get("broadcaster_language") == "en"
        ]

    grouped = defaultdict(list)
    for c in clips:
        grouped[c["broadcaster_id"]].append(c)

    scored = []
    for bid, arr in grouped.items():
        if len(arr) < min_clips_per_creator:
            continue
        total_views = sum(int(x["view_count"]) for x in arr)
        score = total_views * (1 + creator_clip_bonus * (len(arr) - 1))
        scored.append((score, bid))

    if not scored:
        clips.sort(key=lambda c: int(c["view_count"]), reverse=True)
        top = clips[0]
    else:
        scored.sort(reverse=True)
        best_bid = scored[0][1]
        arr = grouped[best_bid]
        arr.sort(key=lambda c: int(c["view_count"]), reverse=True)
        top = arr[0]

    return {
        "id": top["id"],
        "url": top["url"],
        "title": top.get("title", "").strip(),
        "views": top["view_count"],
        "broadcaster_name": top["broadcaster_name"],
    }
