import datetime,re
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
js=open("rp_t.js").read()
row=re.search(r"const row=`([\s\S]*?)`;",js).group(1); cal=re.search(r"const cal=`([\s\S]*?)`;",js).group(1)
row2=row.replace("16:10 Z","16:40 Z").replace("19:00 Z","19:30 Z").replace("15:25 Z","15:55 Z")
cal2=cal.replace("OFF OFF OFF 4 HSBY 4 2","OFF OFF OFF 4 HSBY OFF 2")
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,0,5))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(200)
    pg.fill("#rost-p",cal+"\n"+row); pg.click("#pasteroster"); pg.wait_for_timeout(200); print("first:",pg.inner_text("#rostmsg"))
    pg.fill("#rost-p",cal2+"\n"+row2); pg.click("#pasteroster"); pg.wait_for_timeout(200); print("second:",pg.inner_text("#rostmsg"))
    c=pg.locator("section:has(h2:text('Roster changes'))").first
    print("card:",c.inner_text().replace("\n"," | ")); c.screenshot(path="/tmp/chg.png")
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    print("today has card:", pg.locator("h2:text('Roster changes')").count())
    pg.click("[data-chseen]"); pg.wait_for_timeout(100); print("after got it:", pg.locator("h2:text('Roster changes')").count())
    b.close()
print("ERRORS:", errs or "none")
