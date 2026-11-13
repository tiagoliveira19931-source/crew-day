import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
txt=open("full.txt").read()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,2,15))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(200)
    pg.fill("#rost-p",txt); pg.click("#pasteroster"); pg.wait_for_timeout(200); print("msg:",pg.inner_text("#rostmsg"))
    pg.click('[data-pick="2026-11-12"]'); pg.wait_for_timeout(100); pg.evaluate("()=>window.scrollTo(0,0)")
    print("summary:",pg.inner_text('[aria-label="Month summary"]').replace("\n"," "))
    print("cells:",[x.inner_text().replace("\n"," ") for x in pg.locator('[data-pick^="2026-11-1"],[data-pick^="2026-11-2"],[data-pick^="2026-11-3"]').all()][3:])
    pg.locator('[data-pick="2026-11-16"]').locator("xpath=../..").screenshot(path="/tmp/full.png")
    b.close()
print("ERRORS:", errs or "none")
