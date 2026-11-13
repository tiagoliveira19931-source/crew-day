# Crew Day — notes for Claude

Crew Day is an installable web app (PWA) for airline crew, built for Tiago (Ryanair cabin crew, Stansted) and his partner (Jet2, iPhone). It is served by GitHub Pages from this repo's root: https://tiagoliveira19931-source.github.io/crew-day/

## Layout
- Root (`index.html`, `sw.js`, `manifest.webmanifest`, icons): the **built** app that phones install. Never edit these by hand.
- `dev/crew-day.html`: the **source**. All changes go here.
- `dev/build.py`: builds the root files. `python3 dev/build.py dev/crew-day.html /tmp/build <version>` then copy `/tmp/build/*` to the repo root.
- `dev/offline_test.py /tmp/build`: checks the built app loads and works offline.
- `dev/run_tests.sh`: runs every test (Playwright, fake clocks). Must print `ALL PASSED` before anything is published.

## Versions
The version shows at the bottom of More (`window.CREWDAY_VERSION`, set by build.py). Bump the last number for fixes (1.19.3 → 1.19.4), the middle for new features.

## Rules from Tiago (keep them)
- Plain words: write "VTO" (never "veto"); no abbreviations like HSBY/ASBY in the interface (say Home standby, Airport standby).
- Roster times are entered in Zulu; everything else shows local time marked "L".
- No sales targets, no swap market, no training or annual-leave planner, no payslip storage. Selling staff travel is illegal: never support it.
- Airlines in Profile: Ryanair, Ryanair UK, Jet2, Norse, Other. Home standby call-out: Ryanair and Ryanair UK 1 hour, Jet2 2 hours, Norse not set (crew check their manual). Ryanair group uses a crew code, Jet2 and Norse a staff number.
- Norse is long-haul: the FTL tools are short-haul only and say so for Norse. Long-haul FTL needs checking against the regulation with Tiago before it's built.
- Test rosters in dev/tests are made up. Never put a real roster in the repo.
- Data stays on the phone. Never add anything that sends rosters or personal details anywhere.
- Look: white and teal, rounded friendly font, soft line drawings.
- FTL figures follow EASA ORO.FTL and CS FTL.1 — don't change them without checking the regulation.

## Issue reports
Crew send problems and ideas from More › Report an issue. They queue offline and go to Tiago's Google Form "Crew Day Reports" (responses in a linked Google Sheet). Columns: Timestamp, Type, Area, Report, Version, Airline.
