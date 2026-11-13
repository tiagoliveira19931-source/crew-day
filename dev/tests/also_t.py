# Days with more than one duty code: home standby then flights, flights then a special duty, LATE then airport duty,
# training with a sub-code. Both from the AI line format and from a screenshot reading. Made-up flights.
import datetime, json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
READ="""DUTY FLIGHT TIME: 3H 44M
25 Nov 26, Wed
11:00 Z STN ~ HSBY 18:20 Z
18:20 Z STN CHECK IN
19:09 Z STN + FR2738 BGY 20:45 Z
21:25 Z BGY + FR2739 STN 23:33 Z
26 Nov 26, Thu
00:03 Z STN CHECK OUT
DUTY
26 Nov 26, Thu
04:40 Z LATE 05:40 Z
05:40 Z STN CHECK IN
05:40 Z STN Airport Duty 13:40 Z
13:40 Z CHECK OUT
DUTY
27 Nov 26, Fri
08:00 Z STN CHECK IN
08:00 Z STN Training 17:25 Z
08:00 LT CRMS 17:25 LT
17:25 Z CHECK OUT"""
STUB="<script>window.Tesseract={createWorker:async()=>({setParameters:async()=>{},recognize:async()=>({data:{text:%s}}),terminate:async()=>{}})};</script>"%json.dumps(READ)
PAGE="<!doctype html><html><head><meta charset=utf-8></head><body>"+STUB+html+"</body></html>"
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.fulfill(body=PAGE,content_type="text/html") if r.request.url=="https://t.test/" else r.abort())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0)); pg.goto("https://t.test/")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p","2026-11-20 | DUTY | 14:45 | 22:00 | FR6647 STN-ALC 15:25-17:45; FR6646 ALC-STN 18:37-21:18; + Special Duty 21:48-22:00"); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    pg.set_input_files("#ocr-f",[{"name":"s.png","mimeType":"image/png","buffer":b"\x89PNG"}]); pg.wait_for_timeout(2500)
    R=pg.evaluate("window.CREWDAY_TEST.roster()")
    for d in sorted(R): print(d,R[d]["kind"],R[d].get("report"),R[d].get("off"),R[d].get("also"))
    assert R["2026-11-20"]["also"]==[{"label":"Special duty","from":"21:48","to":"22:00"}], R["2026-11-20"]
    assert R["2026-11-25"]["kind"]=="flying" and R["2026-11-25"]["also"][0]["label"]=="Home standby", R["2026-11-25"]
    assert R["2026-11-26"]["kind"]=="adty" and any(a["label"]=="Late" for a in R["2026-11-26"]["also"]), R["2026-11-26"]
    assert R["2026-11-27"]["kind"]=="training" and R["2026-11-27"]["also"][0]["label"]=="Training CRMS", R["2026-11-27"]
    pg.click('[data-pick="2026-11-25"]'); pg.wait_for_timeout(150); t=pg.inner_text("main")
    assert "also on this day" in t.lower() and "Home standby" in t
    b.close()
print("ERRORS:", errs or "none")
