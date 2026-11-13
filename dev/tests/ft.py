import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,20,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.set_input_files("#ics",sys.argv[2]); pg.wait_for_timeout(200)
    # make 2nd sector a deadhead
    pg.click('[data-pick="2026-11-12"]'); pg.click('[data-sectyp="1:dh"]'); pg.click('[data-saveday="2026-11-12"]')
    print("roster flights label:",pg.locator(".label").filter(has_text="Flights").inner_text())
    # airport duty day
    pg.click('[data-pick="2026-11-13"]'); pg.click('[data-setkind=adty]'); pg.fill("#rw-r","08:00"); pg.fill("#rw-o","16:00"); pg.click('[data-saveday="2026-11-13"]'); print("ADTY in roster:","ADTY" in pg.inner_text("main"))
    pg.click('[data-more=""]')
    pg.clock.set_system_time(datetime.datetime(2026,11,12,5,50)); pg.click("[data-tab=trip]"); pg.wait_for_timeout(100); pg.click("[data-tab=trip]")
    print("timer:",pg.locator(".ftcard").inner_text().replace("\n"," | "))
    pg.fill("#ft-est","2:35"); pg.click("#ftgo")
    pg.clock.run_for(5000); print("running:",pg.locator(".ftcard").inner_text().replace("\n"," | "))
    pg.locator(".ftcard").screenshot(path="/tmp/ft_run.png")
    pg.clock.set_system_time(datetime.datetime(2026,11,12,8,21,5)); pg.click("#ftstop")
    print("after stop:",pg.locator(".ftcard").inner_text().replace("\n"," | "))
    print("my flights:",pg.locator('[data-fold^="flights"]').locator("xpath=..").inner_text().replace("\n"," | ")[:400])
    pg.clock.set_system_time(datetime.datetime(2026,11,13,10,0)); pg.click("[data-tab=today]"); print("ADTY today:",pg.inner_text("main header").replace("\n"," "),"|",pg.inner_text(".pass").replace("\n"," "))
    print("ERRORS:",errs or "none")
