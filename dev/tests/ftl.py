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
    def F(l):
        pg.click("[data-tab=today]")
        if pg.locator('[data-fold^="ftl"][aria-expanded="false"]').count(): pg.click('[data-fold^="ftl"]')
        print(l, pg.locator('[data-fold^="ftl"]').inner_text().replace("\n"," "),"||",pg.locator(".fbody .sbnow").last.inner_text().replace("\n"," "),"|",pg.locator(".fbody p").filter(has_text="shrink").first.inner_text() if pg.locator(".fbody p").filter(has_text="shrink").count() else "")
    F("09:00")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,12,0)); F("12:00")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,18,0)); F("18:00")
    pg.locator(".fbody").last.screenshot(path="/tmp/ftl.png")
    pg.click("#called"); F("called 18:00")
    print("ERRORS:",errs or "none")
