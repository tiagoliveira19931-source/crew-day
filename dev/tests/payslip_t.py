# Pay like my payslip: crew start from the payslip layout (names only), type their own amounts; flight hours come
# from the roster in the pay period, rounded up; tax, NI and pension give an estimated net pay. All figures made up.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="""2026-11-02 | DUTY | 05:00 | 11:00 | FR1 STN-DUB 06:00-07:15; FR2 DUB-STN 07:45-09:00
2026-11-03 | DUTY | 05:00 | 13:00 | FR3 STN-AGP 06:00-08:10; FR4 AGP-STN 08:50-10:55
2026-11-05 | GD | 08:00 | 16:00
2026-11-07 | SICK
2026-11-20 | DUTY | 05:00 | 11:00 | FR5 STN-DUB 06:00-07:15"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,15,12,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="money"]'); pg.wait_for_timeout(150)
    if pg.locator('[data-mv="pay"]').count(): pg.click('[data-mv="pay"]'); pg.wait_for_timeout(150)
    pg.select_option("#p-type","slip"); pg.wait_for_timeout(150)
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(60)
    F("#sl-from","2026-11-01"); F("#sl-to","2026-11-30")
    pg.evaluate("()=>{}")
    pg.click('[data-sltpl="ryr"]'); pg.wait_for_timeout(150)
    names=pg.eval_on_selector_all('[id^="sl-n-"]',"els=>els.map(e=>e.value)")
    assert names[:4]==["Basic Salary","CSS Allowance","London Allowance","UNIMED Allowance"] and "Daily Allowance" in names, names
    assert all(v in ("","0") for v in pg.eval_on_selector_all('[id^="sl-a-"]:not([disabled])',"els=>els.map(e=>e.value)")), "no amounts built in"
    amt={"Basic Salary":"1700","CSS Allowance":"200","London Allowance":"250","UNIMED Allowance":"37.5","UNIMED (sick days)":"3.95","Daily Allowance":"8","Ground Duties":"40","Training":"40","Bank Holiday":"40"}
    for i,n in enumerate(names):
        if n in amt: F(f"#sl-a-{i}",amt[n])
    pg.click('[data-sdadd="1"]'); pg.wait_for_timeout(100); F("#sd-a-0","27")
    E=pg.evaluate("window.CREWDAY_TEST.slip()")
    print({k:round(E[k],2) for k in ("gross","tax","ni","pen","other","net")}, E["C"]["paidH"], E["C"]["sick"], E["C"]["code"])
    # 2:30 + 4:15 flown before today = 6:45 -> paid 7 h (the 20 Nov flight hasn't happened yet)
    assert E["C"]["paidH"]==7 and E["C"]["code"]["GD"]==1 and E["C"]["sick"]==1, E["C"]
    assert abs(E["gross"]-2279.55)<0.01, E["gross"]
    assert abs(E["tax"]-246.41)<0.01 and abs(E["ni"]-98.52)<0.01 and abs(E["pen"]-70.38)<0.01, E
    assert abs(E["net"]-1837.24)<0.01, E["net"]
    t=pg.inner_text("main")
    assert "paid 7 h" in t and "1 occasion" in t and ("1,837.24" in t or "1837.24" in t), t[:900]
    # Scottish tax code and a BR code
    assert abs(pg.evaluate("window.CREWDAY_TEST.tax(2279.55,'S1257L')")-pg.evaluate("window.CREWDAY_TEST.tax(2279.55,'1257L')"))>1
    assert abs(pg.evaluate("window.CREWDAY_TEST.tax(1000,'BR')")-200)<0.01
print("ERRORS:", "; ".join(errs) if errs else "none")
