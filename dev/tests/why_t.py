import datetime,re
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
js=open("rp_t.js").read(); row=re.search(r"const row=`([\s\S]*?)`;",js).group(1)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,2,6))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(200)
    pg.fill("#rost-p",row); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    print("normal:", pg.inner_text('[aria-label="Your duty"]').replace("\n"," "), "|", pg.locator("main p.note").first.inner_text())
    # simulate a wrong journey time
    pg.click('[data-goto^="today:travel"]'); pg.wait_for_timeout(200)
    pg.fill("#d-com","380"); pg.locator("#d-com").dispatch_event("change"); pg.wait_for_timeout(200)
    print("big:", pg.inner_text('[aria-label="Your duty"]').replace("\n"," "))
    pg.wait_for_timeout(400)
    print(pg.locator('[aria-label="Your duty"]').locator("xpath=following-sibling::p[1]").inner_text())
    b.close()
print("ERRORS:", errs or "none")
