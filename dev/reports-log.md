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

## 14 Nov 2026 (1.35.1)
- Idea (Jet2): wants reassurance that changes are saved. Done: a short "✓ Saved on this phone" note appears after each change.
- Problem (Ryanair): with a flight key, the timer should use online times rather than buttons. Done: with a key the Start/On blocks buttons are hidden, block end follows the online estimate and the timer stops by itself at the online on-block time. "Start by hand instead" stays for no signal; without a key nothing changes.
- 1.35.2: with a flight key, empty Off/On blocks fields are filled from the online times (never over typed times).
