import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); tt=open("ttin.txt").read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,18,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    pg.fill("#t-com","35"); pg.locator("#t-com").dispatch_event("change")
    pg.fill("#tr-walk-train","12"); pg.locator("#tr-walk-train").dispatch_event("change")
    pg.fill("#tr-out-train",tt); pg.locator("#tr-out-train").dispatch_event("change")
    pg.fill("#tr-buf-train","10"); pg.locator("#tr-buf-train").dispatch_event("change")
    pg.click("#setupdone"); pg.click("[data-tab=plan]"); pg.fill("#n-rep","07:00"); pg.locator("#n-rep").dispatch_event("change")
    ch=lambda: pg.locator(".seccard").filter(has_text="How are you getting there").inner_text().replace("\n"," | ")
    print("choice (usual car):",ch())
    if pg.locator('[data-fold="alarms"][aria-expanded="false"]').count(): pg.click('[data-fold="alarms"]')
    lv=lambda: [t for t in pg.locator(".step .t, .tip .t").all_inner_texts()][:1]
    pg.click('[data-tmode="2026-11-12|train"]'); print("after pick train:",ch()); print("train card:",pg.locator(".seccard").filter(has_text="Your train").inner_text().replace("\n"," | ")[:200])
    pg.clock.set_system_time(datetime.datetime(2026,11,13,9,50)); pg.click("[data-tab=today]")
    pg.click("#etopen"); pg.click('[data-etkind="standby"]'); pg.fill("#et-s","09:00"); pg.fill("#et-e","17:00"); pg.click("#etsave")
    pg.click("#called"); pg.wait_for_timeout(100)
    print("called:",pg.locator(".nudges").inner_text().replace("\n"," | ")[-330:])
    print("ERRORS:",errs or "none")
