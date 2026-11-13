import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.select_option("#pr-al","Jet2"); pg.fill("#pr-n","Ana"); pg.fill("#pr-s","12345")
    print("callout default:",pg.input_value("#t-co"))
    pg.fill("#t-com","55"); pg.locator("#t-com").dispatch_event("change"); pg.fill("#t-rb","60"); pg.locator("#t-rb").dispatch_event("change")
    pg.locator("section.card").first.screenshot(path="/tmp/setup.png")
    pg.click("#setupdone")
    pg.click("#etopen"); pg.click('[data-etkind="standby"]'); pg.fill("#et-s","10:30"); pg.fill("#et-e","20:30"); pg.click("#etsave")
    print("today:",pg.inner_text("main header").replace("\n"," "),"| folds:",[x.inner_text().split("\n")[0] for x in pg.locator("main .foldh").all()])
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None; pg.click('[data-more="profile"]'); pg.click('[data-fold^="pf_times"]'); pg.click('[data-fold^="pf_travel"]'); print("me times:",pg.input_value("#t-com"),pg.input_value("#t-rb"),pg.input_value("#t-co"))
    print("ERRORS:",errs or "none")
