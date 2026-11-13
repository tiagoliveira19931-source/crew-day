# Preferred transport (Profile): train, bus or whichever is faster decides the suggested ride home.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="2026-11-13 | DUTY | 12:00 | 19:30 | FR1 STN-DUB 12:45-14:00; FR2 DUB-STN 14:30-19:00"
train="Monday to Friday\nxx:13 → xx:28 (06:00 – 23:00)\nReturn\nMonday to Friday\nxx:40 → xx:55 (06:00 – 23:59)\n"
bus="Monday to Sunday\nxx:20 → xx:55 (00:00 – 23:59)\nReturn\nMonday to Sunday\nxx:05 → xx:40 (00:00 – 23:59)\n"
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(80)
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    F("#tr-from-train","Bishops Stortford"); F("#tr-walk-train","5"); F("#tr-out-train",train)
    F("#tr-from-bus","Harlow"); F("#tr-walk-bus","5"); F("#tr-out-bus",bus)
    pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    def gm():
        pg.click("[data-tab=more]"); pg.wait_for_timeout(60)
        if pg.locator('[data-more=""]').count(): pg.click('[data-more=""]')
    def setpref(v):
        gm(); pg.click('[data-more="profile"]'); f=pg.locator('[data-fold^="pf_travel"]')
        if f.get_attribute("aria-expanded")=="false": f.click()
        pg.click(f'[data-tpref="{v}"]'); pg.wait_for_timeout(80)
        if pg.locator("#t-mode").count(): pg.select_option("#t-mode","train")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,19,10)); pg.wait_for_timeout(1200)
    res={}
    for v in ["train","bus","fastest"]:
        setpref(v); pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
        t=pg.inner_text("main").replace("\n"," "); i=t.find("Take:"); res[v]=t[i:i+40]; print(v,"→",res[v])
    assert "train" in res["train"] and "bus" in res["bus"], res
    b.close()
print("ERRORS:", errs or "none")
