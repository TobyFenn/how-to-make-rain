#!/usr/bin/env python3
"""
Mirror the NWS ZHU (Houston ARTCC CWSU) Training Page into a local archive
where every resource exists as BOTH a human-readable PDF and an LLM-readable
Markdown file, laid out in section folders that mirror the page.

Usage:  python zhu_scrape.py <output_dir> [--skip-pdf]
"""
import hashlib
import io
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import unicodedata
import urllib.parse as up
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import MarkdownConverter

INDEX_URL = "https://www.weather.gov/source/zhu/ZHU_Training_Page/ZHU_Training_Page.html"
ZHU_PREFIX_RE = re.compile(r"^https?://(www\.)?weather\.gov/(source|media)/zhu/ZHU_Training_Page/", re.I)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 zhu-training-archiver/1.0"
FETCHED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

OUT = Path(sys.argv[1]).expanduser().resolve()
SKIP_PDF = "--skip-pdf" in sys.argv
REUSE_PDF = "--reuse-pdf" in sys.argv
OUT.mkdir(parents=True, exist_ok=True)
CHROME_PROFILE = OUT / ".chrome-profile"
(OUT / ".chrome-tmp").mkdir(exist_ok=True)

session = requests.Session()
session.headers["User-Agent"] = UA
session.headers["Accept"] = "*/*"

LOG = []
def log(msg):
    print(msg, flush=True)
    LOG.append(msg)

# --------------------------------------------------------------------------- utils
def slugify(s, maxlen=70):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s-]", " ", s).strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:maxlen].strip("-") or "item"

def norm_url(u):
    u = u.strip()
    u = up.urldefrag(u)[0]
    p = up.urlsplit(u)
    # weather.gov http -> https and strip www variance for identity purposes only
    return up.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path, p.query, ""))

def is_zhu(u):
    return bool(ZHU_PREFIX_RE.match(u))

DEAD_HOSTS = set()
_DEADLINE_POOL = ThreadPoolExecutor(max_workers=8)
def with_deadline(seconds, fn, *a, **kw):
    """Run fn in a worker thread; give up (return None) after `seconds` of wall-clock time."""
    fut = _DEADLINE_POOL.submit(fn, *a, **kw)
    try:
        return fut.result(timeout=seconds)
    except Exception as e:  # noqa  (TimeoutError or fn error)
        log(f"    deadline/err ({type(e).__name__}) in {getattr(fn, '__name__', fn)}")
        return None
def fetch(url, timeout=(15, 60), stream=False, tries=3, headers=None):
    """GET with retries. Returns (response|None, error|None). Hosts that refuse/time out on connect are memoised."""
    host = up.urlsplit(url).netloc.lower()
    if host in DEAD_HOSTS:
        return None, "host unreachable (memoised)"
    last = None
    for i in range(tries):
        try:
            r = session.get(url, timeout=timeout, allow_redirects=True, stream=stream, headers=headers)
            if r.status_code < 400:
                return r, None
            last = f"HTTP {r.status_code}"
            if r.status_code in (401, 403, 404, 410):
                break
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
            last = f"{type(e).__name__}"
            if "web.archive.org" not in host:
                DEAD_HOSTS.add(host)
                break
        except Exception as e:  # noqa
            last = f"{type(e).__name__}: {e}"
        time.sleep(1.5 * (i + 1))
    return None, last

def _visible_len(r):
    ct = (r.headers.get("Content-Type") or "").lower()
    if "html" not in ct:
        return len(r.content)
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", r.text)
    return len(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)))

def wayback_lookup(url, want_resp=False):
    """Resolve a good Wayback snapshot via the redirecting /web/<ts>id_/ endpoint (the CDX API hangs).
    Tries a few target years and keeps the candidate with the most visible content (sites often decay
    into stubs before they disappear). Returns (raw_url, pretty_url[, response])."""
    cands = []
    for ts in ("2019", "2015", "2023", "2011"):
        try:
            r = session.get(f"https://web.archive.org/web/{ts}id_/{url}", timeout=(15, 60), allow_redirects=True)
        except Exception as e:  # noqa
            log(f"    wayback lookup failed for {url}: {type(e).__name__}"); continue
        m = re.search(r"/web/(\d+)id_/", r.url)
        if r.status_code < 400 and m and len(r.content) > 0:
            got = m.group(1)
            if any(c[0] == got for c in cands):
                continue
            cands.append((got, r, _visible_len(r)))
            if len(cands) >= 2:
                break
    if not cands:
        return (None, None, None) if want_resp else (None, None)
    got, r, _ = max(cands, key=lambda c: c[2])
    raw = f"https://web.archive.org/web/{got}id_/{url}"
    pretty = f"https://web.archive.org/web/{got}/{url}"
    return (raw, pretty, r) if want_resp else (raw, pretty)

# Hand-curated substitutes for links that are dead/blocked everywhere (same document, different host).
ALT_SOURCES = {
    # Wiley blocks non-browser clients; the paper is CC-BY 4.0 and deposited in HAL (CNRS) by the authors.
    "https://rmets.onlinelibrary.wiley.com/doi/epdf/10.1002/qj.4304": [
        "https://hal.science/hal-03795958/document",
        "https://hal.science/hal-03795958/file/Quart%20J%20Royal%20Meteoro%20Soc%20-%202022%20-%20Fathalli%20-%20Formation%20of%20fog%20due%20to%20stratus%20lowering%20An%20observational%20and%20modelling%20case.pdf",
    ],
}

def fetch_with_fallback(url):
    """Returns (response, via) where via in {'live','wayback','alternate'} or (None, error)."""
    r, err = fetch(url)
    if r is not None:
        return r, "live"
    for alt in ALT_SOURCES.get(url, []):
        log(f"    live fetch failed ({err}); trying alternate source {alt}")
        html_fallback = None
        for hdrs in ({"User-Agent": "curl/8.7.1"}, None):   # some repositories bot-check browser UAs but serve plain clients
            r, err2 = fetch(alt, headers=hdrs, timeout=(15, 180))
            if r is None:
                continue
            if "html" in (r.headers.get("Content-Type") or "").lower():
                html_fallback = html_fallback or r
                continue
            r.alternate_url = alt
            return r, "alternate"
        if html_fallback is not None and alt is ALT_SOURCES[url][-1]:
            html_fallback.alternate_url = alt
            return html_fallback, "alternate"
    log(f"    live fetch failed ({err}); trying Wayback Machine …")
    raw, pretty, r2 = wayback_lookup(url, want_resp=True)
    if r2 is not None:
        r2.wayback_url = pretty
        r2.wayback_raw = raw
        return r2, "wayback"
    return None, f"{err}; no Wayback snapshot"

def sniff_kind(url, resp):
    ct = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower() if resp is not None else ""
    path = up.urlsplit(url).path.lower()
    ext = os.path.splitext(path)[1]
    if ct == "application/pdf" or ext == ".pdf":
        return "pdf"
    if ext in (".ppsx", ".pptx", ".pps", ".ppt") or "presentationml" in ct or "ms-powerpoint" in ct:
        return "pptx"
    if ct.startswith("image/") or ext in (".png", ".gif", ".jpg", ".jpeg", ".webp", ".svg"):
        return "image"
    if "html" in ct or ext in (".htm", ".html", ".php", ".shtml", ".cfm", "") or ct == "" or ct.startswith("text/"):
        return "html"
    return "binary"

