# Crew Day reports log

Reports from More › Report an issue that have been handled. The repo is public: summaries are in neutral words, with no names, links, codes or roster details.

| Timestamp | Summary | Outcome |
| --- | --- | --- |
| 13/11/2026 00:38:51 | Test report | Test, nothing to do |
| 13/11/2026 00:39:04 | Offline test report | Test, nothing to do |
| 13/11/2026 00:39:39 | Offline test repeat | Test, nothing to do |
| 13/11/2026 10:42:21 | Jet2: app says EASA, but UK airlines are under the UK CAA | Fixed in 1.27.0: rules named UK CAA for Jet2 and Ryanair UK |
| 13/11/2026 11:11:31 | Jet2 roster can only be shared as a calendar link by email | Fixed in 1.27.0: roster can come in from a calendar link, kept on the phone |
| 13/11/2026 16:20:26 | Time from pushback to takeoff at Stansted should allow for taxi | Withdrawn by the reporter later the same day; nothing to do |
| 13/11/2026 19:06:07 | Idea: open an email from the app to send a sickness self-certificate to the company | Asked Tiago |
| 13/11/2026 19:06:08 | Idea: a notebook in Trip | Asked Tiago |
| 13/11/2026 19:06:08 | Idea: folders for saved PDFs and pictures (same timestamp as the row above) | Asked Tiago |
| 13/11/2026 19:11:00 | Withdraws the pushback and taxi report | Nothing to do |
| 13/11/2026 19:50:03 | Getting home: also show the train just before the suggested ones | Fixed in 1.31.1: the one just before is shown as "if you're off quickly" |
| 13/11/2026 19:51:18 | Added morning steps: time can't be changed | Asked Tiago: the minutes box works in tests, so unclear what was meant |
| 13/11/2026 19:51:45 | Withdraws the pushback and taxi report (repeat) | Nothing to do |
| 13/11/2026 22:10:16 | Idea: a link to full instructions for the meal recipes | Asked Tiago |
| 13/11/2026 23:17:22 | Getting home: caught an earlier train than the ones listed | Fixed in 1.31.1 (same as 19:50:03) |
| 13/11/2026 23:24:23 | Tonight and sleep ignored a late landing and still said to pack the bag before they were home | Fixed in 1.31.1: plan starts from when you're really home (actual on blocks, train home) |
| 13/11/2026 23:25:31 | Trip: timer should start at taxi, not pushback | Asked Tiago |
| 13/11/2026 23:41:54 | Report an issue: hide reports once they're dealt with | Asked Tiago (the app can't see what happens to a report without fetching from the sheet) |

| 14/11/2026 10:37:56 | Jet2 idea: reassurance that changes are saved | Fixed in 1.35.1: "✓ Saved on this phone" note after each change (1.35.3: not shown when just moving between screens) |
| 14/11/2026 15:14:51 | With a flight key, timer should run from online times, not buttons | Fixed in 1.35.1 and 1.35.2: buttons hidden with a key, stops itself at online on blocks, empty block times filled from online |

Also 1.35.3 (from a screenshot Tiago sent): Getting home tidy-up: Take this buttons beside each row, times marked L, Caught it/Missed it only near off duty, Change button readable over the drawing.

## 14 Nov 2026 evening (1.36.0, from Tiago's own testing)
- Phone abroad on local time: app keeps UK (base) time; trains home and plans no longer shift.
- Live times: timer stops when the feed says landed (no exact on-block time); missing block times filled for every flight of the day.
- Block times always in Zulu; timer shows Zulu first with local time at each airport; predicted landing beside the running clock.
- Duty ends on blocks + 30, logged in hours once all on-block times are in; "off quickly" trains from on blocks + 20 min (setting).
- Today: Now card with the current step and time left; everything else folds (also Plan and Trip). Destination card removed (place comes from flights).
- Dish drawings with a full view (ingredients, how to make it).
