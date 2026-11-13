# Weekly meals: suggestions from the roster, changing a meal, shopping list totals, ticks, extras, and the meal showing in Plan.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="""2026-11-16 | DUTY | 05:30 | 13:00 | FR1 STN-DUB 06:15-07:30; FR2 DUB-STN 08:00-09:15
2026-11-17 | DUTY | 05:45 | 13:10 | FR3 STN-AGP 06:30-09:20; FR4 AGP-STN 09:50-12:40
2026-11-18 | OFF | | |
2026-11-19 | DUTY | 13:00 | 22:30 | FR5 STN-BCN 13:45-16:00; FR6 BCN-STN 16:40-19:00
2026-11-20 | HSBY | 04:00 | 13:30 |"""
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
    picks={d:pg.locator(f'[data-mplan="{d}"]').input_value() for d in ["2026-11-16","2026-11-17","2026-11-18","2026-11-19","2026-11-20"]}
    print("suggested:",picks)
    assert picks["2026-11-16"] and picks["2026-11-17"] and picks["2026-11-19"], "duty days need a meal"
    assert not picks["2026-11-18"], "day off should be empty"
    pg.select_option('[data-mplan="2026-11-16"]',"Pasta salad"); pg.wait_for_timeout(100)
    pg.select_option('[data-mplan="2026-11-17"]',"Pasta salad"); pg.wait_for_timeout(100)
    t=pg.inner_text("main")
    i=t.find("Prep plan"); print(t[i:i+200].replace("\n"," | "))
    assert "Make 2 portions" in t
    i=t.find("Shopping list"); print(t[i:i+400].replace("\n"," | "))
    assert "Wholewheat pasta 150 g" in t.replace("\n"," "), "pasta should total 150 g for two days"
    pg.click('[data-mgot="Wholewheat pasta|g"]'); pg.wait_for_timeout(100)
    assert pg.locator('[data-mgot="Wholewheat pasta|g"]').is_checked()
    pg.fill("#mx-t","Coffee"); pg.click("#mxadd"); pg.wait_for_timeout(100); assert "Coffee" in pg.inner_text("main")
    pg.click("[data-tab=plan]"); pg.wait_for_timeout(200)
    f=pg.locator('[data-fold^="food"]')
    if f.count() and f.get_attribute("aria-expanded")=="false": f.click()
    pg.wait_for_timeout(100); ft=f.locator("xpath=..").inner_text(); print("plan food:",ft[:200].replace("\n"," | "))
    assert "your meal for this duty" in ft.lower()
    b.close()
print("ERRORS:", errs or "none")
