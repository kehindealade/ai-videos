import argparse
import datetime
import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_FILE = os.path.join(ROOT, "claude", "yt-stats", "fb_tokens.json")
GRAPH = "https://graph.facebook.com/v21.0"


def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    return json.load(open(TOKENS_FILE))


def save_tokens(data):
    os.makedirs(os.path.dirname(TOKENS_FILE), exist_ok=True)
    json.dump(data, open(TOKENS_FILE, "w"), indent=2)


def graph_get(path, params):
    url = f"{GRAPH}/{path.lstrip('/')}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")


def graph_post(path, params):
    url = f"{GRAPH}/{path.lstrip('/')}"
    req = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode("utf-8"), method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")


def to_unix_ts(ts_str):
    dt = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
    return int(dt.timestamp())


def cmd_save(args):
    res = graph_get(args.page_id, {"fields": "id,name", "access_token": args.token})
    data = load_tokens()
    data[args.label] = {"page_id": str(res["id"]), "name": res.get("name", ""), "access_token": args.token}
    save_tokens(data)
    print(f"saved {args.label}: {res.get('name')} ({res['id']})")


def upload_thumb(video_id, thumb_path, token):
    boundary = "----fb_thumb_boundary_4c81e2"
    mime = mimetypes.guess_type(thumb_path)[0] or "image/png"
    fname = os.path.basename(thumb_path)
    img = open(thumb_path, "rb").read()
    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"access_token\"\r\n\r\n{token}\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"is_preferred\"\r\n\r\ntrue\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"source\"; filename=\"{fname}\"\r\nContent-Type: {mime}\r\n\r\n".encode()
        + img
        + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    body = b"".join(parts)
    req = urllib.request.Request(
        f"{GRAPH}/{video_id}/thumbnails",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"thumb_warn=HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")
        return None


def cmd_schedule(args):
    data = load_tokens()
    if args.label not in data:
        raise SystemExit(f"Unknown label '{args.label}'. Run 'save' first.")
    page_id = data[args.label]["page_id"]
    token = data[args.label]["access_token"]
    caption = open(args.caption_file).read().strip() if args.caption_file else (args.caption or "")

    # Step 1: start upload session
    start = graph_post(f"{page_id}/video_reels", {
        "upload_phase": "start",
        "access_token": token,
    })
    video_id = start["video_id"]
    upload_url = start["upload_url"]

    # Step 2: upload raw mp4 bytes to rupload.facebook.com
    video_bytes = open(args.video, "rb").read()
    up_req = urllib.request.Request(
        upload_url,
        data=video_bytes,
        method="POST",
        headers={
            "Authorization": f"OAuth {token}",
            "offset": "0",
            "file_size": str(len(video_bytes)),
            "Content-Type": "application/octet-stream",
        },
    )
    try:
        with urllib.request.urlopen(up_req) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Upload failed HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")

    # Step 3: finish and schedule / draft / publish
    finish_params = {
        "upload_phase": "finish",
        "video_id": video_id,
        "description": caption,
        "access_token": token,
    }
    if args.publish_at:
        finish_params["video_state"] = "SCHEDULED"
        finish_params["scheduled_publish_time"] = str(to_unix_ts(args.publish_at))
    else:
        finish_params["video_state"] = args.state

    fin = graph_post(f"{page_id}/video_reels", finish_params)
    print(f"reel video_id={video_id} state={finish_params['video_state']} response={json.dumps(fin)}")

    if args.thumb:
        t_res = upload_thumb(video_id, args.thumb, token)
        if t_res:
            print("thumbnail=uploaded")

    if args.comment_file and finish_params["video_state"] == "PUBLISHED":
        msg = open(args.comment_file).read().strip()
        c_res = graph_post(f"{video_id}/comments", {"message": msg, "access_token": token})
        print(f"comment_id={c_res.get('id')}")


def cmd_comment(args):
    data = load_tokens()
    token = data[args.label]["access_token"]
    msg = open(args.comment_file).read().strip() if args.comment_file else args.message
    res = graph_post(f"{args.video_id}/comments", {"message": msg, "access_token": token})
    print(f"comment_id={res.get('id')}")


def cmd_status(args):
    data = load_tokens()
    token = data[args.label]["access_token"]
    res = graph_get(args.video_id, {"fields": "id,status,permalink_url", "access_token": token})
    print(json.dumps(res, indent=2))


def main():
    p = argparse.ArgumentParser(description="Facebook Page Reels uploader and scheduler (Meta Graph API v21.0)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sv = sub.add_parser("save")
    sv.add_argument("label", help="e.g. smallwin or moneymap")
    sv.add_argument("page_id")
    sv.add_argument("token")

    sc = sub.add_parser("schedule")
    sc.add_argument("label")
    sc.add_argument("--video", required=True)
    sc.add_argument("--caption")
    sc.add_argument("--caption-file")
    sc.add_argument("--publish-at", help="ISO time, e.g. 2026-12-15T23:00:00+01:00 (10 min to 29 days ahead)")
    sc.add_argument("--state", default="DRAFT", choices=["DRAFT", "PUBLISHED"])
    sc.add_argument("--thumb")
    sc.add_argument("--comment-file")

    cm = sub.add_parser("comment")
    cm.add_argument("label")
    cm.add_argument("video_id")
    cm.add_argument("--message")
    cm.add_argument("--comment-file")

    st = sub.add_parser("status")
    st.add_argument("label")
    st.add_argument("video_id")

    args = p.parse_args()
    if args.cmd == "save":
        cmd_save(args)
    elif args.cmd == "schedule":
        cmd_schedule(args)
    elif args.cmd == "comment":
        cmd_comment(args)
    elif args.cmd == "status":
        cmd_status(args)


if __name__ == "__main__":
    main()
