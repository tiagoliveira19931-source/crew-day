import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,15,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone"); pg.click("[data-tab=plan]")
    if pg.locator('[data-fold="planday"][aria-expanded="false"]').count(): pg.click('[data-fold="planday"]')
    pg.click('[data-evepick="Spare tights in bag"]'); pg.click('[data-evepick="Hair bun kit: pins, net, spray"]'); pg.fill("#eve-n","Fake tan"); pg.click("#eveadd")
    pg.locator('[data-eve="0"]').dispatch_event("click")
    box=pg.locator('[data-fold="planday"]').locator("xpath=..")
    print(box.inner_text().replace("\n"," | ")[:700]); box.screenshot(path="/tmp/eve.png")
    print("ERRORS:",errs or "none")
