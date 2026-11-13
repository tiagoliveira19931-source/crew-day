import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); tt=open("ttin.txt").read(); errs=[]
back="""Monday to Friday
05:55 → 06:06
xx:28 → xx:39 (06:00 – 23:00)
Saturday
First train: 06:10
Daytime: xx:28 and xx:58
Last train: 23:40
"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,18,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.select_option("#t-mode","train"); pg.wait_for_timeout(100)
    pg.fill("#tr-walk-train","12"); pg.locator("#tr-walk-train").dispatch_event("change")
    pg.fill("#tr-out-train",tt); pg.locator("#tr-out-train").dispatch_event("change")
    pg.fill("#tr-back-train",back); pg.locator("#tr-back-train").dispatch_event("change")
    print("read out:",pg.locator("#tr-out-train").locator("xpath=..").locator(".note").first.inner_text())
    print("read back:",pg.locator("#tr-back-train").locator("xpath=..").locator(".note").first.inner_text())
    pg.fill("#t-buf","15"); pg.locator("#t-buf").dispatch_event("change"); pg.click("#setupdone")
    pg.click("[data-tab=plan]"); pg.fill("#n-rep","06:30"); pg.locator("#n-rep").dispatch_event("change")
    print("plan 06:30:",pg.locator(".seccard").filter(has_text="Your train").first.inner_text().replace("\n"," | "))
    # duty today ending, getting home
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.click('[data-pick="2026-11-13"]'); pg.click('[data-setkind=flying]'); pg.fill("#rw-r","06:30"); pg.fill("#rw-o","14:50"); pg.click('[data-saveday="2026-11-13"]'); pg.click('[data-more=""]')
    pg.clock.set_system_time(datetime.datetime(2026,11,13,13,0)); pg.click("[data-tab=today]"); pg.wait_for_timeout(100); pg.click("[data-tab=today]")
    print("home card:",pg.locator("section.card").filter(has_text="Getting home").inner_text().replace("\n"," | ") if pg.locator("section.card").filter(has_text="Getting home").count() else "none")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,23,30)); pg.click("[data-tab=today]"); pg.wait_for_timeout(100)
    print("done 23:30:",pg.locator("main section.card").first.inner_text().replace("\n"," | ")[:300])
    print("ERRORS:",errs or "none")
