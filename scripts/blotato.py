#!/usr/bin/env python3
"""
Blotato API client (direct REST, no MCP) for the social-media multi-agent project.

Auth: set BLOTATO_API_KEY (env var or .env at the project root). The key may end in '=' — keep it.
Base: https://backend.blotato.com/v2   Header: blotato-api-key: <key>
Everything is async: create -> poll -> use result URLs.

Usage:
  python scripts/blotato.py whoami
  python scripts/blotato.py accounts [--platform linkedin]
  python scripts/blotato.py templates [--search carousel] [--full]
  python scripts/blotato.py source --type youtube --url "..." [--instructions "..."]
  python scripts/blotato.py source --type text --text "..."
  python scripts/blotato.py visual --template <ID> --inputs '<JSON>'
  python scripts/blotato.py post --account <ACCOUNT_ID> --platform twitter --text "..." --next-free-slot
  python scripts/blotato.py post --account <ACCOUNT_ID> --platform linkedin --page <PAGE_ID> \
        --text-file draft.md --media "https://a.jpg,https://b.jpg" --schedule 2026-07-20T13:00:00Z
  python scripts/blotato.py slots-list
  python scripts/blotato.py slots-create --slots '<JSON array>'

Nothing publishes immediately: `post` REQUIRES --next-free-slot or --schedule.
"""
import argparse, json, os, sys, time, urllib.request, urllib.error, urllib.parse

BASE = "https://backend.blotato.com/v2"


