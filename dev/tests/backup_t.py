# Backup locked with a password: the file can't be read without it, and restores with it.
import datetime, json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="2026-11-16 | DUTY | 05:30 | 13:00 | FR1 STN-DUB 06:15-07:30; FR2 DUB-STN 08:00-09:15"
SP="/tmp/claude-0/-home-claude/826586fa-4961-5511-84d6-a37445adb4b2/scratchpad/"
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":390,"height":844},accept_downloads=True); pg=ctx.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); PAGE="<!doctype html><html><head><meta charset=utf-8></head><body><script>window.CREWDAY_PWA=true;navigator.canShare=undefined</script>"+html+"</body></html>"
    pg.route("**/*",lambda r:r.fulfill(body=PAGE,content_type="text/html") if r.request.url=="https://crewday.test/" else r.abort())
    pg.clock.install(time=datetime.datetime(2026,11,13,1,0))
    pg.goto("https://crewday.test/")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    t=pg.inner_text("main"); assert "No backup yet" in t, t[:400]
    pg.click('[data-more="backup"]'); pg.wait_for_timeout(150)
    pg.fill("#bk-pw","abc"); pg.click("#dobackup"); pg.wait_for_timeout(200); assert "at least 6" in pg.inner_text("#bkmsg")
    pg.fill("#bk-pw","stansted26")
    pg.evaluate("window.__f=null;window.offerFile=null");
    pg.evaluate("document.addEventListener('click',e=>{const a=e.target.closest&&e.target.closest('a[download]');if(a)window.__dl=a.href},true)")
    try:
        with pg.expect_download(timeout=8000) as dl: pg.click("#dobackup")
    except Exception as e:
        print("bkmsg:",pg.inner_text("#bkmsg"), errs); print(pg.evaluate("(async()=>{try{const k=await SEC.derive('abcdef',new Uint8Array(16));return 'ok'}catch(e){return String(e)}})()")); raise
    path=SP+"bk.json"; dl.value.save_as(path); raw=open(path).read(); j=json.loads(raw)
    print("locked:",j.get("locked"), "has name in clear:", "Tiago" in raw or "FR1" in raw)
    assert j.get("locked") and "Tiago" not in raw and "FR1" not in raw
    # restore with the wrong then right password
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    assert "Last backup today" in pg.inner_text("main")
    pg.click('[data-more="backup"]'); pg.wait_for_timeout(150)
    pg.evaluate("localStorage.setItem('x','1')")
    pg.set_input_files("#bk-file",path); pg.click("#dorestore"); pg.click("#dorestore"); pg.wait_for_timeout(400)
    assert "locked" in pg.inner_text("#rsmsg")
    pg.fill("#bk-pin","wrongpass"); pg.click("#dorestore"); pg.click("#dorestore"); pg.wait_for_timeout(1500); print(pg.inner_text("#rsmsg")); assert "doesn't open" in pg.inner_text("#rsmsg")
    pg.fill("#bk-pin","stansted26"); pg.click("#dorestore"); pg.click("#dorestore"); pg.wait_for_timeout(1500); print(pg.inner_text("#rsmsg")); assert "Restored" in pg.inner_text("#rsmsg")
    b.close()
print("ERRORS:", errs or "none")
