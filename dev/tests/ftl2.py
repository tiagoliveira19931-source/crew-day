import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,4,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("#etopen"); pg.click('[data-etkind="standby"]'); pg.fill("#et-s","05:00"); pg.fill("#et-e","17:00"); pg.click("#etsave")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,6,30)); pg.click("[data-tab=today]")
    pg.click('[data-fold^="ftl"]'); print("night start, call 06:30:",pg.locator(".fbody .sbnow").last.inner_text().replace("\n"," "),"|",pg.locator(".fbody p").first.inner_text())
    # airport standby
    pg.click("#etopen"); pg.click('[data-etkind="asby"]'); pg.fill("#et-s","05:00"); pg.fill("#et-e","13:00"); pg.click("#etsave")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,10,0)); pg.click("[data-tab=today]"); print("asby card:",pg.inner_text(".nowcard").replace("\n"," "))
    pg.click("#asbycall"); pg.click("[data-tab=today]"); print("after call:",pg.inner_text(".pass").replace("\n"," "))
    print("ERRORS:",errs or "none")
