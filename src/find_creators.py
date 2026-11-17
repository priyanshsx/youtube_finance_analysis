import os
import re
import statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_KEY = os.environ.get("YOUTUBE_API_KEY")
if not API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY is not set. Add it to your .env file.")
youtube = build("youtube", "v3", developerKey=API_KEY)

# What Cypherock's buyers search for. Each query runs once per region below.
QUERIES = [
    "hardware wallet review",
    "best hardware wallet",
    "crypto self custody",
    "seed phrase backup",
    "bitcoin cold storage",
    "crypto inheritance",
    "ledger vs trezor",
    "how to store bitcoin safely",
    "shamir backup crypto",
    "move crypto off exchange",
]

# Target markets: US, Canada, UK, Germany. (regionCode, relevanceLanguage)
REGIONS = [("US", "en"), ("CA", "en"), ("GB", "en"), ("DE", "de")]

# Creators you already have in the sheet: always included and scored, even if search misses them.
SEED_HANDLES = [
    "@CoinBureau", "@BTCSessions", "@CryptoCasey", "@AltcoinDaily", "@CryptosRUs",
    "@NatalieBrunell", "@AndreiJikh", "@TheCryptoLark", "@IvanOnTech", "@Blocktrainer",
    "@JulianHosp", "@Hasheur", "@CryptoWendyO",
]

SEARCH_LAST_DAYS = 365      # only videos from the last year count as "active on this topic"
MIN_HITS = 2                # a channel must appear in at least this many searches
MIN_SUBS = 10_000           # below this, reach is too small to matter
MAX_SUBS = 3_000_000        # above this, usually too expensive for a first campaign
VIDEOS_TO_ANALYSE = 30
TARGET_COUNTRIES = {"US", "CA", "GB", "DE", "AT", "CH", "FR", "NL", "IE", "SE", "ES", "IT"}

RELEVANCE_TERMS = re.compile(
    r"hardware wallet|cold (?:storage|wallet)|self[- ]?custody|seed phrase|recovery phrase|"
    r"private key|multisig|shamir|not your keys|wallet security|inheritance|"
    r"ledger|trezor|cypherock|tangem|coldcard|bitbox|keystone",
    re.I,
)
SPONSOR_TERMS = re.compile(r"sponsor|#ad\b|paid promotion|affiliate|promo code|discount code|use code", re.I)

# Competitor links in descriptions. Affiliate-style links (with a referral code) are the real conflict.
COMPETITORS = {
    "Ledger": re.compile(r"ledger\.com|shop\.ledger", re.I),
    "Trezor": re.compile(r"trezor\.io|affil\.trezor", re.I),
    "Tangem": re.compile(r"tangem\.com", re.I),
    "Coldcard": re.compile(r"coldcard\.com|coinkite\.com", re.I),
    "BitBox": re.compile(r"bitbox\.swiss|shiftcrypto", re.I),
    "Keystone": re.compile(r"keyst\.one|keystone", re.I),
    "Casa": re.compile(r"keys\.casa", re.I),
}
AFFILIATE_HINT = re.compile(r"[?&](?:r|ref|referral|offer_id|aff|affiliate|code)=|/ref/|affil\.", re.I)


# ---------------- step 1: discovery ----------------

def discover_channels():
    hits = defaultdict(set)  # channel_id -> set of "query | region"
    published_after = (datetime.now(timezone.utc) - timedelta(days=SEARCH_LAST_DAYS)).isoformat()
    for query in QUERIES:
        for region, lang in REGIONS:
            resp = youtube.search().list(
                part="snippet", q=query, type="video", maxResults=50,
                regionCode=region, relevanceLanguage=lang,
                publishedAfter=published_after, order="relevance",
            ).execute()
            for item in resp.get("items", []):
                hits[item["snippet"]["channelId"]].add(f"{query} | {region}")
            print(f"searched: {query!r} in {region} ({len(resp.get('items', []))} videos)")
    return hits


def resolve_handles(handles):
    ids = {}
    for handle in handles:
        resp = youtube.channels().list(part="id", forHandle=handle).execute()
        if resp.get("items"):
            ids[resp["items"][0]["id"]] = handle
        else:
            print(f"handle not found: {handle}")
    return ids


# ---------------- step 2: measurement ----------------

def get_channels(channel_ids):
    """Channel stats in batches of 50 (1 unit per batch)."""
    out = {}
    ids = list(channel_ids)
    for i in range(0, len(ids), 50):
        resp = youtube.channels().list(
            part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])
        ).execute()
        for c in resp.get("items", []):
            stats = c.get("statistics", {})
            out[c["id"]] = {
                "name": c["snippet"]["title"],
                "handle": c["snippet"].get("customUrl", ""),
                "country": c["snippet"].get("country", ""),
                "subscribers": int(stats["subscriberCount"]) if not stats.get("hiddenSubscriberCount") else None,
                "uploads": c["contentDetails"]["relatedPlaylists"]["uploads"],
            }
    return out


