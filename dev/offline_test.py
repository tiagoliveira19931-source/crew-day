import subprocess, time, sys
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,"-m","http.server","8765","--directory",sys.argv[1]],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1); errs=[]
try:
    with sync_playwright() as p:
        b=p.chromium.launch(); ctx=b.new_context(viewport={"width":390,"height":844})
        ctx.route("https://**/*",lambda r:r.abort())  # no internet in this sandbox
        pg=ctx.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto("http://localhost:8765/")
        pg.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller!==null",timeout=15000) if False else None
        pg.evaluate("navigator.serviceWorker.ready.then(()=>true)"); time.sleep(1.5)
        pg.reload(); time.sleep(0.5)
        print("controlled:",pg.evaluate("!!navigator.serviceWorker.controller"))
        print("manifest ok:",pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json()).then(j=>j.name)"))
        pg.click("[data-tab=more]"); print("tiles:",pg.locator(".tile b").all_inner_texts())
        print("status:",pg.inner_text("#status") if pg.locator("#status").count() else "n/a")
        ctx.set_offline(True)
        pg.reload(); time.sleep(0.5)
        print("offline title:",pg.title(),"| tabs:",pg.inner_text("#tabs").replace("\n"," "))
        pg.click("[data-tab=more]"); pg.click('[data-more="money"]'); print("offline money ok:",pg.locator("main h1").inner_text())
        pg.click("[data-tab=plan]"); print("offline plan:",pg.locator("main h1").inner_text())
        b.close()
finally:
    srv.terminate()
print("ERRORS:",errs or "none")
