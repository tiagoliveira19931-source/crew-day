import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read()
errs=[];posts=[]
def handle(r):
    u=r.request.url
    if "formResponse" in u: posts.append(r.request.post_data); return r.fulfill(status=200,body="ok")
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",handle)
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="issues"]'); pg.wait_for_timeout(100)
    print("in issues:", pg.locator("#is-t").count())
    pg.click("[data-tab=more]"); pg.wait_for_timeout(100); print("back to menu:", pg.locator('[data-more="issues"]').count()>0)
    pg.click('[data-more="issues"]')
    ctx.set_offline(True)
    pg.fill("#is-t","Timer did not ring"); pg.click("#issend"); pg.wait_for_timeout(300)
    print("offline msg:", pg.inner_text('[role="status"]'), "| chip:", pg.locator(".chip").all_inner_texts(), "| posts:", len(posts))
    ctx.set_offline(False); pg.evaluate("window.dispatchEvent(new Event('online'))"); pg.wait_for_timeout(2500)
    print("after online posts:", posts, "| chip:", pg.locator(".chip").all_inner_texts())
    b.close()
print("ERRORS:", errs or "none")
