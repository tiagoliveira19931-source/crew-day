# Ryanair legend codes: ground duty, dead head, ground transport, special duty, airport duty, unpaid leave,
# availability, pending sick - read from screenshots and pasted lines with their own names. Made-up days.
import sys, datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    txt="""14 Nov 26
GD 08:00 Z - 16:00 Z
15 Nov 26
DH 06:00 Z - 08:30 Z
16 Nov 26
Available Early Shift 00:00 Z - 23:59 Z
17 Nov 26
Pending Sick 00:00 Z - 23:59 Z
18 Nov 26
AD 05:00 Z - 13:00 Z
19 Nov 26
UL 00:00 Z - 23:59 Z
20 Nov 26
GT 10:00 Z - 11:00 Z
21 Nov 26
SD 09:00 Z - 15:00 Z"""
    r=pg.evaluate("t=>window.CREWDAY_TEST.rpZ(t).map(e=>[e.date,e.kind,e.sub||'',e.report,e.off])",txt)
    want={"2026-11-14":("adty","Ground duty"),"2026-11-15":("adty","Dead head"),"2026-11-16":("off","Day off · available early shift"),"2026-11-17":("sick","Sick (pending)"),
      "2026-11-18":("adty",""),"2026-11-19":("leave","Unpaid leave (pending)"),"2026-11-20":("adty","Ground transport"),"2026-11-21":("adty","Special duty")}
    got={x[0]:(x[1],x[2]) for x in r}
    assert got==want, got
    # pasted lines, then Today on a ground duty day shows its name
    pg.clock.install(time=datetime.datetime(2026,11,14,6,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p","2026-11-14 | GD | 08:00 | 16:00\n2026-11-15 | DH | 06:00 | 08:30\n2026-11-16 | UL"); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    R=pg.evaluate("window.CREWDAY_TEST.roster()")
    assert R["2026-11-14"]["kind"]=="adty" and R["2026-11-14"].get("sub")=="Ground duty", R["2026-11-14"]
    assert R["2026-11-15"].get("sub")=="Dead head" and R["2026-11-16"]["kind"]=="leave", R
    pg.click("[data-tab=today]"); pg.wait_for_timeout(300)
    assert "Ground duty" in pg.inner_text("main")[:200], pg.inner_text("main")[:200]
    print("ERRORS:", "; ".join(errs) if errs else "none")
