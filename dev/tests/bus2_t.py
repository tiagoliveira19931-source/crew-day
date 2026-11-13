import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); bus=open("busin.txt").read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,18,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.select_option("#t-mode","bus")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change")
    F("#tr-from-bus","Riverside (Brazier's Quay)"); F("#tr-ride-bus","20"); F("#tr-walk-bus","6"); F("#tr-out-bus",bus)
    print("out:",pg.locator("#tr-out-bus").locator("xpath=..").locator(".note").first.inner_text())
    print("back:",pg.locator("#tr-back-bus").locator("xpath=..").locator(".note").first.inner_text())
    pg.click("#setupdone"); pg.click("[data-tab=plan]"); F("#n-rep","06:00")
    print("plan:",pg.locator(".seccard").filter(has_text="Your bus").inner_text().replace("\n"," | ")[:260])
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.click('[data-pick="2026-11-13"]'); pg.click('[data-setkind=flying]'); pg.fill("#rw-r","06:00"); pg.fill("#rw-o","14:40"); pg.click('[data-saveday="2026-11-13"]'); pg.click('[data-more=""]')
    pg.clock.set_system_time(datetime.datetime(2026,11,13,13,0)); pg.click("[data-tab=today]"); pg.wait_for_timeout(100); pg.click("[data-tab=today]")
    print("home:",pg.locator("section.card").filter(has_text="Getting home").inner_text().replace("\n"," | "))
    print("ERRORS:",errs or "none")
