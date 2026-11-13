# AI prompts: the roster prompt handles several screenshots; the timetable prompt names the stop and airport,
# and an answer in the asked-for layout fills both directions. The sample timetable is made up.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
ANS="""Monday to Friday
04:58 → 05:10
05:28 → 05:39
xx:13 → xx:23 (07:00 – 22:00)
Saturday
06:13 → 06:23
Sunday
07:13 → 07:23
Return
Monday to Friday
05:40 → 05:52
xx:45 → xx:57 (06:00 – 23:00)
Saturday
07:45 → 07:57
Sunday
08:45 → 08:57"""
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":390,"height":844}); ctx.grant_permissions(["clipboard-read","clipboard-write"]); pg=ctx.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.goto("about:blank"); pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    t=pg.inner_text("main"); assert "How to bring in your roster" in t and "Copy roster prompt" in t and "Open Gemini" in t
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="profile"]'); pg.wait_for_timeout(150)
    for f in pg.locator("[data-fold^='pf_']").all():
        if f.get_attribute("aria-expanded")=="false": f.click(); pg.wait_for_timeout(50)
    pg.fill("#tr-from-train","Bishop's Stortford"); pg.locator("#tr-from-train").dispatch_event("change"); pg.wait_for_timeout(100)
    btn=pg.locator('[data-ttprompt="train"]'); assert btn.count()==1
    btn.click(); pg.wait_for_timeout(300); print("after click:", pg.evaluate("document.activeElement.tagName"), pg.locator("textarea[readonly]").count(), errs)
    clip=pg.input_value('#ttp-train')
    print(clip[:140]); assert "Today is" in clip; assert "Bishop's Stortford" in clip and "Stansted" in clip and "Return" in clip
    pg.fill("#tr-out-train",ANS); pg.locator("#tr-out-train").dispatch_event("change"); pg.wait_for_timeout(200)
    out=pg.locator("#tr-out-train").locator("xpath=..").inner_text(); back=pg.locator("#tr-back-train").locator("xpath=..").inner_text(); back_val=pg.input_value("#tr-back-train")
    print("out:",out.split("Read:")[-1][:120]); print("back value:",back_val[:60])
    print("back:",back.split("Read:")[-1][:120]); assert "Read:" in out and "Read:" in back, "return part should be read for Coming home"
    b.close()
print("ERRORS:", errs or "none")
