# Trip notebook (notes + tick-box list, one per trip, can be saved to Documents) and Documents folders.
import datetime, os, tempfile
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
PAGE="<!doctype html><html><head><meta charset=utf-8></head><body><script>window.CREWDAY_PWA=true</script>"+html+"</body></html>"
d=tempfile.mkdtemp(); pdf=os.path.join(d,"uniform-policy.pdf"); open(pdf,"wb").write(b"%PDF-1.4\n%made up\n")
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.fulfill(body=PAGE,content_type="text/html") if r.request.url=="https://t.test/" else r.abort())
    pg.clock.install(time=datetime.datetime(2026,11,14,10,0)); pg.goto("https://t.test/")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p","2026-11-14 | DUTY | 12:45 | 18:00 | FR147 STN-BER 13:30-15:15; FR146 BER-STN 15:40-17:30"); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    pg.click("[data-tab=today]"); pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    f=pg.locator('[data-fold="notebook"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    pg.fill("#nb-t","Captain prefers tea, no sugar"); pg.locator("#nb-t").dispatch_event("change")
    pg.fill("#nb-i","Buy water"); pg.press("#nb-i","Enter"); pg.wait_for_timeout(100)
    pg.fill("#nb-i","Charge the PA handset"); pg.click("#nbadd"); pg.wait_for_timeout(100)
    pg.locator("[data-nbtick]").first.check(); pg.wait_for_timeout(100)
    assert pg.locator("[data-nbtick]").count()==2 and pg.locator("[data-nbtick]:checked").count()==1
    pg.click("#nbsave"); pg.wait_for_timeout(800); print(pg.inner_text("main").split("Saved to Documents")[1][:60] if "Saved to Documents" in pg.inner_text("main") else "NOT SAVED")
    assert "Notes-BER-2026-11-14.txt" in pg.inner_text("main")
    # Documents: the note is in Trip notes; make a folder, add a PDF, delete it
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="files"]'); pg.wait_for_timeout(150); t=pg.inner_text("main"); assert "Self-certificates" in t and "Trip notes" in t
    pg.locator('[data-docopen]').filter(has_text="Trip notes").click(); pg.wait_for_timeout(150); assert "Notes-BER-2026-11-14.txt" in pg.inner_text("main")
    pg.click('[data-docopen=""]'); pg.fill("#doc-nf","Uniform"); pg.click("#docnew"); pg.wait_for_timeout(100)
    pg.locator('[data-docopen]').filter(has_text="Uniform").click(); pg.wait_for_timeout(100)
    pg.set_input_files("#doc-add",[pdf]); pg.wait_for_timeout(800); t=pg.inner_text("main"); assert "uniform-policy.pdf" in t and "Saved 1 file" in t, t[:400]
    pg.locator("[data-docdelf]").first.click(); pg.locator("[data-docdelf]").first.click(); pg.wait_for_timeout(200); assert "uniform-policy.pdf" not in pg.inner_text("main")
    # a later trip gets a fresh notebook, the old one stays selectable
    pg.fill("#rost-p","2026-11-20 | DUTY | 06:05 | 16:55 | FR2232 STN-NTE 06:50-08:15") if pg.locator("#rost-p").count() else None
    b.close()
print("ERRORS:", errs or "none")
