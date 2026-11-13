# Last sector: ride home shows on Trip, pick another, missed, auto "caught" 15 min after it leaves; timer survives midnight.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="2026-11-12 | DUTY | 16:50 | 01:10 | FR2812 STN-LPA 17:35-21:55; FR2811 LPA-STN 22:30-00:40"
train="""Monday to Friday
xx:28 → xx:43 (06:00 – 23:59)
Return
Monday to Friday
xx:28 → xx:43 (06:00 – 23:59)
"""
bus="""Monday to Sunday
xx:20 → xx:55 (00:00 – 23:59)
Return
Monday to Sunday
xx:10 → xx:45 (00:00 – 23:59)
"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,15,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(80)
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    F("#tr-from-train","Bishops Stortford"); F("#tr-walk-train","10"); F("#tr-out-train",train)
    F("#tr-from-bus","Harlow"); F("#tr-walk-bus","5"); F("#tr-out-bus",bus)
    pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.click("[data-tab=today]"); 
    if pg.locator('[data-goto^="today:travel"]').count(): pg.click('[data-goto^="today:travel"]')
    if pg.locator("#d-mode").count(): pg.select_option("#d-mode","train")
    # last sector pushback 22:35, timer running
    pg.clock.set_system_time(datetime.datetime(2026,11,12,22,35)); pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    f=pg.locator('[data-fold^="flights"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    F("#ts-o-0","17:40"); F("#ts-n-0","22:00")
    pg.fill("#ft-est","2:10"); pg.click("#ftgo"); pg.wait_for_timeout(150)
    t=pg.inner_text("main").replace("\n"," "); i=t.upper().find("GETTING HOME"); print("in flight 22:35:", t[i:i+300])
    assert i>=0, "getting home should show during the last sector"
    # past midnight: timer still there
    pg.clock.set_system_time(datetime.datetime(2026,11,13,0,20)); pg.wait_for_timeout(1200)
    pg.click("[data-tab=today]"); pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    assert pg.locator("#ftstop").count(), "flight timer lost after midnight"
    pg.click("#ftstop"); pg.wait_for_timeout(150)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    t=pg.inner_text("main").replace("\n"," "); i=t.upper().find("GETTING HOME"); print("landed 00:20:", t[i:i+330])
    # pick a different one, then mark missed, then let it auto-catch
    btn=pg.locator("[data-hpick]").first; assert btn.count(); btn.click(); pg.wait_for_timeout(100)
    t=pg.inner_text("main").replace("\n"," "); i=t.find("Your pick"); print("picked:", t[i:i+80]); assert i>=0
    pg.click("[data-hmiss]"); pg.wait_for_timeout(100)
    t=pg.inner_text("main").replace("\n"," "); i=t.upper().find("GETTING HOME"); print("after missed:", t[i:i+200])
    first=pg.locator("[data-hcaught]"); assert first.count()
    # read the suggested departure time and jump to 16 min after it
    import re
    m=re.search(r"Take: (?:bus|train)[^a]* at (\d\d):(\d\d)", t); assert m, t[i:i+200]
    h,mi=int(m.group(1)),int(m.group(2)); dep=datetime.datetime(2026,11,13,h,mi)
    pg.clock.set_system_time(dep+datetime.timedelta(minutes=16)); pg.wait_for_timeout(1200)
    pg.click("[data-tab=trip]"); pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    t=pg.inner_text("main").replace("\n"," "); print("auto:", t[t.upper().find("GETTING HOME"):][:160] if "GETTING HOME" in t.upper() else t[:160])
    assert "On the" in t, "should be auto-marked as caught"
    b.close()
print("ERRORS:", errs or "none")
