import datetime,re
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
gem="""Tuesday, 17 Nov 26: Day Off (OFF) from 00:00 Z to 21:00 Z.
​Wednesday, 18 Nov 26: Home Standby (HSBY) at Stansted (STN) from 04:00 Z (04:00 LT) to 13:30 Z (13:30 LT).
​Thursday, 19 Nov 26: Training (CRMS) at Stansted (STN):
​Check-in: 08:00 Z (08:00 LT)
​Training Duty: 08:00 Z to 17:25 Z (17:25 LT)
​Check-out: 17:25 Z (17:25 LT)
Friday, 20 Nov 26: Duty at Stansted (STN):
Check-in: 05:30 Z (05:30 LT)
Flight FR1234 from STN to AGP, 06:15 Z to 09:05 Z, aircraft EIDCL
Flight FR1235 from AGP to STN, 09:40 Z to 12:35 Z, aircraft EIDCL
Check-out: 13:05 Z (13:05 LT)"""
js=open("rp_t.js").read(); row=re.search(r"const row=`([\s\S]*?)`;",js).group(1)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,12,1,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(200)
    for txt in [gem,row]:
        pg.fill("#rost-p",txt); pg.click("#pasteroster"); pg.wait_for_timeout(200); print("msg:",pg.inner_text("#rostmsg"))
    def show(d):
        pg.click(f'[data-pick="{d}"]'); pg.wait_for_timeout(120)
        v=lambda i: pg.input_value(f"#{i}") if pg.locator(f"#{i}").count() else "-"
        print(d, pg.locator('[data-setkind][aria-checked="true"]').all_inner_texts(), [v(i) for i in ["rw-r","rw-o","sc-flt-0","sc-from-0","sc-to-0","sc-dep-0","sc-arr-0","sc-reg-0","sc-flt-1","sc-dep-1"]])
    for d in ["2026-11-12","2026-11-13","2026-11-17","2026-11-18","2026-11-19","2026-11-20"]: show(d)
    b.close()
print("ERRORS:", errs or "none")
