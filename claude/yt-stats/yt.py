import json, os, sys, urllib.parse, urllib.request, datetime, csv

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.join(HERE, "client.json")
TOKENS = os.path.join(HERE, "tokens")
OUT = os.path.join(HERE, "out")
REDIRECT = "http://localhost"
SCOPES = "https://www.googleapis.com/auth/yt-analytics.readonly https://www.googleapis.com/auth/youtube.readonly"


def unpack():
    b = os.path.join(HERE, "credentials.json")
    if not os.path.exists(b):
        b = os.path.join(HERE, "yt-signin.txt")
    if os.path.exists(b) and not os.path.exists(CLIENT):
        d = json.load(open(b))
        json.dump(d["client"], open(CLIENT, "w"))
        os.makedirs(TOKENS, exist_ok=True)
        for k, v in d["tokens"].items():
            json.dump(v, open(os.path.join(TOKENS, k + ".json"), "w"))


def client():
    unpack()
    d = json.load(open(CLIENT))
    d = d.get("installed") or d.get("web") or d
    return d["client_id"], d["client_secret"]


def post(url, data):
    req = urllib.request.Request(url, urllib.parse.urlencode(data).encode())
    return json.load(urllib.request.urlopen(req))


def get(url, params, tok):
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers={"Authorization": "Bearer " + tok})
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read().decode() or "{}")}


def auth_url():
    cid, _ = client()
    q = dict(client_id=cid, redirect_uri=REDIRECT, response_type="code", scope=SCOPES, access_type="offline", prompt="consent")
    print("https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(q))


def exchange(label, pasted):
    code = pasted
    if "code=" in pasted:
        code = urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query)["code"][0]
    cid, sec = client()
    t = post("https://oauth2.googleapis.com/token", dict(code=code, client_id=cid, client_secret=sec, redirect_uri=REDIRECT, grant_type="authorization_code"))
    os.makedirs(TOKENS, exist_ok=True)
    json.dump({"refresh_token": t["refresh_token"]}, open(os.path.join(TOKENS, label + ".json"), "w"))
    tok = t["access_token"]
    ch = get("https://www.googleapis.com/youtube/v3/channels", dict(part="snippet", mine="true"), tok)
    print("saved", label, [i["snippet"]["title"] for i in ch.get("items", [])])


def access(label):
    cid, sec = client()
    rt = json.load(open(os.path.join(TOKENS, label + ".json")))["refresh_token"]
    return post("https://oauth2.googleapis.com/token", dict(refresh_token=rt, client_id=cid, client_secret=sec, grant_type="refresh_token"))["access_token"]


def analytics(tok, **p):
    p.setdefault("ids", "channel==MINE")
    return get("https://youtubeanalytics.googleapis.com/v2/reports", p, tok)


def table(r):
    if "error" in r:
        return [["error", json.dumps(r["error"])[:300]]]
    return [[h["name"] for h in r.get("columnHeaders", [])]] + r.get("rows", [])


def save(path, rows):
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)


