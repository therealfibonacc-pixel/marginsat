"""Switch Margin's analytics and ads on or off, and refresh asset versions.

  python3 tools/configure.py --goatcounter marginsat
  python3 tools/configure.py --adsense-client ca-pub-1234567890123456 --adsense-slot 1234567890
  python3 tools/configure.py --adsense-client "" --adsense-slot ""        # ads off
  python3 tools/configure.py --search-console <token>                      # optional meta-tag verification
  python3 tools/configure.py                                               # only refresh ?v= asset versions

What it touches:
  index.html        cb-cfg (goatcounter, ads), the AdSense <head> tag, the Search Console meta tag
  assets/site.js    the CFG line the landing pages read
  */index.html      the AdSense <head> tag on every landing page
  ads.txt           written when an AdSense client is set, removed when it's cleared
Paper mode loads assets/site.js for visit counts only; it has no ad slot or AdSense tag, so it never gets ads.
"""
import argparse, glob, hashlib, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def wr(p, s):
    open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)


def ver(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:10]


def pages():
    out = ["index.html"]
    for p in sorted(glob.glob(os.path.join(ROOT, "**", "index.html"), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if rel == "index.html" or rel.startswith(("tools/", ".git/")):
            continue
        out.append(rel)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goatcounter")
    ap.add_argument("--adsense-client")
    ap.add_argument("--adsense-slot")
    ap.add_argument("--search-console")
    a = ap.parse_args()

    idx = rd("index.html")
    m = re.search(r'<script type="application/json" id="cb-cfg">(.*?)</script>', idx, re.S)
    cfg = json.loads(m.group(1))
    cfg.setdefault("ads", {"client": "", "slot": ""})
    if a.goatcounter is not None:
        cfg["goatcounter"] = a.goatcounter.strip().lower()
    if a.adsense_client is not None:
        cfg["ads"]["client"] = a.adsense_client.strip()
    if a.adsense_slot is not None:
        cfg["ads"]["slot"] = a.adsense_slot.strip()
    client, slot = cfg["ads"]["client"], cfg["ads"]["slot"]
    if client and not re.fullmatch(r"ca-pub-\d{10,20}", client):
        raise SystemExit("AdSense client should look like ca-pub-1234567890123456")
    if slot and not re.fullmatch(r"\d{5,14}", slot):
        raise SystemExit("AdSense slot should be the ad unit's number, like 1234567890")
    idx = idx[:m.start(1)] + json.dumps(cfg) + idx[m.end(1):]
    wr("index.html", idx)

    js = rd("assets/site.js")
    js = re.sub(r"^var CFG = .*;$", "var CFG = " + json.dumps({"goatcounter": cfg.get("goatcounter", ""), "ads": cfg["ads"]}) + ";", js, count=1, flags=re.M)
    wr("assets/site.js", js)

    tag = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + client + '" crossorigin="anonymous"></script>') if client else ""
    for p in pages():
        s = rd(p)
        s = re.sub(r"<!--adsense-->.*?<!--/adsense-->", "<!--adsense-->" + tag + "<!--/adsense-->", s, flags=re.S)
        if p == "index.html" and a.search_console is not None:
            t = a.search_console.strip()
            meta = ('<meta name="google-site-verification" content="' + t + '">') if t else ""
            s = re.sub(r"<!--gsv-->.*?<!--/gsv-->", "<!--gsv-->" + meta + "<!--/gsv-->", s, flags=re.S)
        # cache-busting versions for shared assets
        s = re.sub(r'((?:/)?assets/(app\.css|katex\.css|site\.css|site\.js))\?v=[0-9a-f]+', lambda mm: mm.group(1) + "?v=" + ver("assets/" + mm.group(2)), s)
        wr(p, s)

    ads_txt = os.path.join(ROOT, "ads.txt")
    if client:
        wr("ads.txt", "google.com, " + client.replace("ca-", "") + ", DIRECT, f08c47fec0942fa0\n")
    elif os.path.exists(ads_txt):
        os.remove(ads_txt)
    print("goatcounter:", cfg.get("goatcounter") or "off", "| ads:", (client + " / " + slot) if client and slot else ("client only (approval)" if client else "off"))


if __name__ == "__main__":
    main()