def chrome_pdf(src, out_pdf, timeout=120):
    if SKIP_PDF:
        return False
    if isinstance(src, Path):
        src = src.resolve().as_uri()
    import tempfile, signal
    out_pdf = Path(out_pdf)
    if REUSE_PDF and out_pdf.exists() and out_pdf.stat().st_size > 500:
        return True
    if out_pdf.exists():
        out_pdf.unlink()
    profile = tempfile.mkdtemp(prefix="zhu-chrome-", dir=str(CHROME_PROFILE.parent / ".chrome-tmp"))
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
           f"--user-data-dir={profile}", "--hide-scrollbars", "--run-all-compositor-stages-before-draw",
           "--virtual-time-budget=15000", "--no-pdf-header-footer", "--allow-file-access-from-files",
           "--disable-extensions", "--disable-background-networking", "--disable-sync",
           f"--print-to-pdf={out_pdf}", src]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    t0 = time.time(); stable = 0; last = -1
    try:
        while time.time() - t0 < timeout:
            if proc.poll() is not None:
                break
            if out_pdf.exists():
                sz = out_pdf.stat().st_size
                stable = stable + 1 if sz == last and sz > 0 else 0
                last = sz
                if stable >= 3:      # PDF written and unchanged for ~1.5 s: Chrome is just lingering
                    break
            time.sleep(0.5)
        else:
            log(f"    chrome timeout printing {src}")
    finally:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:  # noqa
            pass
        try:
            proc.wait(timeout=5)
        except Exception:  # noqa
            pass
        shutil.rmtree(profile, ignore_errors=True)
    return out_pdf.exists() and out_pdf.stat().st_size > 500

