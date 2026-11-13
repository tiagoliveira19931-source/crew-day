# Food ideas: daily mix, "more ideas", liquids warning and security note.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=plan]"); pg.wait_for_timeout(200)
    f=pg.locator('[data-fold^="food"]'); assert f.count(), "no food section"
    if f.get_attribute("aria-expanded")=="false": f.click()
    pg.wait_for_timeout(150)
    box=f.locator("xpath=..").inner_text()
    print(box.replace("\n"," | ")[:900])
    assert "More ideas" in box and "Security" in box.upper() or "SECURITY" in box, "missing parts"
    assert "100 ml" in box
    b.close()
print("ERRORS:", errs or "none")
