# Phone abroad on another time zone: Crew Day keeps UK (base) time, so report, trains home and plans don't move.
# Made-up roster and timetable.
import datetime, sys
from playwright.sync_api import sync_playwright
html=open(sys.argv[1] if len(sys.argv)>1 else "/home/claude/crew-day.html").read()
rost="2026-11-14 | DUTY | 11:45 | 18:00 | FR147 STN-BER 13:30-15:15; FR146 BER-STN 15:40-17:30"
train="Monday to Sunday\n17:00 → 17:20\n18:28 → 18:36\n18:58 → 19:06\nReturn\nMonday to Sunday\n18:28 → 18:36\n18:58 → 19:06\n19:28 → 19:36\n"
OUT={};errs=[]
def run(p,z,when):
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},timezone_id=z); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=when)
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(80)
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    F("#tr-from-train","Town"); F("#tr-walk-train","10"); F("#tr-out-train",train)
    pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost.replace("2026-11-14",when.strftime("%Y-%m-%d"))); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(400)
    t=pg.inner_text("main"); i=t.find("Getting home")
    r=(t[:t.find("Change")].replace("\n"," "), t[i:i+330].replace("\n"," ") if i>=0 else "")
    b.close(); return r
with sync_playwright() as p:
    for when in (datetime.datetime(2026,11,14,15,38,tzinfo=datetime.timezone.utc), datetime.datetime(2026,7,14,14,38,tzinfo=datetime.timezone.utc)):
        L=run(p,"Europe/London",when); B=run(p,"Europe/Berlin",when); N=run(p,"America/New_York",when)
        print(when.date(),"London:",L[0]); print(when.date(),"Berlin:",B[0])
        assert "Your phone is on Berlin time (+1h)" in B[0], B[0]
        assert "Your phone is on" not in L[0], L[0]
        strip=lambda x:x.split("Your phone")[0].strip()
        assert strip(B[0])==strip(L[0]) and strip(N[0])==strip(L[0]), (L[0],B[0],N[0])
        assert B[1]==L[1] and N[1]==L[1], (L[1],B[1],N[1])
print("ERRORS:", "; ".join(errs) if errs else "none")
