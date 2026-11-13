# Late report: the wake-up alarm follows a full night's sleep, not the report. Early reports and standby call-outs are unchanged.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="""2026-11-13 | DUTY | 15:00 | 23:30 | FR10 STN-LIS 15:45-18:50; FR11 LIS-STN 19:30-22:30
2026-11-14 | DUTY | 05:30 | 13:00 | FR1 STN-DUB 06:15-07:30; FR2 DUB-STN 08:00-09:15"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,1,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    t=pg.inner_text('[aria-label="Your duty"]').replace("\n"," "); print("today:",t); assert "07:30" in t, "wake after 8h30 from 23:00"
    f=pg.locator('[data-fold^="morning"]')
    if f.count() and f.get_attribute("aria-expanded")=="false": f.click()
    pg.wait_for_timeout(100); pg.click("#copyalarms"); pg.wait_for_timeout(300); m=pg.inner_text("#copymsg"); print("alarms:",m)
    assert "07:30 Wake up" in m.replace("  "," ") and "Start getting ready" in m and "Snooze" not in m
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="profile"]'); pg.wait_for_timeout(150)
    ff=pg.locator('[data-fold="pf_times"]')
    if ff.get_attribute("aria-expanded")=="false": ff.click()
    pg.fill("#t-bed","00:00"); pg.locator("#t-bed").dispatch_event("change"); pg.select_option("#t-slp","8"); pg.wait_for_timeout(150)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    t=pg.inner_text('[aria-label="Your duty"]').replace("\n"," "); print("bed 00:00, 8h:",t); assert "08:00" in t
    # early report the next day: wake in time for it
    pg.clock.set_system_time(datetime.datetime(2026,11,14,1,0)); pg.wait_for_timeout(1200)
    pg.click("[data-tab=trip]"); pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    t=pg.inner_text('[aria-label="Your duty"]').replace("\n"," "); print("early:",t); assert "03:15" in t and "07:30" not in t and "08:00" not in t
    b.close()
print("ERRORS:", errs or "none")
