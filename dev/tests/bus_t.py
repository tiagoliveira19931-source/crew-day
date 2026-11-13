import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); tt=open("ttin.txt").read(); errs=[]
bus="""Monday to Friday
04:50 → 05:25
xx:20 → xx:55 (05:00 – 23:00)
"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,18,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change")
    F("#tr-walk-train","12"); F("#tr-out-train",tt); F("#tr-buf-train","10")
    F("#tr-from-bus","Harlow"); F("#tr-walk-bus","5"); F("#tr-out-bus",bus); F("#tr-buf-bus","10")
    print("bus read:",pg.locator("#tr-out-bus").locator("xpath=..").locator(".note").first.inner_text())
    pg.click("#setupdone"); pg.click("[data-tab=plan]"); F("#n-rep","07:00")
    ch=lambda: pg.locator(".seccard").filter(has_text="How are you getting there").inner_text().replace("\n"," | ")
    print("choice:",ch())
    pg.click('[data-tmode="2026-11-12|bus"]'); print("bus card:",pg.locator(".seccard").filter(has_text="Your bus").inner_text().replace("\n"," | ")[:220])
    pg.clock.set_system_time(datetime.datetime(2026,11,13,9,50)); pg.click("[data-tab=today]")
    pg.click("#etopen"); pg.click('[data-etkind="standby"]'); pg.fill("#et-s","09:00"); pg.fill("#et-e","17:00"); pg.click("#etsave")
    print("before call:",pg.locator("section.card").filter(has_text="Been called?").locator("p").last.inner_text())
    pg.click("#called"); pg.wait_for_timeout(100)
    print("called:",pg.locator(".nudges").inner_text().replace("\n"," | ").split("Grab and go")[1][-520:])
    print("ERRORS:",errs or "none")
