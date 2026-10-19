"""Build Margin's landing pages for search engines, plus sitemap.xml.

These are plain HTML pages (no app, no test data) that describe what Margin has and link into the app:
  /sat-practice-tests/            the five full tests, their format and two sample questions
  /sat-question-bank/             the 628-question bank: tiers, skills, four sample questions
  /sat-math-concepts/             the 26 concept drills, by domain
  /sat-math-concepts/<id>/        one page per drill: key idea, trap, Desmos note, three worked examples
  /sat-guide/                     how the tests are made (copied from the in-app guide, tools/content/guide.html)
  /about/  /privacy/

Run from anywhere:  python3 tools/build_pages.py
It reads index.html (concept list and bank index), bank/, data/tests.*.json and tools/content/.
"""
import datetime, glob, hashlib, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://marginsat.com"
TODAY = datetime.date.today().isoformat()
E = html.escape


def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def wr(p, s):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(s)


def ver(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()[:10]


INDEX = rd("index.html")
BANKMETA = json.loads(re.search(r'<script type="application/json" id="cb-bank">(.*?)</script>', INDEX, re.S).group(1))
CONCEPTS = BANKMETA["concepts"]
BANK = json.loads(rd("bank/bank.json"))
DATA = json.loads(rd(sorted(glob.glob(os.path.join(ROOT, "data", "tests.*.json")))[0]))
DOMS = ["Algebra", "Advanced Math", "Problem-Solving and Data Analysis", "Geometry and Trigonometry"]
LEVELS = {1: "Level 1 · Warm-up", 2: "Level 2 · Test level", 3: "Level 3 · Beyond the test"}
TIERS = {1: "Hard", 2: "Harder", 3: "Hardest", 4: "Extreme"}

WORDMARK = '<span class="wordmark" aria-hidden="true">Marg<span class="wi">\u0131<span class="o"></span></span>n</span>'
NAV = [("/sat-practice-tests/", "Practice tests"), ("/sat-question-bank/", "Question bank"),
       ("/sat-math-concepts/", "Concepts"), ("/paper/", "Paper"), ("/sat-guide/", "Guide")]

SEO_TITLE = {
    "no-solution": "No Solution or Infinitely Many Solutions",
    "system-constants": "Systems of Equations With a Missing Constant",
    "systems-in-words": "Systems of Equations Word Problems",
    "inequalities-in-context": "Linear Inequality Word Problems",
    "discriminant": "The Discriminant and Number of Solutions",
    "vertex": "Vertex Form, Maximum and Minimum",
    "sum-product": "Sum and Product of Roots",
    "exponential": "Exponential Growth and Decay",
    "exponent-rules": "Exponent Rules and Radicals",
    "remainder": "Remainder and Factor Theorem",
    "transformations": "Graph Transformations: Shifts and Stretches",
    "extraneous": "Radical and Rational Equations",
    "percent-change": "Percent Change, Chained and Reversed",
    "unit-conversion": "Rates and Unit Conversion",
    "mixtures": "Mixture and Concentration Problems",
    "work-rates": "Work Rate Problems",
    "mean-median": "Mean and Median Problems",
    "conditional-probability": "Conditional Probability From Tables",
    "ratios": "Ratios and Proportions",
    "circle-equations": "Circle Equations and Completing the Square",
    "arcs-sectors": "Arc Length, Sector Area and Radians",
    "similar-figures": "Similar Figures and Scale Factors",
    "right-triangle-trig": "Right Triangle Trigonometry",
    "special-right-triangles": "Special Right Triangles (45-45-90, 30-60-90)",
    "volume": "Volume and Surface Area",
    "angles-polygons": "Angles, Parallel Lines and Polygons",
}


def textish(s):
    """Fields like the trap or Desmos note are plain text unless they carry KaTeX or tags."""
    return s if "<" in s else E(s)


def plain(s):
    """Visible text of an HTML fragment, for meta descriptions."""
    s = re.sub(r'<span class="katex-mathml">.*?</span>', "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def clip(s, n=158):
    s = plain(s)
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


# ------------------------------------------------------------------ page shell
def page(path, title, desc, h1, lead, body, crumbs=(), side="", hero_btns="", katex=False, ld=None, og_title=None, nav_on=None):
    url = SITE + path
    crumb_ld = [{"@type": "ListItem", "position": 1, "name": "Margin", "item": SITE + "/"}]
    for i, (name, href) in enumerate(crumbs, 2):
        crumb_ld.append({"@type": "ListItem", "position": i, "name": name, "item": SITE + href})
    crumb_ld.append({"@type": "ListItem", "position": len(crumb_ld) + 1, "name": h1})
    graph = [{"@type": "BreadcrumbList", "itemListElement": crumb_ld},
             {"@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc, "inLanguage": "en",
              "isPartOf": {"@id": SITE + "/#website"}}]
    if ld:
        graph.extend(ld)
    eyebrow = ""
    if crumbs:
        eyebrow = '<nav class="eyebrow" aria-label="Breadcrumb"><a href="/">Margin</a>' + "".join(
            '<span aria-hidden="true">/</span><a href="' + href + '">' + E(name) + "</a>" for name, href in crumbs) + "</nav>"
    nav = "".join('<a href="' + h + '"' + (' aria-current="page"' if h == nav_on else "") + ">" + n + "</a>" for h, n in NAV)
    css = '<link rel="stylesheet" href="/assets/app.css?v=' + ver("assets/app.css") + '">\n'
    if katex:
        css += '<link rel="stylesheet" href="/assets/katex.css?v=' + ver("assets/katex.css") + '">\n'
    css += '<link rel="stylesheet" href="/assets/site.css?v=' + ver("assets/site.css") + '">'
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<script>if(location.protocol==="http:"&&location.hostname.endsWith("marginsat.com"))location.replace("https://"+location.host+location.pathname+location.search+location.hash)</script>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Margin">
<meta property="og:title" content="{E(og_title or title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1F1C1A">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Geist:wght@300..700&family=Noto+Serif:ital,wght@0,400;0,700;1,400&display=swap">
{css}
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)}</script>
<!--adsense--><!--/adsense-->
</head>
<body class="static">
<div class="shell"><div class="topbar" id="topbar"><div class="bar"><a class="brand" href="/" aria-label="Margin home">{WORDMARK}</a><nav class="nav" aria-label="Main">{nav}</nav><a class="btn primary sm" href="/">Open Margin</a></div></div>
<header class="band"><div class="halo" aria-hidden="true"></div><div class="hero wrap"><div class="hello">{eyebrow}<h1 class="title">{h1}</h1>{('<p class="lead">' + lead + "</p>") if lead else ""}{hero_btns}</div>{side}</div></header>
<main class="main wrap" id="main">
{body}
</main></div>
<div id="extras"><aside id="ad-host" class="adhost wrap" aria-label="Advertisement" hidden></aside><div id="site-foot">{FOOTER}</div></div>
<script src="/assets/site.js?v={ver("assets/site.js")}" defer></script>
</body></html>
"""


FOOTER = ('<footer class="foot wrap"><a class="brand sm" href="/" aria-label="Margin home">' + WORDMARK + '</a>'
          '<p>Independent SAT practice by Lamai Hons. Not affiliated with College Board.</p>'
          '<nav aria-label="Footer"><a href="/#bank">Question bank</a><a href="/#concepts">Concept drills</a><a href="/#guide">Guide</a>'
          '<a href="/paper/">Paper mode</a><a href="/the-art-of-solving-problems.pdf">Problem-solving guide</a><a href="/#tutoring">Tutoring</a></nav>'
          '<nav class="foot-2" aria-label="Guides"><a href="/sat-practice-tests/">Free SAT practice tests</a><a href="/sat-question-bank/">Hard SAT questions</a>'
          '<a href="/sat-math-concepts/">SAT Math concepts</a><a href="/sat-guide/">How the tests are made</a><a href="/about/">About</a><a href="/privacy/">Privacy</a></nav></footer>')


def sheet(inner, cls="", h2=None, more=None, id_=None):
    head = ""
    if h2:
        head = '<header class="sh"><h2>' + h2 + "</h2>" + (more or "") + "</header>"
    return '<section class="sheet' + (" " + cls if cls else "") + '"' + (' id="' + id_ + '"' if id_ else "") + ">" + head + inner + "</section>\n"


def cta(h, p, btn_href, btn_label, second=None):
    btns = '<a class="btn primary" href="' + btn_href + '">' + btn_label + "</a>"
    if second:
        btns += '<a class="btn" href="' + second[0] + '">' + second[1] + "</a>"
    return sheet('<div class="cta"><div><h2>' + h + "</h2><p>" + p + '</p></div><div class="row">' + btns + "</div></div>")


def side(pairs):
    return '<div class="hside">' + "".join("<div><b>" + a + "</b><span>" + b + "</span></div>" for a, b in pairs) + "</div>"


def example(q, label, lv_dots=None, src=None):
    dots = ""
    if lv_dots:
        dots = "<i aria-hidden=\"true\">" + "".join('<b class="on"></b>' if i <= lv_dots else "<b></b>" for i in (1, 2, 3)) + "</i>"
    psg = ""
    if q.get("passage"):
        psg = '<div class="ex-psg">' + q["passage"] + "</div>"
    ch = ""
    if q.get("choices"):
        ch = '<ol class="ex-ch">' + "".join("<li><b>" + "ABCD"[i] + "</b><span>" + c + "</span></li>" for i, c in enumerate(q["choices"])) + "</ol>"
    ans = q["answer"]
    if q.get("choices") and ans in "ABCD" and len(ans) == 1:
        ans_txt = "Answer: " + ans
    else:
        ans_txt = "Answer: " + E(str(ans))
    return ('<div class="ex"><p class="ex-lv">' + dots + E(label) + "</p>" + psg + '<div class="ex-stem">' + q["stem"] + "</div>" + ch +
            '<details><summary>Show the answer</summary><div class="ex-ans"><span class="ok">' + ans_txt + "</span>" + q["explain"] + "</div></details>" +
            ('<p class="ex-src">' + src + "</p>" if src else "") + "</div>")


# ------------------------------------------------------------------ concept pages
def concept_pages():
    out = []
    by_dom = {d: [c for c in CONCEPTS if c["dom"] == d] for d in DOMS}
    for c in CONCEPTS:
        D = json.load(open(os.path.join(ROOT, "bank", "concepts", c["id"] + ".json"), encoding="utf-8"))
        path = "/sat-math-concepts/" + c["id"] + "/"
        st = SEO_TITLE.get(c["id"], c["name"])
        title = st + " | SAT Math Practice"
        if len(title) > 70:
            title = st + " | SAT Math"
        desc = clip(c["short"] + " Learn the key idea and the trap, then practice 36 free SAT questions in three levels with worked explanations.", 165)
        exs = []
        for lv in (1, 2, 3):
            items = [it for it in D["items"] if it["lv"] == lv]
            pick = next((it for it in items if it.get("choices")), None) if lv == 2 else None
            exs.append(example(pick or items[0], LEVELS[lv], lv_dots=lv))
        primer = ('<article class="sheet doc">'
                  "<h2>The key idea</h2><div class=\"lede\">" + D["idea"] + "</div>"
                  "<h2>The trap</h2><p>" + textish(D["trap"]) + "</p>"
                  "<h2>Can Desmos do it?</h2><p>" + textish(D["desmos"]) + "</p>"
                  '<p class="fine">College Board skill: ' + E(c["skill"]) + " · " + E(c["dom"]) + "</p></article>\n")
        examples = sheet('<p class="fine" style="margin:-6px 0 14px">One question from each level. The drill has 12 at every level, and moves you up after four right in a row.</p><div class="exs">' + "".join(exs) + "</div>",
                         h2="Try one at each level")
        sib = [x for x in by_dom[c["dom"]] if x["id"] != c["id"]]
        rel = sheet('<div class="cn-grid">' + "".join(
            '<a class="cn-card" href="/sat-math-concepts/' + x["id"] + '/"><span class="cn-t"><b>' + E(x["name"]) + '</b></span><span class="cn-s">' + E(x["short"]) +
            '</span><span class="cn-m">36 questions, 3 levels</span></a>' for x in sib) + "</div>",
            h2="More " + E(c["dom"]) + " concepts", more='<a class="more" href="/sat-math-concepts/">All 26 concepts</a>')
        body = primer + examples + cta("Practice all 36 questions", "Answer in the drill to get instant feedback, climb the levels, and feed your misses into Tailored practice. Free, no account.",
                                       "/#concept/" + c["id"], "Start the drill", ("/sat-math-concepts/", "All concepts")) + rel
        quiz_ld = {"@type": "LearningResource", "name": c["name"], "learningResourceType": "Practice problems",
                   "educationalLevel": "High school", "teaches": c["skill"], "about": "SAT Math: " + c["dom"],
                   "url": SITE + path, "isAccessibleForFree": True, "inLanguage": "en"}
        wr(path.strip("/") + "/index.html",
           page(path, title, desc, E(c["name"]), E(c["short"]), body,
                crumbs=[("SAT Math concepts", "/sat-math-concepts/"), (c["dom"], "/sat-math-concepts/#" + slug(c["dom"]))],
                side=side([("36", "practice questions"), ("3", "levels")]), katex=True, ld=[quiz_ld], nav_on="/sat-math-concepts/"))
        out.append(path)
    # hub
    secs = ""
    for d in DOMS:
        lst = by_dom[d]
        secs += sheet('<div class="cn-grid">' + "".join(
            '<a class="cn-card" href="/sat-math-concepts/' + x["id"] + '/"><span class="cn-t"><b>' + E(x["name"]) + '</b></span><span class="cn-s">' + E(x["short"]) +
            '</span><span class="cn-m">36 questions, 3 levels</span></a>' for x in lst) + "</div>",
            h2=E(d), more='<span class="fine">' + str(len(lst)) + " concepts</span>", id_=slug(d))
    intro = sheet('<div class="doc" style="padding:0"><p>Some missed SAT Math questions come down to one idea you haven’t nailed yet: mixture problems, work rates, the discriminant, completing the square for a circle. '
                  "Each page below teaches one of those ideas: the key idea in a few lines, the trap that catches most students, and what Desmos can and can’t do for that kind of question. "
                  "Then you practice it in three levels: a warm-up, test level, and beyond the test.</p>"
                  "<p>The drill questions are generated from templates with exact arithmetic, so every answer is right by construction, and each explanation works through the steps.</p></div>")
    body = intro + secs + cta("Want a mix instead?", "Tailored practice in the question bank builds sets from the skills you miss most, across all of Math and Reading and Writing.", "/#bank", "Open the question bank")
    path = "/sat-math-concepts/"
    item_ld = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + "/sat-math-concepts/" + c["id"] + "/", "name": c["name"]} for i, c in enumerate(CONCEPTS)]}
    wr("sat-math-concepts/index.html",
       page(path, "SAT Math Concept Drills: 26 Topics, 936 Free Practice Questions", clip("Free SAT Math practice by topic: 26 concepts from systems and the discriminant to circle equations and work rates. Each has a short lesson, the common trap, and 36 practice questions in three levels.", 165),
            "SAT Math concept drills", "Practice one idea at a time, from mixtures and rates to circle equations. Each concept starts with the key idea and the trap, then climbs three levels.",
            body, side=side([("26", "concepts"), ("936", "practice questions")]), ld=[item_ld], nav_on=path,
            hero_btns='<div class="row"><a class="btn primary" href="/#concepts">Start practicing</a></div>'))
    out.insert(0, path)
    return out


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ------------------------------------------------------------------ practice tests
def tests_page():
    meta = DATA["meta"]
    mods = [("Reading and Writing", "Module 1", 27, 32), ("Reading and Writing", "Module 2", 27, 32), ("Break", "", None, 10),
            ("Math", "Module 1", 22, 35), ("Math", "Module 2", 22, 35)]
    rows = "".join("<tr><th scope=\"row\">" + a + (" · " + b if b else "") + "</th><td>" + (str(n) if n else "") + "</td><td>" + str(m) + " min</td></tr>" for a, b, n, m in mods)
    fmt = ('<div class="tablewrap"><table class="kv"><thead><tr><th class="l">Part</th><th>Questions</th><th>Time</th></tr></thead><tbody>' + rows +
           "</tbody><tfoot><tr><th scope=\"row\">Total</th><td>98</td><td>2 h 14 min</td></tr></tfoot></table></div>")
    tl = "".join('<div class="trow"><div><span class="tn">Practice Test ' + t + '</span><span class="tm">98 questions · 2 h 14 min · every answer explained</span></div>'
                 '<div class="row"><a class="btn sm" href="/#start-' + t + '">Start</a><a class="btn sm quiet" href="/tests/margin-sat-test-' + t + '.pdf">PDF</a></div></div>' for t in "12345")
    tests = sheet('<div class="tlist">' + tl + "</div>", cls="st-tests", h2="The five tests", more='<a class="more" href="/paper/">Take one on paper</a>')

    def pct(t, dom, rw):
        n = c = 0
        for k in (["RW1", "RW2"] if rw else ["M1", "M2"]):
            n += meta[t][k]["n"]; c += meta[t][k]["domains"].get(dom, 0)
        return round(100 * c / n)
    CB_RW = [("Craft and Structure", 28), ("Information and Ideas", 26), ("Standard English Conventions", 26), ("Expression of Ideas", 20)]
    CB_M = [("Algebra", 35), ("Advanced Math", 35), ("Problem-Solving and Data Analysis", 15), ("Geometry and Trigonometry", 15)]

    def mrows(lst, rw):
        r = ""
        for dom, cb in lst:
            v = [pct(t, dom, rw) for t in "12345"]
            r += '<tr><th scope="row">' + dom + "</th><td>" + str(cb) + "%</td><td>" + (str(min(v)) if min(v) == max(v) else str(min(v)) + "–" + str(max(v))) + "%</td></tr>"
        return r
    mix = ('<div class="tablewrap"><table class="kv"><thead><tr><th class="l">Domain</th><th>College Board target</th><th>Margin tests</th></tr></thead><tbody>'
           '<tr class="grp"><th colspan="3">Reading and Writing</th></tr>' + mrows(CB_RW, True) + '<tr class="grp"><th colspan="3">Math</th></tr>' + mrows(CB_M, False) + "</tbody></table></div>")
    built = sheet('<ul class="ticks">'
                  "<li><b>The real structure.</b> Two Reading and Writing modules of 27 questions in 32 minutes each, a 10-minute break, then two Math modules of 22 questions in 35 minutes each.</li>"
                  "<li><b>A Bluebook-style screen.</b> The timer, Mark for Review, answer eliminator, highlighter, reference sheet and a built-in graphing calculator work the way they do on test day.</li>"
                  "<li><b>The harder Module 2, every time.</b> On the real test a strong Module 1 sends you to a harder Module 2. Margin always gives you that one, because it’s the only route to a top score.</li>"
                  "<li><b>Written from scratch.</b> Every passage, data set and problem is original, tagged with College Board’s own domain and skill names, and checked by solving it again from scratch.</li>"
                  "<li><b>A full report.</b> An estimated score from 400 to 1600, your time on every question, the misses you never marked, and a Redo bank that brings your misses back.</li>"
                  "</ul>", h2="Built like the real test")
    fmt_s = sheet(fmt + '<p class="fine" style="margin-top:12px">Single modules can be taken on their own as drills, with their real time limits.</p>', h2="What’s in each test")
    mix_s = sheet('<p class="fine" style="margin:-6px 0 6px">Share of questions by content domain, compared with College Board’s published targets for the digital SAT.</p>' + mix, h2="How the mix compares")
    # samples: one RW and one Math question from Test 1, module 2
    rw = next(q for q in DATA["free"]["1"]["RW2"] if q["domain"] == "Information and Ideas" and q.get("passage") and "<table" not in q.get("passage", "") and "<img" not in q.get("passage", ""))
    m = next(q for q in DATA["free"]["1"]["M2"] if q.get("choices") and "<img" not in q["stem"] and "<svg" not in q["stem"] and q["domain"] == "Advanced Math")
    samples = sheet('<div class="exs">' + example(rw, "Reading and Writing · " + rw["skill"], src="Practice Test 1, Module 2, Question " + str(rw["n"])) +
                    example(m, "Math · " + m["skill"], src="Practice Test 1, Module 2, Question " + str(m["n"])) + "</div>", h2="Two sample questions")
    faq = sheet('<div class="doc" style="padding:0">'
                "<h3>Are the tests really free?</h3><p>Yes. All five tests, their PDFs and every explanation are free, with no account and no sign-up.</p>"
                "<h3>Where is my progress saved?</h3><p>In your browser on the device you use. Nothing is sent to a server, so clearing your browser data clears your history.</p>"
                "<h3>How accurate is the score?</h3><p>Each full test gets an estimated score made by converting your raw score in each section with a fixed table. College Board scores the real test with a statistical model nobody outside College Board can reproduce, so treat it as a close estimate.</p>"
                "<h3>Can I take them on paper?</h3><p>Every test comes as a PDF laid out like a paper booklet, with an answer sheet and explanations. <a href=\"/paper/\">Paper mode</a> lets you write on it in the browser and time each module.</p>"
                "</div>", h2="Questions")
    body = tests + fmt_s + built + samples + mix_s + faq + cta("Ready for Test 1?", "Set aside 2 hours and 14 minutes, or start with a single module.", "/#start-1", "Start Test 1", ("/", "See all options"))
    path = "/sat-practice-tests/"
    wr("sat-practice-tests/index.html",
       page(path, "Free Full-Length SAT Practice Tests (Digital SAT, Bluebook-Style)", clip("Five free full-length digital SAT practice tests in a Bluebook-style screen, with the real timing, a graphing calculator, an estimated score and every answer explained. No sign-up.", 165),
            "Free full-length SAT practice tests", "Five complete digital SAT practice tests in a screen that works like Bluebook, with every answer explained. No account, no sign-up.",
            body, side=side([("5", "full tests"), ("490", "questions")]), katex=True, nav_on=path,
            hero_btns='<div class="row"><a class="btn primary" href="/#start-1">Start Test 1</a><a class="btn" href="/paper/">Take one on paper</a></div>'))
    return [path]


# ------------------------------------------------------------------ question bank
def bank_page():
    idx = BANKMETA["index"]
    rwn = sum(1 for q in idx if q["sec"] == "rw"); mn = len(idx) - rwn
    tiers = {t: sum(1 for q in idx if q["t"] == t) for t in TIERS}
    def split(t):
        r = sum(1 for q in idx if q["t"] == t and q["sec"] == "rw"); m = tiers[t] - r
        if t == 4:
            return "Math only. Past anything on the real test, on purpose."
        return str(r) + " Reading and Writing, " + str(m) + " Math"
    tiers_html = '<div class="tiers">' + "".join("<div><b>" + str(tiers[t]) + "</b><span>" + TIERS[t] + "</span><small>" + split(t) + "</small></div>" for t in TIERS) + "</div>"
    sk = BANKMETA["skills"]
    cnt = {}
    for q in idx:
        cnt[q["s"]] = cnt.get(q["s"], 0) + 1
    rows = ""
    for sec, label in (("rw", "Reading and Writing"), ("math", "Math")):
        rows += '<tr class="grp"><th colspan="2">' + label + "</th></tr>"
        for dom, skills in sk[sec].items():
            for s in skills:
                n = cnt.get(s, 0)
                rows += '<tr><th scope="row">' + E(s) + ' <span class="fine">· ' + E(dom) + "</span></th><td>" + str(n) + "</td></tr>"
    skills_tbl = '<div class="tablewrap"><table class="kv"><thead><tr><th class="l">Skill</th><th>Questions</th></tr></thead><tbody>' + rows + "</tbody></table></div>"
    # samples: two RW (Hardest), two Math (Hardest, Extreme), no figures
    def ok(q):
        return not q.get("figure") and "<img" not in q["stem"] and "<svg" not in q["stem"]
    picks = [next(q for q in BANK.values() if q["sec"] == "rw" and q["tier"] == 3 and ok(q) and q["skill"] == "Inferences"),
             next(q for q in BANK.values() if q["sec"] == "rw" and q["tier"] == 3 and ok(q) and q["skill"] == "Transitions"),
             next(q for q in BANK.values() if q["sec"] == "math" and q["tier"] == 3 and ok(q) and q["domain"] == "Advanced Math" and q.get("choices")),
             next(q for q in BANK.values() if q["sec"] == "math" and q["tier"] == 4 and ok(q))]
    samples = sheet('<div class="exs">' + "".join(example(q, ("Reading and Writing" if q["sec"] == "rw" else "Math") + " · " + q["skill"] + " · " + TIERS[q["tier"]],
                                                          src='Bank question <a href="/#bank/' + q["id"] + '">' + q["id"] + "</a>") for q in picks) + "</div>", h2="Four sample questions")
    about = sheet('<div class="doc" style="padding:0">'
                  "<p>The bank holds " + str(len(idx)) + " questions written to be harder than the five tests: " + str(rwn) + " in Reading and Writing and " + str(mn) + " in Math, spread across all 30 of College Board’s skills. None of them appear in the tests.</p>"
                  "<h3>Built to beat the calculator</h3><p>Desmos is allowed on the whole Math section, and it can solve any equation you can type in. So the bank’s Math questions are written so that typing it in isn’t enough: the equation has an unknown constant, the answer is an expression or a count, the graph only exists after a word problem is set up, or the figure has no coordinates at all.</p>"
                  "<h3>Every trap named</h3><p>Wrong answers are built from the mistakes strong students actually make: an answer true to one sentence but not another, the right idea in the wrong direction, a percent taken of the wrong base, or stopping one step early. Every explanation says which trap each wrong answer sets.</p>"
                  "<h3>Tailored practice</h3><p>Margin keeps a running estimate of how likely you are to get a hard question right in each skill, from every answer you give. Tailored sets weigh each skill by how often it shows up on the real test and how often you miss it, pitch questions just past comfortable, mix skills, and bring missed questions back a day later, then 3, 7 and 16 days after each right answer.</p>"
                  '<p><a href="/sat-guide/#g-bank">How the bank and Tailored practice work, with sources</a></p></div>', h2="What makes it different")
    body = sheet(tiers_html, h2="Four levels of hard") + about + samples + sheet(skills_tbl, h2="Every skill on the test") + cta(
        "Start with a Tailored set", "It works from your first answer and gets sharper with every set. Free, no account.", "/#bank", "Open the question bank")
    path = "/sat-question-bank/"
    wr("sat-question-bank/index.html",
       page(path, "Hard SAT Practice Questions: 628-Question Bank With Explanations", clip("628 original SAT questions written to be harder than the real test, across all 30 College Board skills, with every trap explained and Tailored practice built from your misses. Free.", 165),
            "Hard SAT practice questions", "A bank of " + str(len(idx)) + " original questions written to be harder than the test, with every trap explained. Tailored practice aims each set at your misses.",
            body, side=side([(str(len(idx)), "questions"), ("30", "College Board skills")]), katex=True, nav_on=path,
            hero_btns='<div class="row"><a class="btn primary" href="/#bank">Open the question bank</a></div>'))
    return [path]


# ------------------------------------------------------------------ guide
def guide_page():
    g = rd("tools/content/guide.html")
    g = re.sub(r'\s*data-rise="[^"]*"', "", g)
    g = re.sub(r'\s*style="--i:\d+"', "", g)
    g = re.sub(r'\s*data-act="jump"', "", g)
    g = g.replace('href="#bank"', 'href="/#bank"').replace('href="#concepts"', 'href="/#concepts"').replace('href="paper/"', 'href="/paper/"')
    g = g.replace('href="the-art-of-solving-problems.pdf"', 'href="/the-art-of-solving-problems.pdf"')
    path = "/sat-guide/"
    wr("sat-guide/index.html",
       page(path, "How Margin’s Free SAT Practice Tests Are Made", clip("How Margin builds its digital SAT practice tests and hard question bank: College Board’s blueprint, domain mix, Desmos-proof Math, Tailored practice, scoring and paper mode.", 165),
            "How the tests are made", "How the tests are built, how drills work, and how to think on test day.", g, nav_on=path))
    return [path]


# ------------------------------------------------------------------ about and privacy
def about_page():
    body = sheet('<div class="doc legal" style="padding:0">'
                 "<p>Margin is free SAT practice made by Lamai Hons. "
                 "It started as the practice he wanted for himself: tests that feel like Bluebook, questions harder than the real thing, and explanations that name the trap instead of just giving the answer.</p>"
                 "<h3>What’s here</h3><ul><li><a href=\"/sat-practice-tests/\">Five full-length practice tests</a> in a Bluebook-style screen, plus PDFs for <a href=\"/paper/\">paper mode</a>.</li>"
                 "<li>A <a href=\"/sat-question-bank/\">bank of 628 hard questions</a> with Tailored practice built from your misses.</li>"
                 "<li><a href=\"/sat-math-concepts/\">26 SAT Math concept drills</a>, one idea at a time.</li>"
                 "<li><a href=\"/the-art-of-solving-problems.pdf\">The Art of Solving Problems</a>, a guide to how top scorers read, plan, choose and check.</li></ul>"
                 "<h3>How it’s made</h3><p>Every test and bank question is written from scratch and tagged with College Board’s own skill names. Math answers are checked by solving each question again independently, and every Reading and Writing question is reread to make sure exactly one answer holds up. "
                 "<a href=\"/sat-guide/\">The guide</a> explains the details.</p>"
                 "<h3>Why it’s free</h3><p>Margin has no accounts and no paywall. Your progress stays in your own browser. Ads, when they appear, help pay for the domain so the tests can stay free.</p>"
                 "<h3>Tutoring</h3><p>Lamai also offers <a href=\"/#tutoring\">1:1 SAT tutoring</a>, and the first session is free.</p>"
                 "<h3>Not affiliated with College Board</h3><p>Margin is independent. It isn’t affiliated with or endorsed by College Board, which owns the SAT and Bluebook trademarks.</p>"
                 "</div>")
    path = "/about/"
    person = {"@type": "AboutPage", "url": SITE + path, "mainEntity": {"@id": SITE + "/#org"}}
    wr("about/index.html", page(path, "About Margin", "Margin is free, independent SAT practice made by Lamai Hons: five Bluebook-style tests, a bank of 628 hard questions, and 26 SAT Math concept drills.",
                                "About Margin", "Free, independent SAT practice for the digital SAT.", body, ld=[person]))
    return [path]


def privacy_page():
    body = sheet('<div class="doc legal" style="padding:0">'
                 '<p class="updated">Last updated ' + datetime.date.today().strftime("%B %-d, %Y") + "</p>"
                 "<p>Margin (marginsat.com) is a free SAT practice site with no accounts. This page explains what happens to information when you use it.</p>"
                 "<h3>Your practice data stays in your browser</h3><p>Your answers, scores, highlights, notes, the name you type in, and your settings are saved in your browser’s local storage on your device. "
                 "They aren’t sent to Margin or anyone else. Clearing your browser data, or using a different browser or device, starts you fresh. PDFs you open in paper mode are read in your browser and never uploaded.</p>"
                 "<h3>Visit counts</h3><p>Margin counts visits with GoatCounter, a privacy-friendly analytics service. It records which pages are visited, the referring site, and general details like browser, screen size and country. "
                 "It doesn’t use cookies, doesn’t store your IP address, and doesn’t track you across sites. It also counts when a practice test is started or finished, without recording any answers. "
                 'See <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter’s privacy policy</a>.</p>'
                 "<h3>Advertising</h3><p>Margin may show ads from Google AdSense. Third-party vendors, including Google, use cookies to serve ads based on a person’s prior visits to this website or other websites. "
                 "Google’s use of advertising cookies enables it and its partners to serve ads to people based on their visit to this site and/or other sites on the Internet. "
                 'You can opt out of personalized advertising by visiting <a href="https://adssettings.google.com" rel="noopener">Google’s Ads Settings</a>, and you can learn how Google uses information from sites that use its services at '
                 '<a href="https://policies.google.com/technologies/partner-sites" rel="noopener">policies.google.com/technologies/partner-sites</a>. '
                 'You can also opt out of some third-party vendors’ use of cookies for personalized advertising at <a href="https://www.aboutads.info/choices/" rel="noopener">aboutads.info</a>. '
                 "Visitors in the European Economic Area, the UK and Switzerland are asked for consent before personalized ads are shown.</p>"
                 "<h3>Other services</h3><p>Pages load fonts from Google Fonts, which receives your IP address to deliver them. If the Desmos calculator is turned on, it loads from desmos.com. Links to other sites are covered by those sites’ own policies.</p>"
                 "<h3>Children</h3><p>Margin is meant for high school students preparing for the SAT and isn’t directed to children under 13. Margin doesn’t knowingly collect personal information from anyone.</p>"
                 "<h3>Changes</h3><p>If this policy changes, the new version will be posted here with a new date.</p>"
                 "</div>")
    path = "/privacy/"
    wr("privacy/index.html", page(path, "Privacy Policy | Margin", "How Margin handles information: practice data stays in your browser, cookie-free visit counts with GoatCounter, and Google AdSense advertising.",
                                  "Privacy policy", "Margin has no accounts. Your practice stays in your browser.", body))
    return [path]


# ------------------------------------------------------------------ sitemap
def sitemap(paths):
    urls = ["/", "/paper/"] + paths
    pri = {"/": "1.0", "/sat-practice-tests/": "0.9", "/sat-question-bank/": "0.9", "/sat-math-concepts/": "0.8", "/paper/": "0.7"}
    body = "".join("<url><loc>" + SITE + u + "</loc><lastmod>" + TODAY + "</lastmod>" + ("<priority>" + pri[u] + "</priority>" if u in pri else "") + "</url>\n" for u in urls)
    wr("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n' + body + "</urlset>\n")
    return urls


if __name__ == "__main__":
    paths = tests_page() + bank_page() + concept_pages() + guide_page() + about_page() + privacy_page()
    urls = sitemap(paths)
    print("built", len(paths), "pages;", len(urls), "URLs in sitemap.xml")
