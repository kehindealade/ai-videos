import argparse
import datetime
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YT_DIR = os.path.join(ROOT, "claude", "yt-stats")
CLIENT = os.path.join(YT_DIR, "client.json")
TOKENS = os.path.join(YT_DIR, "tokens")
REDIRECT = "http://localhost"
SCOPES = " ".join([
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
])


def load_client():
    d = json.load(open(CLIENT))
    d = d.get("installed") or d.get("web") or d
    return d["client_id"], d["client_secret"]


def post_form(url, data):
    req = urllib.request.Request(url, urllib.parse.urlencode(data).encode())
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def auth_url():
    cid, _ = load_client()
    q = dict(
        client_id=cid,
        redirect_uri=REDIRECT,
        response_type="code",
        scope=SCOPES,
        access_type="offline",
        prompt="consent",
    )
    print("https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(q))


def exchange(label, pasted):
    code = pasted
    if "code=" in pasted:
        code = urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query)["code"][0]
    cid, sec = load_client()
    t = post_form(
        "https://oauth2.googleapis.com/token",
        dict(
            code=code,
            client_id=cid,
            client_secret=sec,
            redirect_uri=REDIRECT,
            grant_type="authorization_code",
        ),
    )
    os.makedirs(TOKENS, exist_ok=True)
    tok_path = os.path.join(TOKENS, f"{label}_upload.json")
    json.dump({"refresh_token": t["refresh_token"]}, open(tok_path, "w"))
    req = urllib.request.Request(
        "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
        headers={"Authorization": "Bearer " + t["access_token"]},
    )
    with urllib.request.urlopen(req) as resp:
        ch = json.load(resp)
    titles = [i["snippet"]["title"] for i in ch.get("items", [])]
    print("saved", f"{label}_upload", titles)


def access_token(label):
    cid, sec = load_client()
    tok_path = os.path.join(TOKENS, f"{label}_upload.json")
    rt = json.load(open(tok_path))["refresh_token"]
    return post_form(
        "https://oauth2.googleapis.com/token",
        dict(
            refresh_token=rt,
            client_id=cid,
            client_secret=sec,
            grant_type="refresh_token",
        ),
    )["access_token"]


def to_utc_iso(ts_str):
    dt = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def api_err(e):
    body = e.read().decode("utf-8", "replace")
    raise SystemExit(f"HTTP {e.code}: {body}")


def upload_video(args):
    tok = access_token(args.label)
    desc = open(args.desc_file).read().strip() if args.desc_file else (args.desc or "")
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]

    status = {
        "privacyStatus": "private" if args.publish_at else args.privacy,
        "selfDeclaredMadeForKids": False,
    }
    if args.publish_at:
        status["publishAt"] = to_utc_iso(args.publish_at)

    body = {
        "snippet": {
            "title": args.title,
            "description": desc,
            "tags": tags,
            "categoryId": str(args.category),
            "defaultLanguage": args.lang,
            "defaultAudioLanguage": args.lang,
        },
        "status": status,
    }

    video_size = os.path.getsize(args.video)
    meta_bytes = json.dumps(body).encode("utf-8")
    init_req = urllib.request.Request(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        data=meta_bytes,
        method="POST",
        headers={
            "Authorization": "Bearer " + tok,
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(video_size),
            "X-Upload-Content-Type": "video/mp4",
        },
    )
    try:
        with urllib.request.urlopen(init_req) as resp:
            upload_url = resp.headers["Location"]
    except urllib.error.HTTPError as e:
        api_err(e)

    # Stream upload in 8 MB chunks
    chunk_size = 8 * 1024 * 1024
    video_id = None
    with open(args.video, "rb") as f:
        offset = 0
        while offset < video_size:
            chunk = f.read(chunk_size)
            end = offset + len(chunk) - 1
            put_req = urllib.request.Request(
                upload_url,
                data=chunk,
                method="PUT",
                headers={
                    "Authorization": "Bearer " + tok,
                    "Content-Type": "video/mp4",
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {offset}-{end}/{video_size}",
                },
            )
            try:
                with urllib.request.urlopen(put_req) as resp:
                    res = json.load(resp)
                    video_id = res["id"]
            except urllib.error.HTTPError as e:
                if e.code == 308:
                    offset = end + 1
                    continue
                api_err(e)
            offset = end + 1

    print(f"uploaded video_id={video_id}")
    print(f"studio_url=https://studio.youtube.com/video/{video_id}/edit")
    if args.publish_at:
        print(f"scheduled_utc={status['publishAt']}")

    if args.thumb:
        mime = mimetypes.guess_type(args.thumb)[0] or "image/png"
        t_bytes = open(args.thumb, "rb").read()
        t_req = urllib.request.Request(
            f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}&uploadType=media",
            data=t_bytes,
            method="POST",
            headers={
                "Authorization": "Bearer " + tok,
                "Content-Type": mime,
                "Content-Length": str(len(t_bytes)),
            },
        )
        try:
            with urllib.request.urlopen(t_req) as resp:
                resp.read()
            print("thumbnail=set")
        except urllib.error.HTTPError as e:
            print(f"thumbnail_warn=HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")

    if args.srt:
        boundary = "----yt_srt_boundary_7f9a2c"
        meta = json.dumps({
            "snippet": {
                "videoId": video_id,
                "language": args.lang.split("-")[0],
                "name": "English",
                "isDraft": False,
            }
        }).encode("utf-8")
        srt_bytes = open(args.srt, "rb").read()
        payload = (
            f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode()
            + meta
            + f"\r\n--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n".encode()
            + srt_bytes
            + f"\r\n--{boundary}--\r\n".encode()
        )
        c_req = urllib.request.Request(
            "https://www.googleapis.com/upload/youtube/v3/captions?part=snippet&uploadType=multipart",
            data=payload,
            method="POST",
            headers={
                "Authorization": "Bearer " + tok,
                "Content-Type": f"multipart/related; boundary={boundary}",
                "Content-Length": str(len(payload)),
            },
        )
        try:
            with urllib.request.urlopen(c_req) as resp:
                resp.read()
            print("captions=uploaded")
        except urllib.error.HTTPError as e:
            print(f"captions_warn=HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")


def main():
    p = argparse.ArgumentParser(description="YouTube Data API v3 uploader and scheduler")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth-url")
    ex = sub.add_parser("exchange")
    ex.add_argument("label")
    ex.add_argument("pasted")
    up = sub.add_parser("upload")
    up.add_argument("label")
    up.add_argument("--video", required=True)
    up.add_argument("--title", required=True)
    up.add_argument("--desc")
    up.add_argument("--desc-file")
    up.add_argument("--tags", default="")
    up.add_argument("--category", default="1", help="1=Film & Animation, 27=Education")
    up.add_argument("--privacy", default="unlisted", choices=["private", "unlisted", "public"])
    up.add_argument("--publish-at", help="ISO time, e.g. 2026-12-15T23:00:00+01:00")
    up.add_argument("--thumb")
    up.add_argument("--srt")
    up.add_argument("--lang", default="en-US")
    args = p.parse_args()
    if args.cmd == "auth-url":
        auth_url()
    elif args.cmd == "exchange":
        exchange(args.label, args.pasted)
    elif args.cmd == "upload":
        upload_video(args)


if __name__ == "__main__":
    main()
