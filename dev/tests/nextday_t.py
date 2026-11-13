import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="""2026-11-12 | DUTY | 12:50 | 23:25 | FR2812 STN-LPA 13:35-18:00 9HQAG; FR2811 LPA-STN 18:35-22:55 9HQAG
2026-11-13 | DUTY | 15:25 | 22:45 | FR1882 STN-LIS 16:10-19:00 EIEKL; FR1883 LIS-STN 19:25-22:15 EIEKL"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,12,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.clock.set_system_time(datetime.datetime(2026,11,12,23,50)); pg.wait_for_timeout(100)
    pg.clock.set_system_time(datetime.datetime(2026,11,13,0,52)); pg.wait_for_timeout(1500)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200); print("today:", pg.inner_text("main")[:200].replace("\n"," "))
    import json
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(200); print("trip:", pg.inner_text("main")[:600].replace("\n"," | "))
    b.close()
print("ERRORS:", errs or "none")
