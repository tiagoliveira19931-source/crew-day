import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,12,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.click('[data-pick="2026-11-11"]'); pg.click('[data-setkind=flying]'); pg.fill("#rw-r","14:00"); pg.fill("#rw-o","23:30"); pg.click('[data-saveday="2026-11-11"]')
    pg.click('[data-pick="2026-11-12"]'); pg.click('[data-setkind=flying]'); pg.fill("#rw-r","10:00"); pg.fill("#rw-o","18:00"); pg.click('[data-saveday="2026-11-12"]')
    pg.click('[data-more=""]'); pg.click("[data-tab=plan]")
    if pg.locator("[data-usenext]").count(): pg.click("[data-usenext]")
    print("plan:",[l for x in pg.locator("main section.card").all_inner_texts() for l in x.split("\n") if "Rest before" in l])
    pg.click("[data-tab=more]"); pg.click('[data-more="hours"]')
    pg.fill("#rc-r","14:00"); pg.locator("#rc-r").dispatch_event("change"); pg.fill("#rc-o","23:30"); pg.locator("#rc-o").dispatch_event("change")
    card=lambda: pg.locator("section.card").filter(has_text="Rest calculator").inner_text().replace("\n"," | ")
    print("home:",card()[:220])
    pg.click('[data-rcaway="1"]'); print("away:",card()[:220])
    pg.fill("#rc-n","08:00"); pg.locator("#rc-n").dispatch_event("change"); print("check 08:00:",card()[150:400])
    print("ERRORS:",errs or "none")
