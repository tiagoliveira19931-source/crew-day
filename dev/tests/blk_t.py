# Block time from the briefing, entered per flight in My flights, drives the timer and landing estimate.
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
    pg.clock.set_system_time(datetime.datetime(2026,11,12,13,0)); pg.click("[data-tab=trip]"); pg.wait_for_timeout(150)
    f=pg.locator('[data-fold^="flights"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    F("#ts-b-0","4:20"); F("#ts-b-1","4:05")
    v=pg.input_value("#ft-est"); print("timer box:",v); assert v=="4:20",v
    pg.click("#ftgo"); pg.wait_for_timeout(100)
    chip=pg.locator(".ftcard .chip").inner_text(); print("running:",chip); assert "4:20" in chip
    F("#ts-b-0","4:35"); chip=pg.locator(".ftcard .chip").inner_text(); print("changed while running:",chip); assert "4:35" in chip
    note=pg.locator("#ts-b-0").locator("xpath=ancestor::div[contains(@class,'seccard')]").inner_text(); print(note.replace("\n"," ")[-160:]); assert "briefing" in note
    b.close()
print("ERRORS:", errs or "none")
