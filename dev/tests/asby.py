import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
def H(pg): return [h.inner_text() for h in pg.locator("main h1, main h2, main .foldh .ft").all()]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,15,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]')
    pg.click('[data-pick="2026-11-12"]'); pg.click('[data-setkind=asby]'); pg.fill("#rw-r","05:00"); pg.fill("#rw-o","11:00"); pg.click("[data-saveday]")
    print("roster cell:", "ASBY" in pg.inner_text("main"))
    pg.click('[data-more=""]'); pg.click("[data-tab=plan]")
    print("plan:",H(pg)[:3], "| suggest:", pg.locator("[data-usenext]").count())
    if pg.locator("[data-usenext]").count(): pg.click("[data-usenext]")
    print("plan seg:",pg.locator('[data-nkind][aria-pressed=true]').inner_text(),"| end:",pg.input_value("#n-end"))
    pg.locator("main section.card").nth(0).screenshot(path="/tmp/asby_plan.png")
    for hh,mm in [(2,30),(4,0),(6,0)]:
        pg.clock.set_system_time(datetime.datetime(2026,11,12,hh,mm)); pg.click("[data-tab=today]")
        print(f"{hh:02}:{mm:02}",pg.inner_text("main header").replace("\n"," "),"|",pg.inner_text(".nowcard").replace("\n"," ")[:90])
    print("  nudges:",pg.inner_text(".nudges").replace("\n"," | ") if pg.locator(".nudges").count() else "none")
    pg.screenshot(path="/tmp/asby_today.png")
    pg.click("#asbycall"); print("called:",pg.inner_text(".nowcard").replace("\n"," ")[:80])
    pg.click('[data-fold^="details"]'); print("  note:", "Called from airport standby" in pg.inner_text("main"))
    pg.clock.set_system_time(datetime.datetime(2026,11,12,12,0)); pg.click("[data-tab=today]"); print("12:00 still on duty:",pg.inner_text(".nowcard").replace("\n"," ")[:60] if pg.locator(".nowcard").count() else H(pg)[:3])
    print("ERRORS:",errs or "none")
