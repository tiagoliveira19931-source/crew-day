# Landing late: the sleep plan for tomorrow starts from when you're really home, and Getting home also shows the train just before the suggested one.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="""2026-11-12 | DUTY | 13:00 | 20:45 | FR1882 STN-LIS 13:45-16:35; FR1883 LIS-STN 17:15-20:15
2026-11-13 | DUTY | 06:00 | 14:00 | FR2812 STN-DUB 06:45-08:00; FR2813 DUB-STN 08:40-09:55"""
train="""Monday to Friday
05:00 → 05:15
Return
Monday to Friday
21:30 → 21:45
22:58 → 23:13
23:28 → 23:43
23:58 → 00:13
"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,12,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(80)
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    F("#tr-from-train","Bishops Stortford"); F("#tr-walk-train","10"); F("#tr-out-train",train)
    pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.clock.set_system_time(datetime.datetime(2026,11,12,22,0)); pg.click("[data-tab=trip]"); pg.wait_for_timeout(150)
    f=pg.locator('[data-fold^="flights"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    F("#ts-o-1","19:20"); F("#ts-n-1","22:25")
    pg.clock.set_system_time(datetime.datetime(2026,11,12,22,40)); pg.wait_for_timeout(1200)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200); t=pg.inner_text("main").replace("\n"," ")
    print("home:", t[t.find("Getting home"):][:330])
    assert "Take: train at 23:28" in t, "suggested train should still be 23:28"
    assert "22:58 Train (if you're off quickly)" in t, "the earlier 22:58 should be shown too"
    assert "21:30" not in t[t.find("Getting home"):], "a train before landing must not show"
    pg.click('[data-hpick^="train|"] >> nth=0'); pg.wait_for_timeout(150); t=pg.inner_text("main").replace("\n"," ")
    assert "Your pick: train at 22:58" in t, "picking the quick one should stick"
    pg.click("[data-tab=plan]"); pg.wait_for_timeout(200); t=pg.inner_text("main").replace("\n"," ")
    s=t[t.find("Tonight and sleep"):][:200]; print("sleep:", s)
    assert "Home from your duty" in s and "21:40" not in s, "sleep plan should start from the real home time"
    assert "Pack bag" not in s, "no evening packing before you're home"
    b.close()
print("ERRORS:", errs or "none")
