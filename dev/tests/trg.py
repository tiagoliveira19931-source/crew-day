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
    # duty day with flights
    pg.click('[data-pick="2026-11-14"]'); pg.click('[data-setkind=flying]'); pg.click('[data-addsec="2026-11-14"]')
    pg.fill("#sc-flt-0","FR7633"); pg.fill("#sc-reg-0","ei-dcl"); pg.fill("#sc-to-0","AGP"); pg.fill("#sc-dep-0","07:00"); pg.fill("#sc-arr-0","10:45"); pg.click('[data-saveday="2026-11-14"]')
    print("duty saved:", pg.input_value("#rw-r"), pg.inner_text(".seccard").replace("\n"," ")[-120:])
    pg.locator("main section.card").filter(has=pg.locator("#rw-r")).screenshot(path="/tmp/rost_duty.png")
    # off day hides fields
    pg.click('[data-pick="2026-11-15"]'); pg.click('[data-setkind=off]'); print("off fields:",pg.locator("#rw-r").count(),pg.locator("#rw-d").count(),pg.locator("#rw-n").count())
    # training
    pg.click('[data-pick="2026-11-12"]'); pg.click('[data-setkind=training]'); pg.fill("#rw-r","09:00"); pg.fill("#rw-o","17:00"); pg.fill("#rw-l","Ryanair hangar, Stansted"); pg.fill("#rw-n","Recurrent SEP"); pg.click('[data-saveday="2026-11-12"]')
    print("roster TRG:", "TRG" in pg.inner_text("main"))
    pg.locator("main section.card").filter(has=pg.locator("#rw-r")).screenshot(path="/tmp/rost_trg.png")
    for hh,mm in [(7,30),(8,20),(11,0),(17,30)]:
        pg.clock.set_system_time(datetime.datetime(2026,11,12,hh,mm)); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None; pg.click("[data-tab=today]"); pg.wait_for_timeout(100); pg.click("[data-tab=today]")
        print(f"{hh:02}:{mm:02}",pg.inner_text("main header").replace("\n"," "),"|",pg.inner_text(".nudges").replace("\n"," | ")[:160] if pg.locator(".nudges").count() else "-")
        if hh==11: pg.screenshot(path="/tmp/trg_today.png")
    print("ERRORS:",errs or "none")
