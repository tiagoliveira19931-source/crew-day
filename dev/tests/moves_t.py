# Exercises: every exercise has its small line drawing.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    f=pg.locator('[data-fold^="moves"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    pg.wait_for_timeout(150); n=pg.locator(".expic").count(); ex=pg.locator(".ex b").count(); print("pictures",n)
    assert n==12, n
    b.close()
print("ERRORS:", errs or "none")
