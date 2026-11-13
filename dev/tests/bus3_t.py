import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); bus=open("busin2.txt").read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,18,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.select_option("#t-mode","bus")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change")
    F("#tr-ride-bus","25"); F("#tr-walk-bus","5"); F("#tr-out-bus",bus); F("#tr-rides-bus","510=20, 509=25, 309=35")
    print("out:",pg.locator("#tr-out-bus").locator("xpath=..").locator(".note").first.inner_text())
    pg.click("#setupdone"); pg.click("[data-tab=plan]"); F("#n-rep","08:00")
    print("plan:",pg.locator(".seccard").filter(has_text="Your bus").inner_text().replace("\n"," | ")[:260])
    pg.clock.set_system_time(datetime.datetime(2026,11,13,12,50)); pg.click("[data-tab=today]")
    pg.click("#etopen"); pg.click('[data-etkind="standby"]'); pg.fill("#et-s","09:00"); pg.fill("#et-e","17:00"); pg.click("#etsave")
    pg.click("#called"); pg.wait_for_timeout(100)
    print("called:",pg.locator(".nudges").inner_text().replace("\n"," | ").split("Grab and go")[1][-300:])
    print("ERRORS:",errs or "none")