def _load_key():
    key = os.environ.get("BLOTATO_API_KEY")
    if not key:
        # .env lives at the project root (parent of scripts/); fall back to
        # scripts/.env for backward compatibility.
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for env_path in (os.path.join(root, ".env"), os.path.join(script_dir, ".env")):
            if os.path.exists(env_path):
                for line in open(env_path):
                    line = line.strip()
                    if line.startswith("BLOTATO_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
            if key:
                break
    if not key:
        sys.exit("ERROR: BLOTATO_API_KEY not set (env var or .env at the project root). "
                 "Get it at my.blotato.com > Settings > API.")
    return key


def _req(method, path, body=None, timeout=60):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("blotato-api-key", _load_key())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        sys.exit(f"HTTP {e.code} on {method} {path}: {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error on {method} {path}: {e}")


def _poll(path, done_states, fail_states, result_key=None, every=5, tries=120):
    for _ in range(tries):
        r = _req("GET", path)
        item = r.get("item", r)
        st = item.get("status")
        if st in done_states:
            return item
        if st in fail_states:
            sys.exit(f"FAILED (status={st}): {json.dumps(item)[:500]}")
        time.sleep(every)
    sys.exit(f"Timed out polling {path}")


# Live-URL field names Blotato may return once a post is live. Best-effort:
# scheduled posts often have no URL yet -> backfill later with `post-status`.
_URL_KEYS = ("url", "postUrl", "permalink", "publishedUrl", "liveUrl", "link")


def _extract_url(item):
    for k in _URL_KEYS:
        v = item.get(k)
        if isinstance(v, str) and v.startswith("http"):
            return v
    # Sometimes nested under content/target/result.
    for parent in ("content", "target", "result", "post"):
        sub = item.get(parent)
        if isinstance(sub, dict):
            u = _extract_url(sub)
            if u:
                return u
    return ""


_LOG_HEADER = (
    "# Published posts — live log\n\n"
    "> Written by `scripts/blotato.py post --log <this file>` on scheduling/publishing.\n"
    "> Empty URL = scheduled, not live yet. Backfill with `post-status --id <id> --log <file>`.\n\n"
    "| Date (UTC) | Platform | Status | Scheduled | Live URL | submissionId | Draft |\n"
    "|---|---|---|---|---|---|---|\n"
)


def _append_log(path, item, platform, scheduled, sub_id, draft):
    """Append (or backfill) one markdown row in the per-brand live log."""
    if not path:
        return
    exists = os.path.exists(path)
    lines = open(path).read().splitlines(keepends=True) if exists else []
    if not lines:
        lines = [_LOG_HEADER]
    url = _extract_url(item) if isinstance(item, dict) else ""
    status = (item or {}).get("status", "unknown") if isinstance(item, dict) else "unknown"
    stamp = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
    # Backfill: if a row already carries this submissionId, update it in place.
    for i, ln in enumerate(lines):
        if sub_id and f"| {sub_id} |" in ln:
            row = f"| {stamp} | {platform} | {status} | {scheduled or '—'} | {url or '—'} | {sub_id} | {draft or '—'} |\n"
            lines[i] = row
            open(path, "w").writelines(lines)
            print(f"# log backfilled: {path} ({sub_id})", file=sys.stderr)
            return
    row = f"| {stamp} | {platform} | {status} | {scheduled or '—'} | {url or '—'} | {sub_id or '—'} | {draft or '—'} |\n"
    lines.append(row)
    open(path, "w").writelines(lines)
    print(f"# log updated: {path}", file=sys.stderr)


# ---------- commands ----------

def cmd_whoami(a):
    print(json.dumps(_req("GET", "/users/me"), indent=2))


def cmd_accounts(a):
    path = "/users/me/accounts" + (f"?platform={a.platform}" if a.platform else "")
    r = _req("GET", path)
    print(json.dumps(r, indent=2))


def cmd_templates(a):
    fields = "id,name,description,inputs" if a.full else "id,name,description"
    path = f"/videos/templates?fields={fields}"
    if a.search:
        path += f"&search={urllib.parse.quote(a.search)}"
    print(json.dumps(_req("GET", path), indent=2))


def cmd_source(a):
    src = {"sourceType": a.type}
    if a.type in ("text", "perplexity-query"):
        src["text"] = a.text
    else:
        src["url"] = a.url
    body = {"source": src}
    if a.instructions:
        body["customInstructions"] = a.instructions
    created = _req("POST", "/source-resolutions-v3", body)
    sid = created.get("id") or created.get("item", {}).get("id")
    print(f"# source id: {sid}", file=sys.stderr)
    item = _poll(f"/source-resolutions-v3/{sid}",
                 {"completed"}, {"failed"})
    print(json.dumps(item, indent=2))


def cmd_write(a):
    """Blotato writes the copy. Wraps source-resolutions (text or perplexity-query)
    with customInstructions and returns ONLY the generated content (+ title)."""
    stype = "perplexity-query" if a.research else "text"
    brief = a.brief
    if a.brief_file:
        brief = open(a.brief_file).read().strip()
    if not brief:
        sys.exit("ERROR: provide --brief or --brief-file (the topic/brief to write from)")
    if not a.instructions and not a.instructions_file:
        sys.exit("ERROR: provide --instructions or --instructions-file (how Blotato should write it)")
    instructions = a.instructions
    if a.instructions_file:
        instructions = open(a.instructions_file).read().strip()
    body = {"source": {"sourceType": stype, "text": brief},
            "customInstructions": instructions}
    created = _req("POST", "/source-resolutions-v3", body)
    sid = created.get("id") or created.get("item", {}).get("id")
    print(f"# write/source id: {sid}", file=sys.stderr)
    item = _poll(f"/source-resolutions-v3/{sid}", {"completed"}, {"failed"})
    out = {"title": item.get("title"), "content": item.get("content")}
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_visual(a):
    inputs = json.loads(a.inputs)
    body = {"templateId": a.template, "inputs": inputs, "render": True}
    if a.brand_kit:
        body["useBrandKit"] = True
    created = _req("POST", "/videos/from-templates", body)
    vid = created.get("item", {}).get("id") or created.get("id")
    print(f"# visual id: {vid}", file=sys.stderr)
    item = _poll(f"/videos/creations/{vid}",
                 {"done"}, {"creation-from-template-failed", "insufficient-credits"})
    out = {"id": item.get("id"),
           "imageUrls": item.get("imageUrls"),
           "mediaUrl": item.get("mediaUrl")}
    print(json.dumps(out, indent=2))


def cmd_post(a):
    if not a.next_free_slot and not a.schedule:
        sys.exit("REFUSED: pass --next-free-slot or --schedule. Nothing publishes immediately.")
    text = a.text
    if a.text_file:
        text = open(a.text_file).read().strip()
    if text is None:
        sys.exit("ERROR: provide --text or --text-file")
    media = [u.strip() for u in a.media.split(",")] if a.media else []
    content = {"text": text, "mediaUrls": media, "platform": a.platform}
    target = {"targetType": a.platform}
    if a.page:
        target["pageId"] = a.page
    if a.platform == "facebook" and not a.page:
        sys.exit("ERROR: Facebook requires --page (pageId).")
    body = {"post": {"accountId": a.account, "content": content, "target": target}}
    if a.schedule:
        body["scheduledTime"] = a.schedule
    else:
        body["useNextFreeSlot"] = True
    created = _req("POST", "/posts", body)
    sub = created.get("postSubmissionId") or created.get("id")
    print(f"# postSubmissionId: {sub}", file=sys.stderr)
    scheduled = a.schedule or "next-free-slot"
    if a.no_wait:
        _append_log(a.log, created, a.platform, scheduled, sub, a.draft or a.text_file)
        print(json.dumps(created, indent=2)); return
    item = _poll(f"/posts/{sub}", {"published", "scheduled"}, {"failed"}, every=3, tries=40)
    _append_log(a.log, item, a.platform, scheduled, sub, a.draft or a.text_file)
    print(json.dumps(item, indent=2))


def cmd_post_status(a):
    """Fetch a submitted post's current state; optionally backfill its live URL into a log."""
    item = _req("GET", f"/posts/{a.id}")
    item = item.get("item", item)
    if a.log:
        _append_log(a.log, item, a.platform or item.get("platform", "—"),
                    a.schedule, a.id, a.draft)
    print(json.dumps(item, indent=2))


def cmd_slots_list(a):
    print(json.dumps(_req("GET", "/schedule/slots"), indent=2))


def cmd_slots_create(a):
    body = {"slots": json.loads(a.slots)}
    print(json.dumps(_req("POST", "/schedule/slots", body), indent=2))


def main():
    p = argparse.ArgumentParser(description="Blotato direct REST client")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("whoami").set_defaults(fn=cmd_whoami)

    sp = sub.add_parser("accounts"); sp.add_argument("--platform"); sp.set_defaults(fn=cmd_accounts)

    sp = sub.add_parser("templates")
    sp.add_argument("--search"); sp.add_argument("--full", action="store_true")
    sp.set_defaults(fn=cmd_templates)

    sp = sub.add_parser("source")
    sp.add_argument("--type", required=True)
    sp.add_argument("--url"); sp.add_argument("--text"); sp.add_argument("--instructions")
    sp.set_defaults(fn=cmd_source)

    sp = sub.add_parser("write", help="Blotato writes copy from a brief + instructions")
    sp.add_argument("--brief"); sp.add_argument("--brief-file")
    sp.add_argument("--instructions"); sp.add_argument("--instructions-file")
    sp.add_argument("--research", action="store_true",
                    help="use perplexity-query (Blotato researches the web first)")
    sp.set_defaults(fn=cmd_write)

    sp = sub.add_parser("visual")
    sp.add_argument("--template", required=True); sp.add_argument("--inputs", required=True)
    sp.add_argument("--brand-kit", action="store_true")
    sp.set_defaults(fn=cmd_visual)

    sp = sub.add_parser("post")
    sp.add_argument("--account", required=True)
    sp.add_argument("--platform", required=True,
                    choices=["twitter", "linkedin", "instagram", "facebook",
                             "tiktok", "threads", "bluesky", "youtube", "pinterest"])
    sp.add_argument("--page"); sp.add_argument("--text"); sp.add_argument("--text-file")
    sp.add_argument("--media")
    sp.add_argument("--next-free-slot", action="store_true")
    sp.add_argument("--schedule", help="ISO 8601, e.g. 2026-07-20T13:00:00Z")
    sp.add_argument("--no-wait", action="store_true")
    sp.add_argument("--log", help="live log to append, e.g. POSTS-LOG.md")
    sp.add_argument("--draft", help="path to the saved draft, recorded in the log row")
    sp.set_defaults(fn=cmd_post)

    sp = sub.add_parser("post-status", help="poll a submitted post; backfill live URL into --log")
    sp.add_argument("--id", required=True, help="postSubmissionId returned by `post`")
    sp.add_argument("--log"); sp.add_argument("--platform")
    sp.add_argument("--schedule"); sp.add_argument("--draft")
    sp.set_defaults(fn=cmd_post_status)

    sub.add_parser("slots-list").set_defaults(fn=cmd_slots_list)
    sp = sub.add_parser("slots-create"); sp.add_argument("--slots", required=True)
    sp.set_defaults(fn=cmd_slots_create)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
