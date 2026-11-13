import datetime,json,re
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
js=open("rp_t.js").read()
row=re.search(r"const row=`([\s\S]*?)`;",js).group(1); cal=re.search(r"const cal=`([\s\S]*?)`;",js).group(1)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,0,5))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(200)
    pg.fill("#rost-p",cal); pg.click("#pasteroster"); pg.wait_for_timeout(200); print("msg1:",pg.inner_text("#rostmsg"))
    pg.fill("#rost-p",row); pg.click("#pasteroster"); pg.wait_for_timeout(200); print("msg2:",pg.inner_text("#rostmsg"))
    pg.click('[data-pick="2026-11-12"]'); pg.wait_for_timeout(150)
    print("12th:",[pg.input_value(f"#{i}") for i in ["rw-r","rw-o","sc-flt-0","sc-from-0","sc-to-0","sc-dep-0","sc-arr-0","sc-reg-0","sc-flt-1","sc-dep-1","sc-arr-1"]])
    pg.click('[data-pick="2026-11-11"]'); pg.wait_for_timeout(150); print("11th:",pg.input_value("#rw-r"),pg.input_value("#rw-o"))
    for t in ["plan","me","trip"]:
        pg.click(f"[data-tab={t}]"); pg.wait_for_timeout(150)
    print("trip folds:",[x.inner_text().split("\n")[0] for x in pg.locator("main .foldh").all()])
    pg.click("[data-tab=today]"); print("today:",pg.inner_text("main")[:200].replace("\n"," | "))
    b.close()
print("ERRORS:", errs or "none")
