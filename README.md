# Margin

The site behind [marginsat.com](https://marginsat.com): five free, full-length SAT practice tests in a Bluebook-style test screen, plus a paper mode for taking the PDFs with a pen.

This repository holds the built site, served by GitHub Pages. Progress is saved in each visitor's browser; there is no server.

- `index.html`: the practice app (tests, reports, history, redo drills, question bank, concept drills, guide)
- `bank/`: the question bank, 628 original hard questions that aren't in the tests, on four levels up to Extreme, plus their figures. The app builds tailored practice sets from it based on every question a student has missed.
- `bank/concepts/`: 26 concept drills (mixtures, work rates, circle equations and more), each with a short lesson and 36 questions on three levels
- `paper/`: paper mode, a PDF viewer with pen markup, module timers and an answer sheet
- `tests/`: the five practice tests as PDFs
