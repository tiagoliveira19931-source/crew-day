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
    print("09:00:",pg.inner_text(".pass").replace("\n"," "))
    pg.clock.set_system_time(datetime.datetime(2026,11,13,12,10)); pg.click("[data-tab=today]")
    a=pg.inner_text(".pass").replace("\n"," "); pg.clock.run_for(3000); b2=pg.inner_text(".pass").replace("\n"," ")
    print("12:10:",a,"\n  +3s:",b2)
    pg.screenshot(path="/tmp/cd_sb.png")
    pg.click("#etopen"); pg.click('[data-etkind="flying"]'); pg.fill("#et-s","10:00"); pg.click("#etsave")
    print("duty:",pg.inner_text(".pass").replace("\n"," "))
    pg.click("#etopen"); pg.click('[data-etkind="asby"]'); pg.fill("#et-s","11:00"); pg.fill("#et-e","17:00"); pg.click("#etsave")
    print("asby:",pg.inner_text(".pass").replace("\n"," "))
    print("ERRORS:",errs or "none")
