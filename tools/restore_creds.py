import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YT_DIR = os.path.join(ROOT, "claude", "yt-stats")
TOKENS_DIR = os.path.join(YT_DIR, "tokens")
SECRET_NAME = "ai-videos-secrets.json"


def find_file_id():
    r = subprocess.run(
        ["gdrive", "readonly", "search", "--name-contains", SECRET_NAME, "--json"],
        capture_output=True, text=True, check=True,
    )
    out = r.stdout.strip()
    if not out:
        return None
    d = json.loads(out)
    items = d.get("files", d) if isinstance(d, dict) else d
    for it in items:
        if it.get("name") == SECRET_NAME and not it.get("trashed"):
            return it["id"]
    return None


def restore():
    fid = find_file_id()
    if not fid:
        raise SystemExit(f"{SECRET_NAME} not found in Google Drive.")
    tmp = "/tmp/ai-videos-secrets.json"
    subprocess.run(["gdrive", "readonly", "download", fid, "--out", tmp], check=True)
    bundle = json.load(open(tmp))
    os.remove(tmp)

    os.makedirs(TOKENS_DIR, exist_ok=True)
    if "client" in bundle:
        json.dump(bundle["client"], open(os.path.join(YT_DIR, "client.json"), "w"), indent=2)
    for name, tok in bundle.get("yt_tokens", {}).items():
        json.dump(tok, open(os.path.join(TOKENS_DIR, f"{name}.json"), "w"))
    if "fb_tokens" in bundle:
        json.dump(bundle["fb_tokens"], open(os.path.join(YT_DIR, "fb_tokens.json"), "w"), indent=2)
    print(f"restored client.json, {len(bundle.get('yt_tokens', {}))} YouTube tokens, fb_tokens.json")


def save():
    bundle = {}
    cp = os.path.join(YT_DIR, "client.json")
    if os.path.exists(cp):
        bundle["client"] = json.load(open(cp))
    yt_toks = {}
    if os.path.isdir(TOKENS_DIR):
        for fn in sorted(os.listdir(TOKENS_DIR)):
            if fn.endswith(".json"):
                yt_toks[fn[:-5]] = json.load(open(os.path.join(TOKENS_DIR, fn)))
    bundle["yt_tokens"] = yt_toks
    fbp = os.path.join(YT_DIR, "fb_tokens.json")
    if os.path.exists(fbp):
        bundle["fb_tokens"] = json.load(open(fbp))

    tmp = "/tmp/ai-videos-secrets.json"
    json.dump(bundle, open(tmp, "w"), indent=2)
    fid = find_file_id()
    if fid:
        subprocess.run(["gdrive", "mutate", "update", fid, tmp], check=True)
        print(f"updated {SECRET_NAME} ({fid})")
    else:
        subprocess.run(["gdrive", "mutate", "upload", tmp], check=True)
        fid = find_file_id()
        print(f"uploaded {SECRET_NAME} ({fid})")
    os.remove(tmp)
    perms = subprocess.run(["gdrive", "readonly", "permissions", fid], capture_output=True, text=True)
    print(perms.stdout.strip())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "save":
        save()
    else:
        restore()
