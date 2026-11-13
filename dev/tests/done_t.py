import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="2026-11-12 | DUTY | 12:50 | 23:25 | FR2812 STN-LPA 13:35-18:00 9HQAG; FR2811 LPA-STN 18:35-22:55 9HQAG"
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,12,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(80)
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.clock.set_system_time(datetime.datetime(2026,11,12,20,0)); pg.wait_for_timeout(100)
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(150)
    f=pg.locator('[data-fold^="flights"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    F("#ts-o-0","13:46"); F("#ts-n-0","18:27"); F("#ts-o-1","19:08")
    print("20:00 clock:", pg.locator('[aria-label="Duty clock"]').inner_text().replace("\n"," "))
    pg.clock.set_system_time(datetime.datetime(2026,11,12,23,10)); pg.wait_for_timeout(100)
    F("#ts-n-1","22:55")
    print("23:10 clock:", pg.locator('[aria-label="Duty clock"]').inner_text().replace("\n"," "))
    pg.clock.set_system_time(datetime.datetime(2026,11,13,0,0)); pg.wait_for_timeout(1500)
    pg.click("[data-tab=today]"); pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    print("00:00:", pg.locator('[aria-label="Duty done"]').inner_text().replace("\n"," ") if pg.locator('[aria-label="Duty done"]').count() else "no done card", "| duty clock:", pg.locator('[aria-label="Duty clock"]').count())
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200); print("today:", pg.inner_text("main")[:150].replace("\n"," "))
    b.close()
print("ERRORS:", errs or "none")
