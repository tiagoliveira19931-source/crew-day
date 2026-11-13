import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("#etopen"); pg.click('[data-etkind="standby"]'); pg.fill("#et-s","10:30"); pg.fill("#et-e","20:30"); pg.click("#etsave")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,11,40)); pg.click("[data-tab=today]")
    pg.screenshot(path="/tmp/rc.png")
    print("due:",pg.locator(".bigbtn").first.inner_text())
    pg.click(".bigbtn[data-sbcheck]"); print("after: btn count",pg.locator(".bigbtn[data-sbcheck]").count())
    print("top:",pg.inner_text(".pass").replace("\n"," "))
    print("called bg:",pg.evaluate("getComputedStyle(document.getElementById('called')).backgroundColor"))
    print("ERRORS:",errs or "none")
