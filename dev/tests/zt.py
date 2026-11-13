import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,7,10,15,0))   # summer: UK = Z+1
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.click('[data-pick="2026-07-11"]'); pg.click('[data-setkind=flying]'); pg.click('[data-addsec="2026-07-11"]')
    pg.fill("#sc-flt-0","FR2412"); pg.fill("#sc-to-0","kun"); pg.fill("#sc-dep-0","05:00"); pg.fill("#sc-arr-0","07:40"); pg.click('[data-saveday="2026-07-11"]')
    print("roster:",pg.input_value("#rw-r"),"| dest:",pg.input_value("#rw-d"),"|",pg.locator("#rw-r").locator("xpath=../../..").locator("p").first.inner_text())
    pg.click('[data-more=""]'); pg.click("[data-tab=plan]"); pg.wait_for_timeout(200)
    if pg.locator("[data-usenext]").count(): pg.click("[data-usenext]")
    print("plan report (local):",pg.input_value("#n-rep"),"dep:",pg.input_value("#n-dep"),"dest:",pg.input_value("#n-dest"))
    pg.fill("#n-dest","TLL"); pg.locator("#n-dest").dispatch_event("change"); print("plan dest from code:",pg.input_value("#n-dest"))
    pg.clock.set_system_time(datetime.datetime(2026,7,11,4,0)); pg.click("[data-tab=today]"); pg.wait_for_timeout(100); pg.click("[data-tab=today]")
    print("today:",pg.inner_text("main header").replace("\n"," "),"|",pg.inner_text(".pass").replace("\n"," "))
    pg.click("[data-tab=trip]"); pg.click('[data-fold="dest"]'); pg.fill("#tr-city","bcn"); pg.locator("#tr-city").dispatch_event("change"); print("trip city:",pg.input_value("#tr-city"),pg.input_value("#tr-c"))
    pg.clock.set_system_time(datetime.datetime(2026,7,11,5,40)); pg.click("[data-tab=trip]"); pg.wait_for_timeout(100)
    print("timer:",pg.locator(".ftcard").inner_text().replace("\n"," | ")[:200])
    pg.fill("#ft-est","2:40"); pg.click("#ftgo"); print("running:",pg.locator(".ftcard").inner_text().replace("\n"," | ")[:200])
    pg.click("#ftstop")
    if pg.locator('[data-fold^="flights"][aria-expanded="false"]').count(): pg.click('[data-fold^="flights"]')
    print("flights:",pg.locator('[data-fold^="flights"]').locator("xpath=..").inner_text().replace("\n"," | ")[:300])
    pg.click("[data-tab=today]"); print("today head:",pg.inner_text("main header").replace("\n"," "),"|",pg.inner_text(".pass").replace("\n"," ")[:120])
    print("ERRORS:",errs or "none")
