# Updates: a new version published while the app is open loads without needing two app opens.
import subprocess, tempfile, socket, os, sys, threading, http.server, functools
from playwright.sync_api import sync_playwright
src=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","crew-day.html")); build=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","build.py"))
d=tempfile.mkdtemp(); errs=[]
subprocess.run(["python3",build,src,d,"9.0.1"],check=True,capture_output=True)
s=socket.socket();s.bind(("127.0.0.1",0));port=s.getsockname()[1];s.close()
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(("127.0.0.1",port),functools.partial(Q,directory=d)); threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_context().new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{port}/"); pg.wait_for_timeout(2500); pg.reload(); pg.wait_for_timeout(1500)
    assert pg.evaluate("window.CREWDAY_VERSION")=="9.0.1"
    subprocess.run(["python3",build,src,d,"9.0.2"],check=True,capture_output=True)
    if pg.locator("#pr-n").count(): pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click("#chkupd"); pg.wait_for_timeout(5000)
    v=pg.evaluate("window.CREWDAY_VERSION"); print("after check:",v); assert v=="9.0.2", v
    b.close()
srv.shutdown()
print("ERRORS:", errs or "none")
