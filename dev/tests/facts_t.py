import sys,datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,19,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    if pg.locator('[data-fold="dest"][aria-expanded="false"]').count(): pg.click('[data-fold="dest"]')
    pg.select_option("#tr-c","Germany"); pg.wait_for_timeout(100); pg.fill("#tr-city","Cologne"); pg.locator("#tr-city").dispatch_event("change"); pg.wait_for_timeout(300)
    pg.click('[data-fold^="destfacts"]'); pg.wait_for_timeout(200)
    box=pg.locator('[data-fold^="destfacts"]').locator("xpath=..")
    print(box.inner_text()[:1400]); box.screenshot(path="/tmp/facts.png")
    for c,ci in [("Spain","Valencia"),("Egypt","Hurghada"),("Turkey","Antalya")]:
        pg.select_option("#tr-c",c); pg.wait_for_timeout(150); pg.fill("#tr-city",ci); pg.locator("#tr-city").dispatch_event("change"); pg.wait_for_timeout(200)
        t=pg.locator('[data-fold^="destfacts"]').locator("xpath=..").inner_text(); i=t.find("Local time"); print("---",ci,t[i:i+50].replace("\n"," "), "| tail:", t[-260:].replace("\n"," "))
    print("width",pg.evaluate("document.documentElement.scrollWidth"))
    b.close()
print("ERRORS:", errs or "none")
