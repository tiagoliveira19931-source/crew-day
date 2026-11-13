# Each airline the app knows: ID label, call-out default, flight codes on import, and the long-haul notice for Norse.
# All rosters here are made up: invented flights only, no real crew data.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
CASES=[
 ("Ryanair","60","Crew code","2026-11-20 | DUTY | 05:30 | 13:00 | FR1001 STN-DUB 06:15-07:30; FR1002 DUB-STN 08:00-09:15","FR1001"),
 ("Ryanair UK","60","Crew code","2026-11-20 | DUTY | 05:30 | 13:00 | RK1234 STN-BCN 06:15-08:30; RK1235 BCN-STN 09:10-11:25","RK1234"),
 ("Jet2","120","Staff number","2026-11-20 | DUTY | 05:30 | 13:00 | LS901 STN-PMI 06:15-08:40; LS902 PMI-STN 09:30-11:55","LS901"),
 ("Norse","90","Staff number","2026-11-20 | DUTY | 09:00 | 18:30 | N0701 LGW-JFK 10:30-18:15\n2026-11-22 | DUTY | 21:30 | 07:00 | N0702 JFK-LGW 23:00-06:40","N0701"),
]
with sync_playwright() as p:
    b=p.chromium.launch()
    for al,co,idl,rost,flt in CASES:
        pg=b.new_page(viewport={"width":390,"height":844})
        pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
        pg.clock.install(time=datetime.datetime(2026,11,18,9,0))
        pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
        pg.select_option("#pr-al",al); pg.wait_for_timeout(100)
        got=pg.input_value("#t-co"); page=pg.inner_text("main"); print(al,"| call-out",got,"|",idl in page)
        assert got==co, (al,got); assert idl in page, (al,"id label")
        pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
        pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
        pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(200)
        pg.click("[data-tab=today]"); pg.wait_for_timeout(100)
        pg.clock.set_system_time(datetime.datetime(2026,11,20,4,0)); pg.wait_for_timeout(1200)
        pg.click("[data-tab=trip]"); pg.wait_for_timeout(200); t=pg.inner_text("main")
        assert flt in t.replace(" ",""), (al,"flight on Trip",t[:300])
        pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
        if pg.locator('[data-more="hours"]').count():
            pg.click('[data-more="hours"]'); pg.wait_for_timeout(150); h=pg.inner_text("main")
            assert ("Long-haul isn't covered yet" in h)==(al=="Norse"), (al,"long-haul note"); print("  hours checked")
        pg.close()
    b.close()
print("ERRORS:", errs or "none")
