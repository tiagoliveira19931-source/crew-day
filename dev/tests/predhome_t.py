# Getting home follows the predicted landing: "if you're off quickly" from predicted on blocks + 20 min.
# Made-up roster and timetable.
import datetime, sys
from playwright.sync_api import sync_playwright
html=open(sys.argv[1] if len(sys.argv)>1 else "/home/claude/crew-day.html").read(); errs=[]
rost="2026-11-14 | DUTY | 11:45 | 18:00 | FR147 STN-BER 13:30-15:15; FR146 BER-STN 15:40-17:30"
train="Monday to Sunday\n09:28 → 09:36\n10:28 → 10:36\nReturn\nMonday to Sunday\n17:28 → 17:36\n17:58 → 18:06\n18:28 → 18:36\n18:58 → 19:06\n19:28 → 19:36\n"
U=lambda h,m:datetime.datetime(2026,11,14,h,m,tzinfo=datetime.timezone.utc)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=U(9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(80)
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    F("#tr-from-train","Town"); F("#tr-walk-train","10"); F("#tr-out-train",train)
    pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.clock.set_system_time(U(15,50)); pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    f=pg.locator('[data-fold="flights"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    F("#ts-o-0","13:29"); F("#ts-n-0","15:14")
    pg.click("[data-tab=today]"); pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    F("#ft-est","1:50"); pg.click("#ftgo"); pg.wait_for_timeout(200)   # off blocks 15:45, predicted on 17:35
    pg.click("[data-tab=today]"); pg.wait_for_timeout(300)
    h=pg.locator('[data-fold^="home"]')
    if h.get_attribute("aria-expanded")=="false": h.click()
    t=pg.inner_text("main").replace("\n"," "); i=t.find("Off duty around"); g=t[i:i+520]; print(g)
    assert "predicted landing 17:35" in g, g
    assert "17:58 Train (if you're off quickly)" in g, g          # 17:35 + 20 = 17:55
    assert "17:28" not in g, g
    assert "Take: train at 18:28" in g, g
    # quickest time 30 min: the 17:58 is no longer offered
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="profile"]'); pg.wait_for_timeout(150)
    if pg.locator("#pr-tostn").count()==0:
        for fl in pg.locator('[data-fold^="pf_"][aria-expanded="false"]').all():
            fl.click(); pg.wait_for_timeout(80)
            if pg.locator("#pr-tostn").count(): break
    F("#pr-tostn","30")
    pg.click("[data-tab=today]"); pg.wait_for_timeout(300)
    t=pg.inner_text("main").replace("\n"," "); i=t.find("Off duty around"); g=t[i:i+520]
    assert "17:58" not in g, g
print("ERRORS:", "; ".join(errs) if errs else "none")
