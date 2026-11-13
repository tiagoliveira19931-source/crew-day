import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
gem="""Here is your roster:

2026-11-11 | HSBY | 05:00 | 13:00 |
2026-11-12 | DUTY | 12:50 | 23:25 | FR2812 STN-LPA 13:35-18:00 9HQAG; FR2811 LPA-STN 18:35-22:55 9HQAG
**2026-11-13 | DUTY | 15:25Z | 22:45Z | FR1882 STN-LIS 16:10-19:00 EIEKL; FR1883 LIS-STN 19:25-22:15 EIEKL**
2026-11-14 | 2 | | |
2026-11-15 | OFF | | |
2026-11-19 | TRNG | | |
2026-11-30 | L | | |"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,10,20,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(200)
    pg.click("#copygem"); pg.wait_for_timeout(200)
    print("copy btn:", pg.inner_text("#copygem"), "| fallback box:", pg.locator("#gemp").count())
    pg.fill("#rost-p",gem); pg.click("#pasteroster"); pg.wait_for_timeout(200); print("msg:",pg.inner_text("#rostmsg"))
    def show(d):
        pg.click(f'[data-pick="{d}"]'); pg.wait_for_timeout(120)
        v=lambda i: pg.input_value(f"#{i}") if pg.locator(f"#{i}").count() else "-"
        print(d, [v(i) for i in ["rw-r","rw-o","sc-flt-0","sc-from-0","sc-to-0","sc-dep-0","sc-arr-0","sc-reg-0","sc-flt-1"]], pg.locator('[data-setkind][aria-checked="true"]').all_inner_texts())
    for d in ["2026-11-11","2026-11-12","2026-11-13","2026-11-14","2026-11-15","2026-11-19","2026-11-30"]: show(d)
    b.close()
print("ERRORS:", errs or "none")