def report(label, start=None, end=None):
    tok = access(label)
    end = end or datetime.date.today().isoformat()
    start = start or (datetime.date.today() - datetime.timedelta(days=28)).isoformat()
    d = os.path.join(OUT, label)
    os.makedirs(d, exist_ok=True)
    ch = get("https://www.googleapis.com/youtube/v3/channels", dict(part="snippet,statistics,contentDetails", mine="true"), tok)
    item = ch["items"][0]
    up = item["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = get("https://www.googleapis.com/youtube/v3/playlistItems", dict(part="contentDetails", playlistId=up, maxResults=50), tok)
    ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
    vids = get("https://www.googleapis.com/youtube/v3/videos", dict(part="snippet,statistics,contentDetails,status", id=",".join(ids)), tok) if ids else {"items": []}
    rows = [["videoId", "title", "published", "duration", "privacy", "views", "likes", "comments"]]
    for v in vids["items"]:
        rows.append([v["id"], v["snippet"]["title"], v["snippet"]["publishedAt"], v["contentDetails"]["duration"], v["status"]["privacyStatus"],
                     v["statistics"].get("viewCount"), v["statistics"].get("likeCount"), v["statistics"].get("commentCount")])
    save(os.path.join(d, "videos.csv"), rows)
    base = dict(startDate=start, endDate=end)
    m = "views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments,shares"
    save(os.path.join(d, "per_video.csv"), table(analytics(tok, metrics=m, dimensions="video", sort="-views", maxResults=50, **base)))
    save(os.path.join(d, "daily.csv"), table(analytics(tok, metrics="views,engagedViews,estimatedMinutesWatched,subscribersGained", dimensions="day", sort="day", **base)))
    save(os.path.join(d, "traffic.csv"), table(analytics(tok, metrics="views,estimatedMinutesWatched,averageViewDuration", dimensions="insightTrafficSourceType", sort="-views", **base)))
    save(os.path.join(d, "search_terms.csv"), table(analytics(tok, metrics="views", dimensions="insightTrafficSourceDetail", filters="insightTrafficSourceType==YT_SEARCH", sort="-views", maxResults=25, **base)))
    save(os.path.join(d, "countries.csv"), table(analytics(tok, metrics="views,estimatedMinutesWatched", dimensions="country", sort="-views", maxResults=25, **base)))
    save(os.path.join(d, "devices.csv"), table(analytics(tok, metrics="views,averageViewDuration", dimensions="deviceType", **base)))
    save(os.path.join(d, "content_type.csv"), table(analytics(tok, metrics="views,engagedViews,estimatedMinutesWatched,averageViewDuration", dimensions="creatorContentType", **base)))
    for vid in ids:
        r = analytics(tok, metrics="audienceWatchRatio,relativeRetentionPerformance", dimensions="elapsedVideoTimeRatio", filters="video==" + vid, **base)
        save(os.path.join(d, "retention_" + vid + ".csv"), table(r))
    s = item["statistics"]
    print(item["snippet"]["title"], "subs", s.get("subscriberCount"), "views", s.get("viewCount"), "videos", s.get("videoCount"))
    print("window", start, "to", end, "files in", d)


def complete(q):
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(dict(client="firefox", ds="yt", q=q))
    try:
        return json.loads(urllib.request.urlopen(url, timeout=10).read().decode("utf-8", "ignore"))[1]
    except Exception:
        return []


def suggest(seed):
    hits = {}
    for i, s in enumerate(complete(seed)):
        hits.setdefault(s, [0, 99])
        hits[s][0] += 3
        hits[s][1] = min(hits[s][1], i)
    for ch in "abcdefghijklmnopqrstuvwxyz":
        for i, s in enumerate(complete(seed + " " + ch)):
            hits.setdefault(s, [0, 99])
            hits[s][0] += 1
            hits[s][1] = min(hits[s][1], i)
    for w in ("why", "how", "what", "is"):
        for i, s in enumerate(complete(w + " " + seed)):
            hits.setdefault(s, [0, 99])
            hits[s][0] += 1
            hits[s][1] = min(hits[s][1], i)
    rows = sorted(hits.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
    os.makedirs(OUT, exist_ok=True)
    save(os.path.join(OUT, "suggest_" + seed.replace(" ", "_") + ".csv"), [["phrase", "hits", "best_rank"]] + [[k, v[0], v[1]] for k, v in rows])
    for k, v in rows[:40]:
        print(v[0], v[1], k, flush=True)


def iso_seconds(d):
    import re
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    dd, h, mi, s = (int(x or 0) for x in m.groups())
    return dd * 86400 + h * 3600 + mi * 60 + s


def outliers(label, query, max_subs=None, kind="long", months=None):
    tok = access(label)
    p = dict(part="snippet", q=query, type="video", maxResults=50, order="relevance")
    if months:
        p["publishedAfter"] = (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(days=30 * int(months))).strftime("%Y-%m-%dT%H:%M:%SZ")
    s = get("https://www.googleapis.com/youtube/v3/search", p, tok)
    ids = [i["id"]["videoId"] for i in s.get("items", [])]
    if not ids:
        print(s)
        return
    v = get("https://www.googleapis.com/youtube/v3/videos", dict(part="snippet,statistics,contentDetails", id=",".join(ids)), tok)["items"]
    cids = list({x["snippet"]["channelId"] for x in v})
    chans = {}
    for k in range(0, len(cids), 50):
        for c in get("https://www.googleapis.com/youtube/v3/channels", dict(part="snippet,statistics", id=",".join(cids[k:k + 50])), tok)["items"]:
            chans[c["id"]] = c
    rows = []
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    for x in v:
        sec = iso_seconds(x["contentDetails"]["duration"])
        if kind == "long" and sec <= 180:
            continue
        if kind == "short" and sec > 180:
            continue
        c = chans.get(x["snippet"]["channelId"])
        if not c:
            continue
        cs = c["statistics"]
        subs = int(cs.get("subscriberCount", 0))
        if max_subs and subs > int(max_subs):
            continue
        avg = int(cs.get("viewCount", 0)) / max(1, int(cs.get("videoCount", 1)))
        views = int(x["statistics"].get("viewCount", 0))
        pub = datetime.datetime.strptime(x["snippet"]["publishedAt"][:19], "%Y-%m-%dT%H:%M:%S")
        days = max(1, (now - pub).days)
        rows.append([round(views / max(1, avg), 1), views, subs, days, round(views / days), sec // 60, x["snippet"]["title"], c["snippet"]["title"], x["id"]])
    rows.sort(key=lambda r: -r[0])
    os.makedirs(OUT, exist_ok=True)
    save(os.path.join(OUT, "outliers_" + query.replace(" ", "_") + ".csv"),
         [["outlier_x", "views", "channel_subs", "age_days", "views_per_day", "minutes", "title", "channel", "videoId"]] + rows)
    for r in rows[:25]:
        print(r[0], "x |", r[1], "views |", r[2], "subs |", r[3], "d |", r[5], "min |", r[6], "|", r[7])


CATS = {"film": "1", "people": "22", "entertainment": "24", "education": "27", "comedy": "23", "news": "25", "howto": "26", "all": ""}


def trending(label, region="US", cat="all", query=None):
    tok = access(label)
    rows = []
    if query:
        p = dict(part="snippet", q=query, type="video", maxResults=50, order="viewCount",
                 publishedAfter=(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        if region != "ALL":
            p["regionCode"] = region
        ids = [i["id"]["videoId"] for i in get("https://www.googleapis.com/youtube/v3/search", p, tok).get("items", [])]
        items = get("https://www.googleapis.com/youtube/v3/videos", dict(part="snippet,statistics,contentDetails", id=",".join(ids)), tok).get("items", []) if ids else []
    else:
        p = dict(part="snippet,statistics,contentDetails", chart="mostPopular", regionCode=region, maxResults=50)
        if CATS.get(cat, cat):
            p["videoCategoryId"] = CATS.get(cat, cat)
        r = get("https://www.googleapis.com/youtube/v3/videos", p, tok)
        if "error" in r:
            print(r["error"])
            return
        items = r.get("items", [])
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    for x in items:
        pub = datetime.datetime.strptime(x["snippet"]["publishedAt"][:19], "%Y-%m-%dT%H:%M:%S")
        hours = max(1, (now - pub).total_seconds() / 3600)
        views = int(x["statistics"].get("viewCount", 0))
        rows.append([round(views / hours), views, round(hours / 24, 1), iso_seconds(x["contentDetails"]["duration"]) // 60, x["snippet"]["title"], x["snippet"]["channelTitle"], x["id"]])
    rows.sort(key=lambda r: -r[0])
    os.makedirs(OUT, exist_ok=True)
    name = "trending_" + (query or cat).replace(" ", "_") + "_" + region + ".csv"
    save(os.path.join(OUT, name), [["views_per_hour", "views", "age_days", "minutes", "title", "channel", "videoId"]] + rows)
    for r in rows[:25]:
        print(r[0], "vph |", r[1], "views |", r[2], "d |", r[3], "min |", r[4], "|", r[5])


STOP = set("a an the and or of to in on for with is are was it its this that you your i my me we our how why what when who does do make makes made from by at as be vs".split())


def seo(label, query, region="US"):
    import re
    from collections import Counter
    tok = access(label)
    p = dict(part="snippet", q=query, type="video", maxResults=25, order="relevance", regionCode=region)
    ids = [i["id"]["videoId"] for i in get("https://www.googleapis.com/youtube/v3/search", p, tok).get("items", [])]
    vids = get("https://www.googleapis.com/youtube/v3/videos", dict(part="snippet,statistics", id=",".join(ids)), tok).get("items", []) if ids else []
    tags, words, pairs = Counter(), Counter(), Counter()
    with_tags = chapters = 0
    dlen = []
    for v in vids:
        sn = v["snippet"]
        w = 1 + (int(v["statistics"].get("viewCount", 0)) ** 0.25)
        t = [x.lower().strip() for x in sn.get("tags", [])]
        if t:
            with_tags += 1
        for x in set(t):
            tags[x] += w
        toks = [x for x in re.findall(r"[a-z0-9$']+", sn["title"].lower())]
        for x in set(toks) - STOP:
            words[x] += w
        for a, b in set(zip(toks, toks[1:])):
            if a not in STOP or b not in STOP:
                pairs[a + " " + b] += w
        d = sn.get("description", "")
        dlen.append(len(d))
        if len(re.findall(r"(?m)^\s*\(?\d{1,2}:\d{2}", d)) >= 3:
            chapters += 1
    ac = [k for k in complete(query)]
    for ch in "abcdefghij":
        ac += complete(query + " " + ch)
    ac = list(dict.fromkeys(ac))
    os.makedirs(OUT, exist_ok=True)
    rows = [["kind", "item", "score"]]
    rows += [["tag", k, round(v, 1)] for k, v in tags.most_common(40)]
    rows += [["title_word", k, round(v, 1)] for k, v in words.most_common(25)]
    rows += [["title_phrase", k, round(v, 1)] for k, v in pairs.most_common(25)]
    rows += [["autocomplete", k, ""] for k in ac[:40]]
    rows += [["top_title", v["snippet"]["title"], v["statistics"].get("viewCount", 0)] for v in vids]
    save(os.path.join(OUT, "seo_" + query.replace(" ", "_") + ".csv"), rows)
    print("videos", len(vids), "| with tags", with_tags, "| with chapters", chapters, "| median description chars", sorted(dlen)[len(dlen) // 2] if dlen else 0)
    print("TAGS:", ", ".join(k for k, _ in tags.most_common(25)))
    print("TITLE WORDS:", ", ".join(k for k, _ in words.most_common(15)))
    print("TITLE PHRASES:", ", ".join(k for k, _ in pairs.most_common(12)))
    print("AUTOCOMPLETE:", " | ".join(ac[:20]))


def videos_with_channels(tok, ids):
    if not ids:
        return [], {}
    v = get("https://www.googleapis.com/youtube/v3/videos", dict(part="snippet,statistics,contentDetails", id=",".join(ids)), tok).get("items", [])
    cids = list({x["snippet"]["channelId"] for x in v})
    chans = {}
    for k in range(0, len(cids), 50):
        for c in get("https://www.googleapis.com/youtube/v3/channels", dict(part="statistics", id=",".join(cids[k:k + 50])), tok).get("items", []):
            chans[c["id"]] = c
    return v, chans


def search_ids(tok, q, order, days):
    p = dict(part="snippet", q=q, type="video", maxResults=50, order=order,
             publishedAfter=(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    return [i["id"]["videoId"] for i in get("https://www.googleapis.com/youtube/v3/search", p, tok).get("items", [])]


def scan_one(tok, seed, small=50000):
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    ac = list(dict.fromkeys(complete(seed) + complete(seed + " ")))
    v, chans = videos_with_channels(tok, search_ids(tok, seed, "relevance", 365))
    wins = {"long": [], "short": []}
    import re
    key = [w for w in re.findall(r"[a-z0-9]+", seed.lower()) if w not in STOP]
    order = {x["id"]: x for x in v}
    top = v[:20]
    comp = {"title_match": sum(1 for x in v if all(k in x["snippet"]["title"].lower() for k in key)),
            "big_share": round(sum(1 for x in top if int(chans.get(x["snippet"]["channelId"], {}).get("statistics", {}).get("subscriberCount", 0)) > 500000) / max(1, len(top)), 2),
            "small_n": sum(1 for x in v if int(chans.get(x["snippet"]["channelId"], {}).get("statistics", {}).get("subscriberCount", 0)) <= small)}
    for x in v:
        c = chans.get(x["snippet"]["channelId"])
        if not c:
            continue
        cs = c["statistics"]
        subs = int(cs.get("subscriberCount", 0))
        if subs > small:
            continue
        avg = int(cs.get("viewCount", 0)) / max(1, int(cs.get("videoCount", 1)))
        views = int(x["statistics"].get("viewCount", 0))
        ox = views / max(1, avg)
        kind = "short" if iso_seconds(x["contentDetails"]["duration"]) <= 180 else "long"
        if ox >= 3 and views >= 1000:
            wins[kind].append((round(ox, 1), views, x["snippet"]["title"]))
    t, _ = videos_with_channels(tok, search_ids(tok, seed, "viewCount", 14))
    vph = {"long": [], "short": []}
    for x in t:
        pub = datetime.datetime.strptime(x["snippet"]["publishedAt"][:19], "%Y-%m-%dT%H:%M:%S")
        h = max(1, (now - pub).total_seconds() / 3600)
        kind = "short" if iso_seconds(x["contentDetails"]["duration"]) <= 180 else "long"
        vph[kind].append((round(int(x["statistics"].get("viewCount", 0)) / h), x["snippet"]["title"]))
    for k in vph:
        vph[k].sort(key=lambda r: -r[0])
        wins[k].sort(key=lambda r: -r[0])
    return ac, wins, vph, comp


def confidence(ac, wins, vph):
    score = 0
    score += 2 if len(ac) >= 8 else 1 if len(ac) >= 3 else 0
    nw = len(wins["long"]) + len(wins["short"])
    score += 3 if nw >= 4 else 2 if nw >= 2 else 1 if nw == 1 else 0
    top = max([r[0] for r in vph["long"][:1] + vph["short"][:1]] or [0])
    score += 2 if top >= 2000 else 1 if top >= 200 else 0
    level = "High" if score >= 6 else "Medium" if score >= 4 else "Low"
    sl, ss = len(wins["short"]), len(wins["long"])
    tl = vph["long"][0][0] if vph["long"] else 0
    ts = vph["short"][0][0] if vph["short"] else 0
    if ss >= 2 and sl <= ss:
        fmt = "Long (Shorts cut from it)"
    elif sl >= 2 and ss == 0:
        fmt = "Shorts"
    elif ts > 3 * max(1, tl):
        fmt = "Shorts"
    elif tl > 0 or ss > 0:
        fmt = "Long (Shorts cut from it)"
    else:
        fmt = "Shorts (test first)"
    return score, level, fmt


def scan(label, seeds_file, small="50000"):
    tok = access(label)
    seeds = [l.strip() for l in open(seeds_file) if l.strip() and not l.startswith("#")]
    out = [["seed", "score_of_7", "confidence", "format", "competition", "title_match_of_50", "big_channel_share_top20", "autocomplete_n", "long_wins", "short_wins", "top_long_vph", "top_short_vph", "best_long_win", "best_short_win", "hot_now", "autocomplete"]]
    for sd in seeds:
        ac, wins, vph, comp = scan_one(tok, sd, int(small))
        sc, lv, fmt = confidence(ac, wins, vph)
        cl = "Low" if comp["title_match"] <= 12 and comp["big_share"] <= 0.25 else "High" if comp["title_match"] >= 30 or comp["big_share"] >= 0.5 else "Medium"
        bl = wins["long"][0] if wins["long"] else ("", "", "")
        bs = wins["short"][0] if wins["short"] else ("", "", "")
        hot = (vph["long"] + vph["short"])
        hot = max(hot, key=lambda r: r[0]) if hot else (0, "")
        out.append([sd, sc, lv, fmt, cl, comp["title_match"], comp["big_share"], len(ac), len(wins["long"]), len(wins["short"]),
                    vph["long"][0][0] if vph["long"] else 0, vph["short"][0][0] if vph["short"] else 0,
                    "%sx %s" % (bl[0], bl[2]) if bl[0] else "", "%sx %s" % (bs[0], bs[2]) if bs[0] else "",
                    "%s vph %s" % hot if hot[0] else "", " | ".join(ac[:8])])
        print(sd, "|", sc, lv, "|", fmt, "| comp", cl, comp["title_match"], comp["big_share"], "| ac", len(ac), "| wins L/S", len(wins["long"]), len(wins["short"]), "| vph L/S",
              out[-1][10], out[-1][11], flush=True)
    os.makedirs(OUT, exist_ok=True)
    save(os.path.join(OUT, "scan_" + os.path.basename(seeds_file).replace(".txt", "") + ".csv"), out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "auth-url":
        auth_url()
    elif cmd == "exchange":
        exchange(sys.argv[2], sys.argv[3])
    elif cmd == "report":
        report(sys.argv[2], *sys.argv[3:5])
    elif cmd == "suggest":
        suggest(sys.argv[2])
    elif cmd == "outliers":
        outliers(sys.argv[2], sys.argv[3], *sys.argv[4:7])
    elif cmd == "trending":
        trending(sys.argv[2], *sys.argv[3:6])
    elif cmd == "scan":
        scan(sys.argv[2], sys.argv[3], *sys.argv[4:5])
    elif cmd == "seo":
        seo(sys.argv[2], sys.argv[3], *sys.argv[4:5])
