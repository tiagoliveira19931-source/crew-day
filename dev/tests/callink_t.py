# Roster from a private calendar link: fetched by the phone straight from the airline, refreshed when online.
# The link and calendar here are made up.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]; ics=open("roster2.ics").read(); hits=[]
def route(r):
    u=r.request.url
    if u.startswith("https://crew.example/cal/"):
        hits.append(u)
        if "broken" in u: return r.abort()
        return r.fulfill(body=ics,content_type="text/calendar",headers={"Access-Control-Allow-Origin":"*"})
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",route)
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.select_option("#pr-al","Jet2"); pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#cal-u","webcal://crew.example/cal/abc123.ics"); pg.click("#calsave"); pg.wait_for_timeout(800)
    m=pg.inner_text("#rostmsg"); print(m); assert "Imported" in m and "calendar link" in m, m
    assert hits and hits[0].startswith("https://"), hits
    assert pg.locator("#calget").count()==1 and "Last updated" in pg.inner_text("main")
    # a link the phone can't read shows the other ways in
    pg.fill("#cal-u","https://crew.example/cal/broken.ics"); pg.click("#calget"); pg.wait_for_timeout(800)
    m=pg.inner_text("#rostmsg"); print(m); assert "couldn't read" in m; assert "another way" in pg.inner_text("main")
    assert "Shortcuts" in pg.inner_text("main")
    # calendar data pasted from an iPhone Shortcut imports like a file
    pg.fill("#rost-p",ics); pg.click("#pasteroster"); pg.wait_for_timeout(300); m=pg.inner_text("#rostmsg"); print(m); assert "from your calendar" in m, m
    pg.click("#caldel"); pg.wait_for_timeout(100); assert pg.locator("#calsave").count()==1
    # UK CAA wording for Jet2
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="hours"]'); pg.wait_for_timeout(150); h=pg.inner_text("main"); assert "UK CAA" in h and "EASA guide" not in h
    b.close()
print("ERRORS:", errs or "none")
