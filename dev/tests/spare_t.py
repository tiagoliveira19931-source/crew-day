# Going to work: the app suggests one train before the last one that works (a spare); the last one is still selectable, at your own risk.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="""2026-11-12 | DUTY | 14:50 | 00:40 | FR2812 STN-LPA 15:35-20:00; FR2811 LPA-STN 20:35-00:10
2026-11-14 | DUTY | 12:45 | 18:00 | FR147 STN-BER 13:30-15:15; FR146 BER-STN 15:40-17:30"""
train="""Monday to Friday
05:30 → 05:45
xx:13 → xx:28 (06:00 – 23:00)
Saturday
xx:13 → xx:28 (07:00 – 09:00)
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
    pg.clock.install(time=datetime.datetime(2026,11,12,13,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(80)
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    F("#tr-from-train","Bishops Stortford"); F("#tr-walk-train","10"); F("#tr-out-train",train)
    F("#tr-from-bus","Harlow"); F("#tr-walk-bus","5"); F("#tr-out-bus",bus)
    pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.click("[data-tab=today]"); pg.click('[data-goto^="today:travel"]') if pg.locator('[data-goto^="today:travel"]').count() else None
    pg.wait_for_timeout(100)
    if pg.locator("#d-mode").count(): pg.select_option("#d-mode","train"); pg.wait_for_timeout(100)
    pg.clock.set_system_time(datetime.datetime(2026,11,12,9,0)); pg.wait_for_timeout(1200)
    pg.click("[data-tab=trip]"); pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    pg.locator('[data-goto="plan"]').first.click(); pg.wait_for_timeout(200)
    t=pg.inner_text("main").replace("\n"," "); i=t.find("Leave home"); print("card:", t[max(0,i-200):i+400])
    assert "Leave home 10:15 for the 10:20" in t or "for the 07:13" not in t, "card should match the plan"
    assert "at your own risk" in t, "a spare departure should be suggested, with the last one marked own risk"
    btns=pg.locator("[data-tpick]"); last=btns.nth(btns.count()-1); print("last btn:", last.inner_text()); assert "last one" in last.inner_text()
    last.click(); pg.wait_for_timeout(200)
    t=pg.inner_text("main").replace("\n"," "); assert "You picked the last one that works" in t, "picking the last one should warn"
    b.close()
print("ERRORS:", errs or "none")
