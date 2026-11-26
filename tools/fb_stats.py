import argparse
import csv
import json
import os
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_FILE = os.path.join(ROOT, "claude", "yt-stats", "fb_tokens.json")
OUT_DIR = os.path.join(ROOT, "claude", "yt-stats", "out", "facebook")
GRAPH = "https://graph.facebook.com/v21.0"

REEL_METRICS = ",".join([
    "fb_reels_total_plays",
    "blue_reels_play_count",
    "fb_reels_replay_count",
    "post_video_avg_time_watched",
    "post_video_view_time",
    "post_video_followers",
])

PAGE_METRICS = ",".join([
    "page_media_view",
    "page_total_media_view_unique",
    "page_follows",
    "page_post_engagements",
    "page_video_views",
    "page_views_total",
])


def load_tokens():
    return json.load(open(TOKENS_FILE)) if os.path.exists(TOKENS_FILE) else {}


def graph_get(path, params):
    url = f"{GRAPH}/{path.lstrip('/')}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode("utf-8", "replace")}


def cmd_exchange(args):
    """Exchange a short-lived User token + App ID/Secret into never-expiring Page tokens."""
    ll = graph_get("oauth/access_token", {
        "grant_type": "fb_exchange_token",
        "client_id": args.app_id,
        "client_secret": args.app_secret,
        "fb_exchange_token": args.user_token,
    })
    if "access_token" not in ll:
        raise SystemExit(f"Exchange failed: {ll}")
    long_user = ll["access_token"]
    data = load_tokens()
    for lbl, pid in (("moneymap", "532721356778356"), ("smallwin", "398717443559378")):
        res = graph_get(pid, {"fields": "id,name,access_token", "access_token": long_user})
        if "access_token" in res:
            data[lbl] = {"page_id": str(res["id"]), "name": res.get("name", lbl), "access_token": res["access_token"]}
            print(f"permanent token saved: {lbl} ({res.get('name')})")
        else:
            print(f"warn {lbl}: {res}")
    os.makedirs(os.path.dirname(TOKENS_FILE), exist_ok=True)
    json.dump(data, open(TOKENS_FILE, "w"), indent=2)


def cmd_report(args):
    tokens = load_tokens()
    labels = [args.label] if args.label else list(tokens.keys())
    os.makedirs(OUT_DIR, exist_ok=True)

    for lbl in labels:
        info = tokens[lbl]
        pid, tok, name = info["page_id"], info["access_token"], info.get("name", lbl)
        print(f"\n=== Facebook {lbl}: {name} ({pid}) ===")

        pg = graph_get(f"{pid}/insights", {"metric": PAGE_METRICS, "period": "days_28", "access_token": tok})
        if "error" in pg:
            print("  page insights error:", pg["error"][:200])
        else:
            for m in pg.get("data", []):
                vals = m.get("values", [])
                val = vals[-1]["value"] if vals else None
                print(f"  {m['name']}: {val}")

        reels = graph_get(f"{pid}/video_reels", {
            "fields": "id,description,created_time,published,length",
            "limit": str(args.limit),
            "access_token": tok,
        })
        if "error" in reels:
            print("  reels error:", reels["error"][:200])
            continue

        rows = [[
            "video_id", "created_time", "length_s", "plays", "initial_plays",
            "replays", "avg_watch_ms", "total_watch_ms", "new_followers", "caption",
        ]]
        for r in reels.get("data", []):
            ins = graph_get(f"{r['id']}/video_insights", {"metric": REEL_METRICS, "access_token": tok})
            vals = {}
            for m in ins.get("data", []):
                if m.get("values"):
                    vals[m["name"]] = m["values"][0]["value"]
            cap = (r.get("description") or "").replace("\n", " ")[:70]
            rows.append([
                r["id"], r.get("created_time", ""), r.get("length", ""),
                vals.get("fb_reels_total_plays", ""), vals.get("blue_reels_play_count", ""),
                vals.get("fb_reels_replay_count", ""), vals.get("post_video_avg_time_watched", ""),
                vals.get("post_video_view_time", ""), vals.get("post_video_followers", ""), cap,
            ])
            print(f"  {r.get('created_time','')[:10]} | plays={vals.get('fb_reels_total_plays','?')} replays={vals.get('fb_reels_replay_count','?')} avg_ms={vals.get('post_video_avg_time_watched','?')} | {cap}")

        out_csv = os.path.join(OUT_DIR, f"{lbl}_reels.csv")
        with open(out_csv, "w", newline="") as f:
            csv.writer(f).writerows(rows)
        print("  saved:", out_csv)


def main():
    p = argparse.ArgumentParser(description="Facebook Page & Reels analytics via Meta Graph API")
    sub = p.add_subparsers(dest="cmd", required=True)

    rp = sub.add_parser("report")
    rp.add_argument("label", nargs="?", help="smallwin or moneymap (default: both)")
    rp.add_argument("--limit", type=int, default=25)

    ex = sub.add_parser("exchange", help="Convert User token + App ID/Secret into permanent Page tokens")
    ex.add_argument("app_id")
    ex.add_argument("app_secret")
    ex.add_argument("user_token")

    args = p.parse_args()
    if args.cmd == "report":
        cmd_report(args)
    elif args.cmd == "exchange":
        cmd_exchange(args)


if __name__ == "__main__":
    main()
