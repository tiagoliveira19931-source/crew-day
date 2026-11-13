import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},color_scheme="dark")
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,20,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.set_input_files("#ics",sys.argv[2]); pg.wait_for_timeout(200); pg.click('[data-more=""]')
    pg.clock.set_system_time(datetime.datetime(2026,11,12,3,40)); pg.click("[data-tab=today]"); pg.screenshot(path="/tmp/look_duty.png")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,10,0)); pg.click("[data-tab=today]")
    pg.click("#etopen"); pg.click('[data-etkind="standby"]'); pg.fill("#et-s","10:30"); pg.fill("#et-e","20:30"); pg.click("#etsave")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,11,35)); pg.click("[data-tab=today]")
    print("11:35:",pg.inner_text(".pass").replace("\n"," "))
    pg.click(".bigbtn[data-sbcheck]"); print("after:",pg.inner_text(".pass").replace("\n"," "))
    pg.screenshot(path="look_sb.png",full_page=True)
    pg.click("[data-tab=more]"); pg.click('[data-more="settings"]'); pg.click('[data-mode="auto"]'); print("auto bg:",pg.evaluate("getComputedStyle(document.body).backgroundColor")); pg.click('[data-mode="light"]'); print("light bg:",pg.evaluate("getComputedStyle(document.body).backgroundColor"))
    print("ERRORS:",errs or "none")
