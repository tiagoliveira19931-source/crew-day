import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,12,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Ana"); pg.click('[data-gender="f"]'); pg.fill("#pr-s","123"); pg.click("#setupdone")
    pg.click("[data-tab=plan]"); pg.fill("#n-rep","05:30"); pg.locator("#n-rep").dispatch_event("change")
    if pg.locator('[data-fold="planday"][aria-expanded="false"]').count(): pg.click('[data-fold="planday"]')
    box=pg.locator('[data-fold="planday"]').locator("xpath=..")
    print("F steps:",[x.inner_text().replace("\n"," ") for x in box.locator(".tip").all()][4:])
    print("F evening:",[x.inner_text() for x in box.locator('label.chk').all()])
    pg.click("[data-tab=more]"); pg.click('[data-more="kit"]'); pg.wait_for_timeout(100); print("F kit has tights:", "Spare tights" in pg.inner_text("main"), pg.inner_text("main h1"))
    pg.fill("#pd-n","Pretty Polly 15 denier"); pg.select_option("#pd-t","Tights"); pg.fill("#pd-p","4.50"); pg.fill("#pd-d","4"); pg.click("#prodadd")
    print("product:",pg.locator(".seccard").first.inner_text().replace("\n"," | "))
    pg.clock.set_system_time(datetime.datetime(2026,11,13,12,0)); pg.click('[data-more=""]'); pg.click("[data-tab=plan]")
    if pg.locator('[data-fold="kitcheck"][aria-expanded="false"]').count(): pg.click('[data-fold="kitcheck"]')
    print("plan low:",pg.locator('[data-fold="kitcheck"]').locator("xpath=..").locator("p").first.inner_text())
    # switch to male
    pg.click("[data-tab=more]"); pg.click('[data-more="profile"]'); pg.click('[data-fold^="pf_about"]'); pg.click('[data-gender="m"]'); pg.click('[data-more=""]'); pg.click("[data-tab=plan]")
    if pg.locator('[data-fold="planday"][aria-expanded="false"]').count(): pg.click('[data-fold="planday"]')
    box=pg.locator('[data-fold="planday"]').locator("xpath=..")
    pg.wait_for_timeout(200); print("main h1:",pg.inner_text("main h1"))
    print("M steps:",[x.inner_text().replace("\n"," ") for x in box.locator(".tip").all()][4:])
    print("M evening:",[x.inner_text() for x in box.locator('label.chk').all()])
    print("ERRORS:",errs or "none")