def get_recent_videos(uploads_playlist, n=VIDEOS_TO_ANALYSE):
    ids = []
    resp = youtube.playlistItems().list(
        part="contentDetails", playlistId=uploads_playlist, maxResults=min(50, n)
    ).execute()
    ids = [i["contentDetails"]["videoId"] for i in resp.get("items", [])][:n]
    if not ids:
        return []
    resp = youtube.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids)).execute()
    videos = []
    for v in resp.get("items", []):
        if v["snippet"].get("liveBroadcastContent") in ("live", "upcoming"):
            continue
        s = v.get("statistics", {})
        videos.append({
            "id": v["id"],
            "title": v["snippet"]["title"],
            "description": v["snippet"].get("description", ""),
            "published": datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00")),
            "duration": parse_duration(v["contentDetails"].get("duration", "PT0S")),
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0)),
        })
    return sorted(videos, key=lambda x: x["published"], reverse=True)


def parse_duration(iso):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m:
        return 0
    d, h, mi, s = (int(g) if g else 0 for g in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


# ---------------- step 3: scoring ----------------

def analyse(channel, videos):
    long_form = [v for v in videos if v["duration"] > 180] or videos  # Shorts distort view counts
    now = datetime.now(timezone.utc)
    views = [v["views"] for v in long_form]
    subs = channel["subscribers"]

    relevant = [v for v in videos if RELEVANCE_TERMS.search(v["title"] + " " + v["description"])]
    sponsored = [v for v in videos if SPONSOR_TERMS.search(v["description"])]

    conflicts, conflict_examples = set(), []
    for v in videos:
        for brand, pattern in COMPETITORS.items():
            for line in v["description"].splitlines():
                if pattern.search(line) and AFFILIATE_HINT.search(line):
                    if brand not in conflicts:
                        conflict_examples.append(f"{brand}: youtube.com/watch?v={v['id']}")
                    conflicts.add(brand)

    span_days = max((videos[0]["published"] - videos[-1]["published"]).days, 1) if len(videos) > 1 else None
    return {
        "avg_views_last_10": round(statistics.mean(views[:10])) if views else None,
        "median_views_last_30": round(statistics.median(views)) if views else None,
        "views_per_sub": round(statistics.median(views) / subs, 4) if views and subs else None,
        "engagement_rate": round(statistics.median(
            [(v["likes"] + v["comments"]) / v["views"] for v in long_form if v["views"]]), 4) if long_form else None,
        "uploads_per_week": round(len(videos) / span_days * 7, 1) if span_days else None,
        "days_since_last_upload": (now - videos[0]["published"]).days if videos else None,
        "relevance_share": round(len(relevant) / len(videos), 2) if videos else 0,
        "sponsored_share": round(len(sponsored) / len(videos), 2) if videos else 0,
        "mentions_cypherock": any("cypherock" in (v["title"] + v["description"]).lower() for v in videos),
        "competitor_affiliate_links": ", ".join(sorted(conflicts)),
        "conflict_examples": " | ".join(conflict_examples),
    }


def pct_rank(series):
    return series.rank(pct=True).fillna(0)


def main():
    hits = discover_channels()
    seeds = resolve_handles(SEED_HANDLES)

    candidates = {cid for cid, h in hits.items() if len(h) >= MIN_HITS} | set(seeds)
    print(f"\n{len(hits)} channels found; {len(candidates)} candidates after the hit filter (plus seeds)")

    channels = get_channels(candidates)
    rows = []
    for cid, ch in channels.items():
        is_seed = cid in seeds
        if not is_seed and (ch["subscribers"] is None or not MIN_SUBS <= ch["subscribers"] <= MAX_SUBS):
            continue
        videos = get_recent_videos(ch["uploads"])
        if not videos:
            continue
        m = analyse(ch, videos)
        rows.append({
            "name": ch["name"],
            "youtube_url": f"https://www.youtube.com/{ch['handle']}" if ch["handle"] else f"https://www.youtube.com/channel/{cid}",
            "country": ch["country"] or "not listed",
            "subscribers": ch["subscribers"],
            **m,
            "search_hits": len(hits.get(cid, ())),
            "found_by": "; ".join(sorted(hits.get(cid, ())))[:300],
            "in_original_list": is_seed,
        })
        print(f"measured: {ch['name']}")

    df = pd.DataFrame(rows)

    # Fit score (0-100). Weights are deliberate and easy to explain:
    #   35% engagement (views per subscriber), 30% topic relevance,
    #   15% consistency (uploads per week), 10% search visibility, 10% target geography.
    #   Inactive channels (no upload in 60 days) are halved. Competitor affiliate links are flagged, not hidden.
    df["geo_fit"] = df["country"].isin(TARGET_COUNTRIES).astype(float)
    df["fit_score"] = (
        35 * pct_rank(df["views_per_sub"])
        + 30 * df["relevance_share"].clip(upper=0.5) / 0.5
        + 15 * pct_rank(df["uploads_per_week"])
        + 10 * pct_rank(df["search_hits"])
        + 10 * df["geo_fit"]
    ).round(1)
    df.loc[df["days_since_last_upload"] > 60, "fit_score"] = (df["fit_score"] / 2).round(1)

    df = df.sort_values("fit_score", ascending=False)
    df.to_csv("creators_ranked.csv", index=False)
    print(f"\nSaved {len(df)} creators to creators_ranked.csv")
    print(df[["name", "country", "subscribers", "views_per_sub", "relevance_share",
              "competitor_affiliate_links", "fit_score"]].head(25).to_string(index=False))


if __name__ == "__main__":
    main()