def front_matter(**kv):
    lines = ["---"]
    for k, v in kv.items():
        if v is None or v == "":
            continue
        if isinstance(v, list):
            lines.append(f"{k}:")
            for x in v:
                lines.append(f"  - {json.dumps(x)}")
        else:
            lines.append(f"{k}: {json.dumps(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"

def rel(from_dir: Path, to: Path):
    return os.path.relpath(to, from_dir).replace(os.sep, "/")


class FakeResponse:
    """Response-like object built from a previously captured file (resume support)."""
    def __init__(self, content, url, content_type, wayback_url=None, wayback_raw=None):
        self.content = content; self.url = url
        self.headers = {"Content-Type": content_type or ""}
        self.encoding = None
        self.status_code = 200
        if wayback_url: self.wayback_url = wayback_url
        if wayback_raw: self.wayback_raw = wayback_raw
    @property
    def apparent_encoding(self):
        try:
            from charset_normalizer import from_bytes
            best = from_bytes(self.content[:200000]).best()
            return best.encoding if best else "utf-8"
        except Exception:  # noqa
            return "utf-8"

def save_capture(item_dir: Path, item, resp, kind, source_file):
    (item_dir / ".capture.json").write_text(json.dumps({
        "url": item["url"], "via": item.get("via"), "wayback_url": item.get("wayback_url"), "alternate_url": item.get("alternate_url"),
        "wayback_raw": getattr(resp, "wayback_raw", None), "final_url": getattr(resp, "url", item["url"]),
        "kind": kind, "content_type": (resp.headers.get("Content-Type") or ""), "source_file": source_file,
        "captured": FETCHED_AT}, indent=1))

WAYBACK_HINT = set()   # URLs known (from a previous run's log) to have come via Wayback
def load_capture(item_dir: Path, item):
    """Return (resp, via) from disk if this item was captured before, else (None, None)."""
    cj = item_dir / ".capture.json"
    src_dir = item_dir / "source"
    if cj.exists():
        try:
            m = json.loads(cj.read_text())
            f = item_dir / m["source_file"]
            if f.exists():
                item["wayback_url"] = m.get("wayback_url")
                if m.get("alternate_url"): item["alternate_url"] = m.get("alternate_url")
                return FakeResponse(f.read_bytes(), m.get("final_url") or item["url"], m.get("content_type"),
                                    m.get("wayback_url"), m.get("wayback_raw")), m.get("via") or "live"
        except Exception:  # noqa
            pass
    # legacy (first run, before .capture.json existed): infer from source/ contents
    if src_dir.is_dir():
        files = [f for f in src_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
        if len(files) == 1:
            f = files[0]
            ct = mimetypes.guess_type(f.name)[0] or ("text/html" if f.suffix in (".htm", ".html") else "")
            if f.name == "original.html": ct = "text/html"
            via, wb_url, wb_raw = "live", None, None
            if item["url"] in WAYBACK_HINT:
                raw, pretty = wayback_lookup(item["url"])
                if raw:
                    via, wb_url, wb_raw = "wayback", pretty, raw
                    item["wayback_url"] = pretty
            return FakeResponse(f.read_bytes(), item["url"], ct, wb_url, wb_raw), via
    return None, None

def load_wayback_hints(logfile):
    try:
        cur = None
        for line in Path(logfile).read_text(errors="replace").splitlines():
            m = re.match(r"^\[\d+/\d+\] .*", line)
            if m: cur = None; continue
            m = re.match(r"^    (https?://\S+)$", line)
            if m and cur is None: cur = m.group(1); continue
            if "trying Wayback Machine" in line and cur: WAYBACK_HINT.add(cur)
            if "FAILED:" in line and cur: WAYBACK_HINT.discard(cur)
    except Exception:  # noqa
        pass

# --------------------------------------------------------------------------- index parsing
def parse_index(html):
    soup = BeautifulSoup(html, "html5lib")
    sections = []          # ordered list of {name, items:[...]}
    by_name = {}
    def section(name):
        if name not in by_name:
            by_name[name] = {"name": name, "items": []}
            sections.append(by_name[name])
        return by_name[name]

    for table in soup.find_all("table"):
        rows = table.find_all("tr", recursive=False) or table.find_all("tr")
        rows = [r for r in table.find_all("tr") if r.find_parent("table") is table]
        headers = []
        for tr in rows:
            tds = [td for td in tr.find_all("td") if td.find_parent("tr") is tr]
            has_link = any(td.find("a", href=True) for td in tds)
            if not headers and not has_link:
                headers = [td.get_text(" ", strip=True) for td in tds if td.get_text(strip=True)]
                continue
            if not headers:
                continue
            for i, td in enumerate(tds):
                sec_name = headers[i] if i < len(headers) else headers[-1]
                # notes (no link) inside a td -> attach as section note
                links = [a for a in td.find_all("a", href=True) if a["href"].strip() and a.get_text(strip=True)]
                if not links:
                    note = td.get_text(" ", strip=True)
                    if note:
                        section(sec_name).setdefault("notes", []).append(note)
                    continue
                # split td into groups: a <br> separates independent groups; within a group first link is primary
                groups, cur = [], []
                for node in td.descendants:
                    if isinstance(node, Tag) and node.name == "br":
                        if cur:
                            groups.append(cur); cur = []
                    elif isinstance(node, Tag) and node.name == "a" and node.get("href", "").strip() and node.get_text(strip=True):
                        cur.append(node)
                if cur:
                    groups.append(cur)
                td_text = td.get_text(" ", strip=True)
                for g in groups:
                    primary = g[0].get_text(" ", strip=True)
                    if re.match(r"^\(.*\)$", primary):
                        # label lives outside the anchor, e.g. "Commercial Pilot Meteorology (Part 1) (Part 2)"
                        pre = td_text.split(primary)[0].strip()
                        if pre:
                            primary = f"{pre} {primary}"
                    for j, a in enumerate(g):
                        label = a.get_text(" ", strip=True)
                        title = primary if j == 0 else f"{primary} — {label}"
                        href = up.urljoin(INDEX_URL, a["href"].strip())
                        section(sec_name)["items"].append({
                            "title": title, "label": label, "primary": primary,
                            "url": href, "section": sec_name,
                        })
    return sections

# --------------------------------------------------------------------------- HTML → local page + markdown
class MD(MarkdownConverter):
    def convert_div(self, el, text, parent_tags):
        text = text.strip("\n")
        return f"\n\n{text}\n\n" if text.strip() else ""
    def convert_center(self, el, text, parent_tags):
        return self.convert_div(el, text, parent_tags)
    def convert_font(self, el, text, parent_tags):
        return text
    def convert_img(self, el, text, parent_tags):
        alt = el.attrs.get("alt", None) or ""
        src = el.attrs.get("src", None) or ""
        title = el.attrs.get("title", None) or ""
        title_part = ' "%s"' % title.replace('"', r"\"") if title else ""
        return f"![{alt}]({src}{title_part})"

BLOCK_TAGS = {"p", "div", "ul", "ol", "table", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "hr", "center", "form"}
def is_layout_table(t):
    rows = [r for r in t.find_all("tr") if r.find_parent("table") is t]
    if len(rows) <= 1:
        return True
    ncols = max((len([c for c in r.find_all(["td", "th"]) if c.find_parent("tr") is r]) for r in rows), default=0)
    if ncols <= 1:
        return True
    if t.find("table"):
        return True
    for c in t.find_all(["td", "th"]):
        if c.find_parent("table") is not t:
            continue
        if c.find(BLOCK_TAGS - {"p"}) or len(c.find_all("p")) > 1 or len(c.find_all("br")) > 3:
            return True
        if len(c.get_text(" ", strip=True)) > 300 or c.find("img") and len(c.get_text(strip=True)) > 120:
            return True
    return False

def unwrap_layout_tables(soup):
    """Turn presentational (layout) tables into plain block flow so Markdown reads top-to-bottom;
    genuine data tables (regular grid of short cells) are kept as tables."""
    changed = True
    while changed:
        changed = False
        for t in soup.find_all("table"):
            if is_layout_table(t):
                own = lambda tags: [x for x in t.find_all(tags) if x.find_parent("table") is t]
                for c in own(["td", "th"]):
                    c.name = "div"
                for r in own("tr"):
                    r.unwrap()
                for g in own(["tbody", "thead", "tfoot", "colgroup", "col", "caption"]):
                    if g.name == "caption":
                        g.name = "p"
                    else:
                        g.unwrap()
                t.name = "div"
                changed = True
                break
    return soup

def html_to_md(soup_body):
    md = MD(heading_style="ATX", bullets="-", strip=["script", "style"]).convert_soup(soup_body)
    md = re.sub(r"\*{4}", "**", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"[ \t]+\n", "\n", md)
    return md.strip() + "\n"

ASSET_ATTRS = [("img", "src"), ("link", "href"), ("script", "src"), ("source", "src"), ("embed", "src"),
               ("iframe", "src"), ("input", "src"), ("body", "background"), ("td", "background"), ("table", "background")]

def process_html_page(url, resp, item_dir: Path, slug: str, item, crawl_queue, url_to_local):
    """Mirror an HTML page: save source, download assets, rewrite links, produce .md and .pdf.
    crawl_queue: list to which discovered internal ZHU pages are appended (for recursion)."""
    raw = resp.content
    enc = resp.encoding or "iso-8859-1"
    try:
        html = raw.decode(resp.apparent_encoding or enc, errors="replace")
    except Exception:  # noqa
        html = raw.decode("iso-8859-1", errors="replace")
    (item_dir / "source").mkdir(exist_ok=True)
    (item_dir / "source" / "original.html").write_bytes(raw)

    soup = BeautifulSoup(html, "html5lib")
    for t in soup(["script", "noscript"]):
        t.decompose()
    base_tag = soup.find("base", href=True)
    base_url = up.urljoin(url, base_tag["href"]) if base_tag else url
    if base_tag:
        base_tag.decompose()

    assets_dir = item_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    asset_map = {}
    amap_file = assets_dir / ".map.json"
    if amap_file.exists():
        try:
            for k, v in json.loads(amap_file.read_text()).items():
                if v and (assets_dir / v).exists():
                    asset_map[k] = assets_dir / v
                elif not v:
                    asset_map[k] = None   # known missing from a previous run — don't spend time retrying
        except Exception:  # noqa
            pass
    external = not is_zhu(url)
    budget_end = time.time() + (150 if external else 600)
    counters = {"css": 0, "img": 0, "wb_fail": 0}
    FONT_EXT = (".woff", ".woff2", ".ttf", ".otf", ".eot")
    wb_ts = None
    if getattr(resp, "wayback_raw", None):
        m = re.search(r"/web/(\d+)id_/", resp.wayback_raw)
        wb_ts = m.group(1) if m else None
    def local_asset(abs_url):
        if abs_url in asset_map:
            return asset_map[abs_url]
        low = up.urlsplit(abs_url).path.lower()
        if low.endswith(FONT_EXT) or time.time() > budget_end:
            return None
        if external:
            if low.endswith(".css"):
                counters["css"] += 1
                if counters["css"] > 15: return None
            else:
                counters["img"] += 1
                if counters["img"] > 60: return None
        # reuse an asset already on disk from a previous run (by basename)
        guess = re.sub(r"[^\w.\-]+", "_", up.unquote(os.path.basename(up.urlsplit(abs_url).path) or ""))
        if guess and os.path.splitext(guess)[1] and (assets_dir / guess).exists():
            asset_map[abs_url] = assets_dir / guess
            return asset_map[abs_url]
        host = up.urlsplit(abs_url).netloc.lower()
        if wb_ts and "web.archive.org" not in abs_url:
            # archived page: pull assets from the same snapshot era first
            res = with_deadline(45, fetch, f"https://web.archive.org/web/{wb_ts}id_/{abs_url}", timeout=(10, 30), tries=1)
            r, err = res if res else (None, "deadline")
            if r is None:
                res = with_deadline(30, fetch, abs_url, timeout=(10, 20), tries=1)
                r, err = res if res else (None, "deadline")
        else:
            res = with_deadline(45, fetch, abs_url, timeout=(10, 30), tries=1)
            r, err = res if res else (None, "deadline")
        if r is None and "web.archive.org" not in abs_url and not wb_ts and host in DEAD_HOSTS and counters["wb_fail"] < 4:
            # page itself is archived / host is dead: try the Wayback Machine for the asset
            wb_url = f"https://web.archive.org/web/{wb_ts or '2'}id_/{abs_url}"
            res = with_deadline(40, fetch, wb_url, timeout=(10, 25), tries=1)
            r, err = res if res else (None, "deadline")
            counters["wb_fail"] = 0 if r is not None else counters["wb_fail"] + 1
        if r is None:
            asset_map[abs_url] = None
            return None
        path = up.urlsplit(abs_url).path
        name = os.path.basename(path) or "asset"
        name = up.unquote(name)
        ext = os.path.splitext(name)[1]
        if not ext:
            ext = mimetypes.guess_extension((r.headers.get("Content-Type") or "").split(";")[0].strip()) or ""
            name += ext
        name = re.sub(r"[^\w.\-]+", "_", name)
        target = assets_dir / name
        if target.exists() and target.stat().st_size != len(r.content):
            h = hashlib.md5(abs_url.encode()).hexdigest()[:6]
            target = assets_dir / f"{os.path.splitext(name)[0]}_{h}{ext}"
        target.write_bytes(r.content)
        asset_map[abs_url] = target
        return target

    # CSS: also pull url(...) images referenced inside stylesheets
    def rewrite_css(css_text, css_url):
        def repl(m):
            ref = m.group(2).strip()
            if ref.startswith("data:") or not ref:
                return m.group(0)
            absu = up.urljoin(css_url, ref)
            t = local_asset(absu)
            return f"url({m.group(1)}{t.name if t else ref}{m.group(1)})" if t else m.group(0)
        return re.sub(r"url\((['\"]?)([^)'\"]+)\1\)", repl, css_text)

    for tag, attr in ASSET_ATTRS:
        for el in soup.find_all(tag):
            v = el.get(attr)
            if not v or v.startswith("data:") or v.startswith("#"):
                continue
            if tag == "link":
                relv = " ".join(el.get("rel", [])).lower()
                if "stylesheet" not in relv and "icon" not in relv:
                    continue
            absu = up.urljoin(base_url, v.strip())
            if tag == "iframe":
                el[attr] = absu
                continue
            t = local_asset(absu)
            if t is None:
                el[attr] = absu  # keep absolute so it can still be resolved online
                continue
            if tag == "link" and "stylesheet" in " ".join(el.get("rel", [])).lower():
                try:
                    css = t.read_text(errors="replace")
                    t.write_text(rewrite_css(css, absu))
                except Exception:  # noqa
                    pass
            el[attr] = "assets/" + t.name
    # inline <style> blocks
    for st in soup.find_all("style"):
        if st.string:
            st.string = rewrite_css(st.string, base_url)

    # links: internal ZHU links -> queue for crawl and rewrite later; others absolute
    page_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        absu = up.urljoin(base_url, href)
        absu = re.sub(r"^https?://web\.archive\.org/web/\d+(?:id_)?/", "", absu)  # de-archive links
        frag = up.urlsplit(absu).fragment
        n = norm_url(absu)
        a["href"] = absu
        a["data-zhu-target"] = n + (("#" + frag) if frag else "")
        page_links.append(n)
        if is_zhu(n) and n not in url_to_local:
            crawl_queue.append((n, a.get_text(" ", strip=True) or os.path.basename(up.urlsplit(n).path)))
    try:
        amap_file.write_text(json.dumps({k: (v.name if v else None) for k, v in asset_map.items()}, indent=0))
    except Exception:  # noqa
        pass
    item["links_found"] = sorted(set(page_links))
    item["_soup"] = soup
    item["_base_url"] = base_url
    return soup

def finalize_html_page(item, url_to_local):
    """Second pass (after crawl): rewrite links to local mirrors, write page.html/.md/.pdf."""
    soup = item.pop("_soup")
    item_dir = Path(item["dir"])
    slug = item["slug"]
    md_path = item_dir / f"{slug}.md"
    for a in soup.find_all("a", attrs={"data-zhu-target": True}):
        tgt = a["data-zhu-target"]
        n, _, frag = tgt.partition("#")
        loc = url_to_local.get(n)
        if loc:
            a["href"] = rel(item_dir, Path(loc["dir"]) / (loc["slug"] + ".md")) + (("#" + frag) if frag else "")
            a["data-local-html"] = rel(item_dir, Path(loc["dir"]) / "page.html") + (("#" + frag) if frag else "")
        del a["data-zhu-target"]

    # HTML for the human PDF (links to local page.html)
    html_soup = BeautifulSoup(str(soup), "html5lib")
    for a in html_soup.find_all("a", attrs={"data-local-html": True}):
        a["href"] = a["data-local-html"]; del a["data-local-html"]
    for a in soup.find_all("a", attrs={"data-local-html": True}):
        del a["data-local-html"]
    # banner in PDF for provenance
    banner = html_soup.new_tag("div", style="font:12px/1.4 -apple-system,Helvetica,Arial;color:#444;border-bottom:1px solid #ccc;padding:6px 0;margin-bottom:10px")
    banner.string = f"ZHU Training Page archive · {item['title']} · Source: {item['url']} · Captured {FETCHED_AT}" + (f" · via Wayback Machine ({item.get('wayback_url')})" if item.get('via') == 'wayback' else "")
    if html_soup.body:
        html_soup.body.insert(0, banner)
    if not html_soup.find("meta", charset=True):
        m = html_soup.new_tag("meta", charset="utf-8")
        (html_soup.head or html_soup).insert(0, m)
    (item_dir / "page.html").write_text(str(html_soup), encoding="utf-8")

    title_tag = soup.title.get_text(strip=True) if soup.title else ""
    md_soup = BeautifulSoup(str(soup), "html5lib")
    unwrap_layout_tables(md_soup)
    body = md_soup.body or md_soup
    md_body = html_to_md(body)
    fm = front_matter(title=item["title"], page_title=title_tag or None, section=item["section"],
                      source_url=item["url"], captured=FETCHED_AT, via=item.get("via"),
                      wayback_url=item.get("wayback_url"), kind="html",
                      pdf=f"{slug}.pdf", original="source/original.html",
                      parent=item.get("parent_title"))
    header = f"# {item['title']}\n\n> Source: <{item['url']}>  \n> Section: {item['section']}  \n> Captured: {FETCHED_AT}" + (f" (via Wayback Machine: {item['wayback_url']})" if item.get('via') == 'wayback' else "") + f"  \n> PDF: [{slug}.pdf]({slug}.pdf) · Original HTML: [source/original.html](source/original.html)\n\n---\n\n"
    md_path.write_text(fm + header + md_body, encoding="utf-8")
    item["md"] = str(md_path)
    pdf_path = item_dir / f"{slug}.pdf"
    ok = False
    if item.get("via") == "live" and not is_zhu(item["url"]) and item.get("print_live", True):
        ok = chrome_pdf(item["url"], pdf_path)   # live render (JS/CSS intact) for external sites
        # some sites print an empty/blocked page — sanity check size
        if ok and pdf_path.stat().st_size < 3000:
            ok = False
    if not ok:
        ok = chrome_pdf(item_dir / "page.html", pdf_path)
    item["pdf"] = str(pdf_path) if ok else None
    if not ok:
        log(f"    !! PDF failed for {item['title']}")

# --------------------------------------------------------------------------- PDF → markdown
def process_pdf(url, resp, item_dir: Path, slug, item):
    import pymupdf
    (item_dir / "source").mkdir(exist_ok=True)
    orig_name = up.unquote(os.path.basename(up.urlsplit(url).path)) or f"{slug}.pdf"
    orig = item_dir / "source" / orig_name
    orig.write_bytes(resp.content)
    pdf_path = item_dir / f"{slug}.pdf"
    shutil.copyfile(orig, pdf_path)
    item["pdf"] = str(pdf_path)
    md_path = item_dir / f"{slug}.md"
    try:
        doc = pymupdf.open(str(pdf_path))
    except Exception as e:  # noqa
        md_path.write_text(front_matter(title=item["title"], source_url=url, kind="pdf", error=str(e)) + f"# {item['title']}\n\nCould not parse PDF: {e}\n")
        item["md"] = str(md_path); return
    n = doc.page_count
    render_all = n <= 80
    pages_dir = item_dir / "pages"
    parts = []
    total_chars = 0
    for i, page in enumerate(doc):
        text = page.get_text("text")
        total_chars += len(text.strip())
        sparse = len(text.strip()) < 80
        parts.append((i + 1, text, sparse))
    doc_meta = doc.metadata or {}
    body = []
    for pno, text, sparse in parts:
        body.append(f"\n\n## Page {pno}\n\n")
        if render_all or sparse:
            pages_dir.mkdir(exist_ok=True)
            img = pages_dir / f"page-{pno:03d}.jpg"
            if not img.exists():
                pix = doc[pno - 1].get_pixmap(dpi=100)
                pix.save(str(img), jpg_quality=75)
            body.append(f"![Page {pno}](pages/{img.name})\n\n")
        t = text.strip()
        if t:
            body.append(t + "\n")
        elif sparse:
            body.append("_(no extractable text on this page — see rendered image above)_\n")
    fm = front_matter(title=item["title"], section=item["section"], source_url=url, captured=FETCHED_AT,
                      via=item.get("via"), wayback_url=item.get("wayback_url"), alternate_url=item.get("alternate_url"), kind="pdf", pages=n,
                      pdf_title=doc_meta.get("title") or None, pdf_author=doc_meta.get("author") or None,
                      pdf=f"{slug}.pdf", original=f"source/{orig_name}",
                      note="Text extracted with PyMuPDF; page images rendered for visual context." if (render_all or any(p[2] for p in parts)) else "Text extracted with PyMuPDF.")
    header = f"# {item['title']}\n\n> Source: <{url}>  \n> Section: {item['section']}  \n> Captured: {FETCHED_AT}  \n> PDF: [{slug}.pdf]({slug}.pdf) ({n} pages)\n\n---\n"
    md_path.write_text(fm + header + "".join(body), encoding="utf-8")
    item["md"] = str(md_path)
    item["pages"] = n
    if total_chars < 200 * max(1, n) * 0.1:
        item["note"] = "PDF has little extractable text (likely image-based); page renders included in Markdown."

# --------------------------------------------------------------------------- PPTX/PPSX → markdown + pdf
def process_pptx(url, resp, item_dir: Path, slug, item):
    from pptx import Presentation
    from pptx.util import Emu
    (item_dir / "source").mkdir(exist_ok=True)
    orig_name = up.unquote(os.path.basename(up.urlsplit(url).path)) or f"{slug}.ppsx"
    orig = item_dir / "source" / orig_name
    orig.write_bytes(resp.content)
    md_path = item_dir / f"{slug}.md"
    assets = item_dir / "assets"; assets.mkdir(exist_ok=True)
    try:
        prs = Presentation(io.BytesIO(resp.content))
    except Exception as e:  # noqa
        # ppsx main-part content type may not be recognised — patch content types and retry
        import zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zin, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for zi in zin.infolist():
                data = zin.read(zi.filename)
                if zi.filename == "[Content_Types].xml":
                    data = data.replace(b"presentationml.slideshow.main+xml", b"presentationml.presentation.main+xml")
                zout.writestr(zi, data)
        prs = Presentation(io.BytesIO(buf.getvalue()))
    slides_md, slides_html = [], []
    W, H = prs.slide_width, prs.slide_height
    def shape_texts(shape, out):
        if shape.shape_type == 6 and hasattr(shape, "shapes"):  # group
            for s in shape.shapes: shape_texts(s, out)
            return
        if getattr(shape, "has_text_frame", False) and shape.text_frame:
            for p in shape.text_frame.paragraphs:
                t = "".join(r.text for r in p.runs).strip()
                if t:
                    out.append(("  " * min(p.level, 4)) + ("- " if p.level or True else "") + t)
        if getattr(shape, "has_table", False) and shape.has_table:
            rows = []
            for r in shape.table.rows:
                rows.append("| " + " | ".join(c.text.replace("\n", " ").strip() for c in r.cells) + " |")
            if rows:
                rows.insert(1, "|" + "---|" * len(shape.table.rows[0].cells))
                out.append("\n" + "\n".join(rows) + "\n")
    for idx, slide in enumerate(prs.slides, 1):
        title = ""
        try:
            if slide.shapes.title is not None:
                title = slide.shapes.title.text.strip()
        except Exception:  # noqa
            pass
        lines, imgs = [], []
        for shape in slide.shapes:
            if shape.shape_type == 13 or getattr(shape, "image", None) is not None and shape.shape_type == 13:
                try:
                    im = shape.image
                    ext = im.ext
                    name = f"slide{idx:03d}-{len(imgs)+1}.{ext}"
                    (assets / name).write_bytes(im.blob)
                    imgs.append((name, shape))
                except Exception:  # noqa
                    pass
            shape_texts(shape, lines)
        # de-dup title from lines
        if title and lines and lines[0].lstrip("- ").strip() == title:
            lines = lines[1:]
        notes = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            notes = slide.notes_slide.notes_text_frame.text.strip()
        smd = [f"\n\n## Slide {idx}" + (f": {title}" if title else "") + "\n"]
        for name, _ in imgs:
            smd.append(f"![Slide {idx} image](assets/{name})\n")
        if lines:
            smd.append("\n".join(lines) + "\n")
        if notes:
            smd.append(f"\n> **Speaker notes:** {notes}\n")
        slides_md.append("".join(smd))
        # html slide (absolute-positioned approximation)
        parts = [f'<div class="wrap"><div class="slide"><div class="num">Slide {idx}</div>']
        for k, (name, shape) in enumerate(imgs):
            if name.lower().endswith(".gif"):
                # animated GIFs stall Chrome's print pipeline — use a static first frame for the PDF
                try:
                    import pymupdf
                    static = name[:-4] + ".static.png"
                    if not (assets / static).exists():
                        pymupdf.Pixmap(str(assets / name)).save(str(assets / static))
                    imgs[k] = (static, shape); name = static
                except Exception:  # noqa
                    pass
            try:
                l, t, w, h = (shape.left or 0) / W * 100, (shape.top or 0) / H * 100, (shape.width or 0) / W * 100, (shape.height or 0) / H * 100
                parts.append(f'<img src="assets/{name}" style="position:absolute;left:{l:.2f}%;top:{t:.2f}%;width:{w:.2f}%;height:{h:.2f}%;object-fit:contain">')
            except Exception:  # noqa
                parts.append(f'<img src="assets/{name}" style="max-width:100%">')
        for shape in slide.shapes:
            if getattr(shape, "has_text_frame", False) and shape.text_frame and shape.text_frame.text.strip():
                try:
                    l, t, w, h = (shape.left or 0) / W * 100, (shape.top or 0) / H * 100, (shape.width or 0) / W * 100, (shape.height or 0) / H * 100
                except Exception:  # noqa
                    l, t, w, h = 5, 5, 90, 90
                txt = "<br>".join(BeautifulSoup(p, "html.parser").get_text() if False else html_escape(p) for p in shape.text_frame.text.split("\n"))
                is_title = False
                try: is_title = shape == slide.shapes.title
                except Exception: pass
                parts.append(f'<div class="txt{" title" if is_title else ""}" style="left:{l:.2f}%;top:{t:.2f}%;width:{w:.2f}%;min-height:{h:.2f}%">{txt}</div>')
        parts.append("</div>")
        if notes:
            parts.append(f'<div class="notes"><b>Speaker notes (slide {idx}):</b> {html_escape(notes)}</div>')
        parts.append("</div>")
        slides_html.append("".join(parts))
    n = len(prs.slides)
    ratio = H / W * 100
    slide_w = min(10.1, 7.0 / (ratio / 100))   # fit within the 11x8.5in landscape page (0.4in margins) incl. header
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{html_escape(item['title'])}</title>
<style>
@page {{ size: 11in 8.5in; margin: 0.4in; }}
body{{font-family:-apple-system,Helvetica,Arial,sans-serif;color:#111;margin:0}}
.hdr{{font-size:10px;color:#444;border-bottom:1px solid #ccc;padding:2px 0;margin-bottom:4px}}
.slide{{position:relative;width:{slide_w:.3f}in;height:{slide_w*ratio/100:.3f}in;border:1px solid #bbb;background:#fff;margin:0 0 6px 0;overflow:hidden;page-break-inside:avoid}}
.wrap{{page-break-after:always;page-break-inside:avoid}}
.wrap:last-child{{page-break-after:auto}}
.hdr{{page-break-after:avoid}}
.slide .num{{position:absolute;right:4px;bottom:2px;font-size:10px;color:#888}}
.slide .txt{{position:absolute;font-size:14px;line-height:1.25;overflow:hidden;white-space:pre-wrap}}
.slide .txt.title{{font-size:22px;font-weight:bold}}
.notes{{font-size:12px;color:#333;background:#f6f6f6;padding:6px;margin-bottom:14px;border-left:3px solid #999}}
</style></head><body>
<div class="hdr">ZHU Training Page archive · {html_escape(item['title'])} · Source: {html_escape(url)} · Captured {FETCHED_AT} · Rendered from PowerPoint ({n} slides); layout is approximate — original file: source/{html_escape(orig_name)}</div>
{''.join(slides_html)}
</body></html>"""
    (item_dir / "slides.html").write_text(html, encoding="utf-8")
    fm = front_matter(title=item["title"], section=item["section"], source_url=url, captured=FETCHED_AT,
                      via=item.get("via"), kind="pptx", slides=n, pdf=f"{slug}.pdf", original=f"source/{orig_name}",
                      note="Slide text/images extracted with python-pptx; PDF rendered from an HTML approximation of the slides. The original PowerPoint is in source/.")
    header = f"# {item['title']}\n\n> Source: <{url}>  \n> Section: {item['section']}  \n> Captured: {FETCHED_AT}  \n> Format: PowerPoint show ({n} slides). PDF: [{slug}.pdf]({slug}.pdf) · Original: [source/{orig_name}](source/{orig_name})\n\n---\n"
    md_path.write_text(fm + header + "".join(slides_md), encoding="utf-8")
    item["md"] = str(md_path)
    item["slides"] = n
    pdf_path = item_dir / f"{slug}.pdf"
    item["pdf"] = str(pdf_path) if chrome_pdf(item_dir / "slides.html", pdf_path) else None

def html_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

# --------------------------------------------------------------------------- image
def process_image(url, resp, item_dir: Path, slug, item):
    (item_dir / "source").mkdir(exist_ok=True)
    name = up.unquote(os.path.basename(up.urlsplit(url).path)) or "image"
    if not os.path.splitext(name)[1]:
        name += mimetypes.guess_extension((resp.headers.get("Content-Type") or "").split(";")[0]) or ".img"
    orig = item_dir / "source" / name
    orig.write_bytes(resp.content)
    ext = os.path.splitext(name)[1]
    img_copy = item_dir / f"{slug}{ext}"
    shutil.copyfile(orig, img_copy)
    md_path = item_dir / f"{slug}.md"
    # try to describe dimensions
    dims = ""
    try:
        import pymupdf
        pm = pymupdf.Pixmap(str(img_copy)); dims = f"{pm.width}×{pm.height}px"
    except Exception:  # noqa
        pass
    fm = front_matter(title=item["title"], section=item["section"], source_url=url, captured=FETCHED_AT,
                      via=item.get("via"), kind="image", dimensions=dims or None, pdf=f"{slug}.pdf",
                      image=img_copy.name, original=f"source/{name}",
                      note="Live/graphic resource: this is a snapshot at capture time." if item.get("live") else None)
    md = (fm + f"# {item['title']}\n\n> Source: <{url}>  \n> Section: {item['section']}  \n> Captured: {FETCHED_AT}  \n> PDF: [{slug}.pdf]({slug}.pdf)" + (f" · {dims}" if dims else "") + "\n\n---\n\n"
          f"![{item['title']}]({img_copy.name})\n")
    md_path.write_text(md, encoding="utf-8")
    item["md"] = str(md_path)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{html_escape(item['title'])}</title>
<style>@page{{size:auto;margin:0.4in}} body{{font-family:-apple-system,Helvetica,Arial;margin:0}} .hdr{{font-size:12px;color:#444;border-bottom:1px solid #ccc;padding:6px 0;margin-bottom:10px}} img{{max-width:100%;height:auto}}</style></head>
<body><div class="hdr">ZHU Training Page archive · {html_escape(item['title'])} · Source: {html_escape(url)} · Captured {FETCHED_AT}</div><img src="{img_copy.name}"></body></html>"""
    (item_dir / "page.html").write_text(html, encoding="utf-8")
    pdf_path = item_dir / f"{slug}.pdf"
    item["pdf"] = str(pdf_path) if chrome_pdf(item_dir / "page.html", pdf_path) else None

def process_binary(url, resp, item_dir: Path, slug, item):
    (item_dir / "source").mkdir(exist_ok=True)
    name = up.unquote(os.path.basename(up.urlsplit(url).path)) or "file.bin"
    (item_dir / "source" / name).write_bytes(resp.content)
    md_path = item_dir / f"{slug}.md"
    md_path.write_text(front_matter(title=item["title"], section=item["section"], source_url=url, captured=FETCHED_AT, kind="binary", original=f"source/{name}") +
                       f"# {item['title']}\n\nDownloaded binary file: [source/{name}](source/{name}) (content-type: {resp.headers.get('Content-Type')}). No text conversion available.\n")
    item["md"] = str(md_path)
    item["pdf"] = None

# --------------------------------------------------------------------------- driver
def main():
    log(f"== ZHU Training Page archiver → {OUT}")
    for extra in sys.argv[2:]:
        if extra.startswith("--hints="):
            load_wayback_hints(extra.split("=", 1)[1]); log(f"   wayback hints: {len(WAYBACK_HINT)}")
    r, err = fetch(INDEX_URL)
    if r is None:
        sys.exit(f"cannot fetch index: {err}")
    index_html = r.content.decode("iso-8859-1", errors="replace")
    (OUT / "_source").mkdir(exist_ok=True)
    (OUT / "_source" / "ZHU_Training_Page.html").write_bytes(r.content)
    sections = parse_index(index_html)
    log(f"parsed {len(sections)} sections, {sum(len(s['items']) for s in sections)} link items")

    # assign folders
    url_to_local = {}   # normalized url -> item (first occurrence wins)
    all_items = []
    for si, sec in enumerate(sections, 1):
        sec["dir"] = OUT / f"{si:02d}-{slugify(sec['name'], 40)}"
        sec["dir"].mkdir(exist_ok=True)
        used = set()
        for it in sec["items"]:
            n = norm_url(it["url"])
            it["norm"] = n
            if n in url_to_local:
                it["duplicate_of"] = url_to_local[n]["title"]
                it["dir"] = url_to_local[n]["dir"]; it["slug"] = url_to_local[n]["slug"]
                continue
            slug = slugify(it["title"])
            base = slug
            k = 2
            while slug in used:
                slug = f"{base}-{k}"; k += 1
            used.add(slug)
            it["slug"] = slug
            it["dir"] = str(sec["dir"] / slug)
            it["depth"] = 0
            url_to_local[n] = it
            all_items.append(it)

    # crawl
    queue = list(all_items)
    html_items = []
    seen_crawl = set(url_to_local)
    live_hosts = ("waterdata.usgs.gov", "eldoradoweather.com", "ospo.noaa.gov", "nodc.noaa.gov", "tropicaltidbits.com", "spaghettimodels.com", "cpc.ncep.noaa.gov")
    i = 0
    while i < len(queue):
        it = queue[i]; i += 1
        url = it["url"]
        log(f"[{i}/{len(queue)}] {it['section']} :: {it['title']}\n    {url}")
        item_dir = Path(it["dir"]); item_dir.mkdir(parents=True, exist_ok=True)
        it["live"] = any(h in url for h in live_hosts)
        resp, via = load_capture(item_dir, it)
        if resp is not None:
            log(f"    (from local cache, via {via})")
        else:
            res = with_deadline(240, fetch_with_fallback, url)
            resp, via = res if res else (None, "timed out (240 s wall-clock cap)")
        if resp is None:
            it["status"] = "failed"; it["error"] = via
            log(f"    FAILED: {via}")
            (item_dir / f"{it['slug']}.md").write_text(
                front_matter(title=it["title"], section=it["section"], source_url=url, captured=FETCHED_AT, kind="unavailable", error=via) +
                f"# {it['title']}\n\n**Could not be retrieved** at capture time ({FETCHED_AT}).\n\n- Source URL: <{url}>\n- Error: `{via}`\n- Wayback Machine also had no usable snapshot.\n", encoding="utf-8")
            it["md"] = str(item_dir / f"{it['slug']}.md"); it["pdf"] = None
            continue
        it["status"] = "ok"; it["via"] = via
        if via == "wayback":
            it["wayback_url"] = getattr(resp, "wayback_url", None)
        if via == "alternate":
            it["alternate_url"] = getattr(resp, "alternate_url", None)
        it["final_url"] = resp.url
        kind = sniff_kind(url, resp)
        it["kind"] = kind
        try:
            if kind == "html":
                found = []
                process_html_page(url, resp, item_dir, it["slug"], it, found, url_to_local)
                html_items.append(it)
                if is_zhu(it["norm"]):
                    for (n, text) in found:
                        if n in seen_crawl:
                            continue
                        seen_crawl.add(n)
                        # child page lives under parent's folder
                        child_slug = slugify(os.path.splitext(os.path.basename(up.urlsplit(n).path))[0] or text)
                        child = {"title": f"{it['title']} — {text or child_slug}" if text and text.lower() != child_slug else f"{it['title']} — {child_slug}",
                                 "label": text, "primary": it["primary"], "url": n, "norm": n, "section": it["section"],
                                 "slug": child_slug, "dir": str(item_dir / "subpages" / child_slug),
                                 "depth": it.get("depth", 0) + 1, "parent_title": it["title"], "parent": it["norm"]}
                        url_to_local[n] = child
                        queue.append(child)
                        it.setdefault("children", []).append(child)
            elif kind == "pdf":
                process_pdf(url, resp, item_dir, it["slug"], it)
            elif kind == "pptx":
                process_pptx(url, resp, item_dir, it["slug"], it)
            elif kind == "image":
                process_image(url, resp, item_dir, it["slug"], it)
            else:
                process_binary(url, resp, item_dir, it["slug"], it)
            src_dir = item_dir / "source"
            srcs = [f for f in src_dir.iterdir() if f.is_file() and not f.name.startswith(".")] if src_dir.is_dir() else []
            if srcs:
                save_capture(item_dir, it, resp, kind, "source/" + srcs[0].name)
        except Exception as e:  # noqa
            import traceback; traceback.print_exc()
            it["status"] = "error"; it["error"] = f"{type(e).__name__}: {e}"
            log(f"    ERROR processing: {e}")

    log("== finalizing HTML pages (link rewriting, markdown, PDF) …")
    for it in html_items:
        try:
            finalize_html_page(it, url_to_local)
        except Exception as e:  # noqa
            import traceback; traceback.print_exc()
            it["status"] = "error"; it["error"] = f"{type(e).__name__}: {e}"

    # ---------------------------------------------------------------- outputs: manifest, README, report
    def public(it):
        return {k: v for k, v in it.items() if not k.startswith("_") and k not in ("children",)} | {
            "children": [public(c) for c in it.get("children", [])]}
    manifest = {"source": INDEX_URL, "captured": FETCHED_AT, "sections": []}
    for sec in sections:
        manifest["sections"].append({"name": sec["name"], "dir": rel(OUT, sec["dir"]), "notes": sec.get("notes", []),
                                     "items": [public(it) for it in sec["items"]]})
    def relpaths(o):
        if isinstance(o, dict):
            return {k: relpaths(v) for k, v in o.items()}
        if isinstance(o, list):
            return [relpaths(v) for v in o]
        if isinstance(o, str) and o.startswith(str(OUT)):
            return rel(OUT, Path(o))
        return o
    (OUT / "manifest.json").write_text(json.dumps(relpaths(manifest), indent=2), encoding="utf-8")

    # README index
    L = []
    L.append("# ZHU Training Page — Offline Archive\n")
    L.append(f"A complete mirror of the NWS **ZHU (Houston ARTCC) Center Weather Service Unit Training Page** — <{INDEX_URL}> — captured {FETCHED_AT}.\n")
    L.append("Every resource is stored **twice, side by side**: a `.pdf` for people and a `.md` (Markdown with YAML front-matter) for LLMs/agents. "
             "Folders mirror the sections of the original page. Each item folder also keeps the untouched original in `source/`, any images in `assets/`, and (for HTML pages) a browsable `page.html`.\n")
    L.append("> **Attribution (from the original page):** Content for ZHU training page was derived from a myriad of sources (e.g., NWS, academia, private meteorologists). "
             "With the exception of presentations/event write-ups clearly marked, ZHU CWSU takes no credit for content listed. This archive is for personal study; copyrights remain with the original authors.\n")
    L.append("**Machine-readable index:** [`manifest.json`](manifest.json) · **Capture report:** [`REPORT.md`](REPORT.md) · **Original index page:** [`_source/ZHU_Training_Page.html`](_source/ZHU_Training_Page.html)\n")
    L.append("## Contents\n")
    for si, sec in enumerate(sections, 1):
        L.append(f"- [{sec['name']}](#{slugify(sec['name'])}) — {len([x for x in sec['items'] if 'duplicate_of' not in x])} items")
    L.append("")
    def status_mark(it):
        if it.get("status") == "failed": return "❌ unavailable"
        if it.get("status") == "error": return "⚠️ partial"
        if it.get("via") == "wayback": return "🕰 via Wayback"
        if it.get("via") == "alternate": return "🔁 alternate source"
        return ""
    def item_line(it, indent=0):
        pad = "  " * indent
        d = Path(it["dir"])
        md = rel(OUT, d / f"{it['slug']}.md")
        pdf = it.get("pdf") and rel(OUT, Path(it["pdf"]))
        kind = it.get("kind", "?")
        extra = []
        if it.get("pages"): extra.append(f"{it['pages']} pp")
        if it.get("slides"): extra.append(f"{it['slides']} slides")
        if it.get("live"): extra.append("live-data snapshot")
        sm = status_mark(it)
        if sm: extra.append(sm)
        s = f"{pad}- **{it['title']}** — [md]({md})" + (f" · [pdf]({pdf})" if pdf else "") + f" · [source]({it['url']}) `{kind}`" + (f" _( {', '.join(extra)} )_" if extra else "")
        out = [s]
        for c in it.get("children", []):
            out.extend(item_line(c, indent + 1))
        return out
    for si, sec in enumerate(sections, 1):
        L.append(f"## {sec['name']}\n")
        L.append(f"Folder: [`{rel(OUT, sec['dir'])}/`]({rel(OUT, sec['dir'])}/)\n")
        for note in sec.get("notes", []):
            L.append(f"> {note}\n")
        # group by primary
        cur_primary = None
        for it in sec["items"]:
            if "duplicate_of" in it:
                d = url_to_local[it["norm"]]
                L.append(f"- **{it['title']}** — same resource as *{d['title']}* → [md]({rel(OUT, Path(d['dir'])/(d['slug']+'.md'))})")
                continue
            L.extend(item_line(it))
        L.append("")
    L.append("## How to use this archive\n")
    L.append("- **Humans:** open any `.pdf`, or browse `page.html` inside an item folder (internal links between mirrored pages work offline).\n"
             "- **Agents/LLMs:** read `manifest.json` for the full tree with source URLs, kinds, and paths; every `.md` begins with YAML front-matter (`title`, `section`, `source_url`, `kind`, `pdf`, `original`). PDF-derived Markdown is split by `## Page N`; PowerPoint-derived Markdown by `## Slide N`. Where a PDF page had little extractable text, a rendered page image is embedded (`pages/`).\n"
             "- **Scope:** everything linked from the index page (internal *and* external) was captured, and internal ZHU pages were crawled recursively (child pages live in `subpages/`). External sites linked *from* those child pages are kept as ordinary hyperlinks but not archived. Live-data links (buoys, water temps, SST charts) are point-in-time snapshots.\n")
    (OUT / "README.md").write_text("\n".join(L), encoding="utf-8")

    # REPORT
    R = [f"# Capture report — {FETCHED_AT}\n"]
    ok = [x for x in url_to_local.values() if x.get("status") == "ok"]
    failed = [x for x in url_to_local.values() if x.get("status") == "failed"]
    errs = [x for x in url_to_local.values() if x.get("status") == "error"]
    wb = [x for x in ok if x.get("via") == "wayback"]
    alt = [x for x in ok if x.get("via") == "alternate"]
    nopdf = [x for x in ok if not x.get("pdf")]
    R.append(f"- Resources captured: **{len(ok)}** (of {len(url_to_local)} unique URLs; {len(all_items)} top-level, {len(url_to_local)-len(all_items)} discovered by crawling)")
    R.append(f"- Retrieved from the Wayback Machine (original link dead): **{len(wb)}**")
    R.append(f"- Unavailable (dead everywhere): **{len(failed)}**")
    R.append(f"- Processing errors: **{len(errs)}**")
    R.append(f"- Captured but PDF rendering failed: **{len(nopdf)}**\n")
    R.append(f"- Retrieved from an alternate host (original blocked): **{len(alt)}**")
    for title, lst in (("Via Wayback Machine", wb), ("Via alternate source", alt), ("Unavailable", failed), ("Processing errors", errs), ("PDF render failed", nopdf)):
        R.append(f"## {title}\n")
        if not lst: R.append("_none_\n")
        for x in lst:
            R.append(f"- **{x['title']}** ({x['section']}) — <{x['url']}>" + (f" — `{x.get('error')}`" if x.get('error') else "") + (f" — snapshot {x.get('wayback_url')}" if x.get('wayback_url') else "") + (f" — alternate: {x.get('alternate_url')}" if x.get('alternate_url') else ""))
        R.append("")
    R.append("## Full log\n\n```\n" + "\n".join(LOG) + "\n```\n")
    (OUT / "REPORT.md").write_text("\n".join(R), encoding="utf-8")
    log(f"== done. {len(ok)} ok, {len(failed)} failed, {len(errs)} errors, {len(wb)} via wayback")

if __name__ == "__main__":
    main()
