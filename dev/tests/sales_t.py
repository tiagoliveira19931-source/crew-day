# Sales log: crew can tick "sales target met" for a flight; the app never asks for or sets a target. Made-up figures.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,15,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.evaluate("()=>{}")
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    if pg.locator('[data-more="money"]').count()==0:
        pg.click('[data-more="profile"]'); pg.wait_for_timeout(100)
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="money"]'); pg.wait_for_timeout(150)
    pg.click('[data-mv="sales"]'); pg.wait_for_timeout(150)
    t=pg.inner_text("main")
    assert "Sales target met on this flight" in t and "(optional)" in t, t[:400]
    assert pg.locator("input[type=number][id*=tgt], #s-target").count()==0, "no target amount field"
    pg.fill("#s-fl","FR146"); pg.fill("#s-amt","120"); pg.check("#s-tgt"); pg.click("#addsale"); pg.wait_for_timeout(150)
    pg.fill("#s-fl","FR147"); pg.fill("#s-amt","80"); pg.click("#addsale"); pg.wait_for_timeout(150)
    t=pg.inner_text("main")
    assert t.upper().count("TARGET ✓")==1, t
    assert "target met on 1" in t, t
print("ERRORS:", "; ".join(errs) if errs else "none")
