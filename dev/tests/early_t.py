import datetime,re
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
js=open("rp_t.js").read(); row=re.search(r"const row=`([\s\S]*?)`;",js).group(1)
bus="""Monday to Friday
05:05 → 05:50
05:35 → 06:20
06:05 → 06:50
"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,2,6))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change")
    F("#tr-from-bus","Harlow"); F("#tr-walk-bus","5"); F("#tr-out-bus",bus); F("#tr-buf-bus","10")
    pg.click("#setupdone")
    pg.evaluate("()=>0")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(200)
    pg.fill("#rost-p",row); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    pg.click("[data-tab=plan]"); pg.wait_for_timeout(200)
    # choose bus for today via the data attribute if present
    sel='[data-tmode="2026-11-12|bus"]'
    print("bus option present:", pg.locator(sel).count())
    if pg.locator(sel).count(): pg.click(sel)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    pg.click('[data-goto^="today:travel"]'); pg.wait_for_timeout(150)
    pg.select_option("#d-mode","bus"); pg.wait_for_timeout(200)
    print("pass:", pg.inner_text('[aria-label="Your duty"]').replace("\n"," "))
    print("why:", pg.locator('[aria-label="Your duty"]').locator("xpath=following-sibling::p[1]").inner_text())
    # now with a full timetable
    pg.evaluate("()=>0")
    b.close()
print("ERRORS:", errs or "none")
