# Margin

The site behind [marginsat.com](https://marginsat.com): five free, full-length SAT practice tests in a Bluebook-style test screen, plus a paper mode for taking the PDFs with a pen.

This repository holds the built site, served by GitHub Pages. Progress is saved in each visitor's browser; there is no server.

- `index.html`: the practice app (tests, reports, history, redo drills, question bank, concept drills, a checklist of every SAT skill with progress bars, guide). It holds a static copy of the home page so it shows before the test data loads.
- `data/tests.<hash>.json`: the five tests, loaded by the app at startup
- `assets/`: `app.css` (the app's styles), `katex.css` (math typesetting), `site.css` and `site.js` (landing pages)
- `bank/`: the question bank, 628 original hard questions that aren't in the tests, on four levels up to Extreme, plus their figures. The app builds tailored practice sets from it based on every question a student has missed.
- `bank/concepts/`: 26 concept drills (mixtures, work rates, circle equations and more), each with a short lesson and 36 questions on three levels
- `paper/`: paper mode, a PDF viewer with pen markup, module timers and an answer sheet
- `tests/`: the five practice tests as PDFs
- `sat-practice-tests/`, `sat-question-bank/`, `sat-math-concepts/` (one page per drill), `sat-guide/`, `about/`, `privacy/`: plain landing pages for search engines, built by `tools/build_pages.py`

## Tools

- `python3 tools/build_pages.py` rebuilds the landing pages and `sitemap.xml` from the data.
- `python3 tools/prerender.py` refreshes the static copy of the home page inside `index.html` (needs Playwright).
- `python3 tools/configure.py` switches analytics and ads on or off and refreshes asset versions:
  - `--goatcounter marginsat` counts visits at marginsat.goatcounter.com (no cookies)
  - `--adsense-client ca-pub-… --adsense-slot …` turns on the one manual ad unit and writes `ads.txt`
  - `--search-console <token>` adds Google's verification meta tag (DNS verification works too)

Ads appear in one labeled slot near the bottom of the home page, reports, history, the bank and concept pages, and the landing pages. Never in the test screen, single bank questions, or paper mode. Add `?adpreview=1` to any URL to see where the slot goes before AdSense is set up (`?adpreview=0` turns the preview off).
