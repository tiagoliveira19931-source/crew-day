# Snacks: picked for each duty day with variety, changeable, and added to the shopping list.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="""2026-11-16 | DUTY | 05:30 | 13:00 | FR1 STN-DUB 06:15-07:30; FR2 DUB-STN 08:00-09:15
2026-11-17 | DUTY | 05:45 | 13:10 | FR3 STN-AGP 06:30-09:20; FR4 AGP-STN 09:50-12:40
2026-11-18 | OFF | | |
2026-11-19 | DUTY | 13:00 | 22:30 | FR5 STN-BCN 13:45-16:00; FR6 BCN-STN 16:40-19:00
2026-11-21 | DUTY | 21:00 | 05:30 | FR7 STN-TFS 21:45-02:10; FR8 TFS-STN 02:50-07:10"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,16,1,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="meals"]'); pg.wait_for_timeout(200)
    sn={}
    for d in ["2026-11-16","2026-11-17","2026-11-18","2026-11-19","2026-11-21"]:
        L=pg.locator(f'[data-msnack^="{d}|"]'); sn[d]=[L.nth(i).input_value() for i in range(L.count())]
    print("snacks:",sn)
    assert len(sn["2026-11-16"])==2 and len(sn["2026-11-21"])==3 and not sn["2026-11-18"]
    allv=[x for v in sn.values() for x in v]; assert len(set(allv))==len(allv), "no snack repeated in the week"
    n=pg.locator('[data-msnack="2026-11-16|0"] option').count()-1; print("snack choices:",n); assert n>=36
    pg.select_option('[data-msnack="2026-11-16|0"]',"Two boiled eggs"); pg.wait_for_timeout(100)
    t=pg.inner_text("main").replace("\n"," "); i=t.find("Shopping list"); print(t[i:i+500])
    assert "Two boiled eggs" in t[i:], "snack ingredients should be on the shopping list"
    pg.click("[data-tab=plan]"); pg.wait_for_timeout(200)
    f=pg.locator('[data-fold^="food"]')
    if f.count() and f.get_attribute("aria-expanded")=="false": f.click()
    pg.wait_for_timeout(100); ft=f.locator("xpath=..").inner_text(); assert "Your snacks" in ft or "YOUR SNACKS" in ft, ft[:300]
    b.close()
print("ERRORS:", errs or "none")
