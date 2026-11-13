# Landing after midnight: Today keeps yesterday's duty (and getting home) until home + 30 min, then shows today's duty.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="""2026-11-12 | DUTY | 14:50 | 00:40 | FR2812 STN-LPA 15:35-20:00; FR2811 LPA-STN 20:35-00:10
2026-11-13 | DUTY | 15:25 | 22:45 | FR1882 STN-LIS 16:10-19:00; FR1883 LIS-STN 19:25-22:15"""
train="""Monday to Friday
00:30 → 00:45
05:30 → 05:45
Return
Monday to Friday
00:55 → 01:10
05:28 → 05:43
"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,13,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(80)
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    F("#tr-from-train","Bishops Stortford"); F("#tr-walk-train","10"); F("#tr-out-train",train)
    pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.clock.set_system_time(datetime.datetime(2026,11,12,23,30)); pg.click("[data-tab=trip]"); pg.wait_for_timeout(150)
    f=pg.locator('[data-fold^="flights"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    F("#ts-o-1","20:40"); F("#ts-n-1","00:15")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,0,40)); pg.wait_for_timeout(1200)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200); t=pg.inner_text("main").replace("\n"," ")
    print("00:40:", t[:220]); assert "Lisbon" not in t[:120], "switched to today's duty too early"
    assert "Getting home" in t or "GETTING HOME" in t.upper(), "getting home missing"
    pg.clock.set_system_time(datetime.datetime(2026,11,13,2,30)); pg.wait_for_timeout(1200)
    pg.click("[data-tab=trip]"); pg.click("[data-tab=today]"); pg.wait_for_timeout(200); t=pg.inner_text("main").replace("\n"," ")
    print("02:30:", t[:160]); assert "Lisbon" in t[:200], "should show today's Lisbon duty now"
    b.close()
print("ERRORS:", errs or "none")
