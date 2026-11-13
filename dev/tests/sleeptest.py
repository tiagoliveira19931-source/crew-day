import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,12,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone"); pg.click("[data-tab=plan]")
    def show(rep):
        pg.fill("#n-rep",rep); pg.locator("#n-rep").dispatch_event("change")
        if pg.locator('[data-fold="planday"][aria-expanded="false"]').count(): pg.click('[data-fold="planday"]')
        box=pg.locator('[data-fold="planday"]').locator("xpath=..")
        tips=[x.inner_text().replace("\n"," ") for x in box.locator(".tip").all()]
        ps=box.locator("p").all_inner_texts()
        print(f"REPORT {rep}:",ps[:1],tips)
    for r in ["05:30","09:30","15:00","22:30"]: show(r)
    # late finish today (roster) then early tomorrow
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.click('[data-pick="2026-11-11"]'); pg.click('[data-setkind=flying]'); pg.fill("#rw-r","15:00"); pg.fill("#rw-o","23:40"); pg.click('[data-saveday="2026-11-11"]'); pg.click('[data-more=""]'); pg.click("[data-tab=plan]")
    show("10:00")
    print("ERRORS:",errs or "none")
