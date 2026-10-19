"""Copy the rendered home page into index.html so it shows before the test data loads.

The app renders into #app with JavaScript, after data/tests.*.json arrives. This script opens the site in a
headless browser as a first-time visitor, copies what the home page renders (and the footer), and writes it
between the <!--pre--> and <!--prefoot--> markers. Search engines and first-time visitors then see the home
page in the HTML itself; the app replaces it with identical markup when it starts.

Run after any change to the home page:  python3 tools/prerender.py
Needs Playwright with Chromium (pip install playwright; python3 -m playwright install chromium).
"""
import asyncio, functools, http.server, os, re, socketserver, threading
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    handler.log_message = lambda *a: None
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def strip_pre(html):
    html = re.sub(r"<!--pre-->.*?<!--/pre-->", "<!--pre--><!--/pre-->", html, flags=re.S)
    return re.sub(r"<!--prefoot-->.*?<!--/prefoot-->", "<!--prefoot--><!--/prefoot-->", html, flags=re.S)


async def capture(url):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1366, "height": 900})
        pg = await ctx.new_page()
        await pg.route(re.compile(r"https://(gc\.zgo\.at|pagead2\.googlesyndication\.com)/.*"), lambda r: r.abort())
        await pg.goto(url, wait_until="load")
        # copy right after the first render, before the hero demo starts moving
        await pg.wait_for_function("document.querySelector('#app > .shell') && document.querySelector('#site-foot footer')", timeout=20000, polling=10)
        app, foot = await pg.evaluate("""() => {
          const a = document.querySelector('#app > .shell').cloneNode(true);
          a.setAttribute('data-pre', '');
          a.querySelectorAll('.reveal,.pre').forEach(e => e.classList.remove('reveal', 'pre'));
          a.querySelectorAll('.halo,.dm-cur').forEach(e => e.removeAttribute('style'));   // positions the app sets as it runs
          const t = a.querySelector('#topbar'); if(t) t.classList.remove('stuck', 'light');
          const f = document.querySelector('#site-foot footer').cloneNode(true);
          f.setAttribute('data-pre', '');
          return [a.outerHTML, f.outerHTML];
        }""")
        await b.close()
        return app, foot


def main():
    html = strip_pre(open(INDEX, encoding="utf-8").read())
    open(INDEX, "w", encoding="utf-8").write(html)
    httpd = serve()
    try:
        app, foot = asyncio.run(capture("http://127.0.0.1:%d/" % httpd.server_address[1]))
    finally:
        httpd.shutdown()
    assert "Practice Test 1" in app and "data-pre" in app
    html = html.replace("<!--pre--><!--/pre-->", "<!--pre-->" + app + "<!--/pre-->", 1)
    html = html.replace("<!--prefoot--><!--/prefoot-->", "<!--prefoot-->" + foot + "<!--/prefoot-->", 1)
    open(INDEX, "w", encoding="utf-8").write(html)
    print("prerendered home: %d bytes, footer %d bytes" % (len(app), len(foot)))


if __name__ == "__main__":
    main()
