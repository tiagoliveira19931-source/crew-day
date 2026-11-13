import datetime,json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
rost="2026-11-12 | DUTY | 16:00 | 23:25 | FR2812 STN-LPA 16:45-21:10; FR2811 LPA-STN 21:35-23:55\n2026-11-03 | VTO | | |\n2026-11-15 | OFF | | |"
train="""Early Morning Departures:
05:26
Daytime Pattern (07:00 – 23:00):
:13 (arriving at :28)
:43 (arriving at :58)
Return
Daytime Pattern (07:00 – 23:59):
:28 (arriving at :36)
:58 (arriving at :06)
"""
def handle(r):
    u=r.request.url;H={"Access-Control-Allow-Origin":"*"}
    if "rss2json" in u: return r.fulfill(status=200,content_type="application/json",headers=H,body=json.dumps({"status":"ok","items":[{"title":"Ryanair adds new routes","description":"<p>Ryanair announced <b>12</b> new routes.</p>","link":"https://example.com/a","pubDate":"2026-11-12 10:00:00"}]}))
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",handle)
    pg.clock.install(time=datetime.datetime(2026,11,12,15,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    def gm():
        pg.click("[data-tab=more]"); pg.wait_for_timeout(80)
        if pg.locator('[data-more=""]').count(): pg.click('[data-more=""]'); pg.wait_for_timeout(80)
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(80)
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1")
    F("#tr-from-train","Bishops Stortford"); F("#tr-walk-train","10"); F("#tr-out-train",train)
    pg.click("#setupdone")
    gm(); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",rost); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    # Profile folds
    gm(); pg.click('[data-more="profile"]'); pg.wait_for_timeout(150)
    print("profile:", [x.inner_text().split("\n")[0] for x in pg.locator("main .foldh, main [data-fold]").all()][:9])
    pg.click('[data-fold^="pf_food"]'); pg.wait_for_timeout(100); pg.click('[data-diet="vegetarian"]'); pg.wait_for_timeout(100)
    print("food hint:", pg.locator('[data-fold^="pf_food"]').inner_text().replace("\n"," "))
    # Money
    gm(); 
    if pg.locator('[data-more="money"]').count(): pg.click('[data-more="money"]')
    pg.wait_for_timeout(150)
    if pg.locator("#p-basic").count():
        F("#p-basic","26000"); F("#p-ud","1")
        print("money:", pg.locator("table").first.inner_text().replace("\n"," | "))
    # Sick reason
    gm()
    if pg.locator('[data-more="sick"]').count():
        pg.click('[data-more="sick"]'); pg.wait_for_timeout(100); pg.fill("#sk-from","2026-11-20"); pg.fill("#sk-to","2026-11-20"); pg.fill("#sk-reason","migraine"); pg.click("#addsick"); pg.wait_for_timeout(150)
        t=pg.inner_text("main"); i=t.find("I'm unwell"); print("sick msg:", t[i:i+60])
        pg.click('[data-delsick]') if pg.locator('[data-delsick]').count() else None
    # Today getting there
    pg.click("[data-tab=today]"); pg.wait_for_timeout(150)
    f=pg.locator('[data-fold^="travel"]')
    if f.count() and f.get_attribute("aria-expanded")=="false": f.click()
    pg.wait_for_timeout(150)
    print("pass:", pg.inner_text('[aria-label="Your duty"]').replace("\n"," "), "|", pg.locator('[aria-label="Your duty"]').locator("xpath=following-sibling::p[1]").inner_text() if pg.locator('[aria-label="Your duty"]').locator("xpath=following-sibling::p[1]").count() else "")
    t=pg.inner_text("main"); i=t.find("HOW ARE YOU GETTING THERE"); i=i if i>=0 else t.lower().find("how are you getting there"); print("getting there:", t[i:i+300].replace("\n"," | "))
    # Trip timer: start, restart, stop, undo stop
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(150)
    print("slot field:", pg.locator("#ft-slot").count())
    F("#ft-slot","17:10"); print("slot line:", pg.locator("#ft-slot").locator("xpath=../..").inner_text().replace("\n"," "))
    pg.fill("#ft-est","4:25"); pg.click("#ftgo"); pg.wait_for_timeout(100)
    pg.clock.run_for(60000*3); pg.click("#ftrestart"); pg.wait_for_timeout(100)
    print("running:", pg.locator(".ftcard").inner_text().replace("\n"," ")[:200])
    pg.click("#ftstop"); pg.wait_for_timeout(100); print("undo btn:", pg.locator("#ftunstop").count())
    pg.click("#ftunstop"); pg.wait_for_timeout(100); print("running again:", pg.locator("#ftstop").count())
    pg.click("#ftundo"); pg.wait_for_timeout(100)
    # My flights Now buttons + home shift
    f=pg.locator('[data-fold^="flights"]')
    if f.count() and f.get_attribute("aria-expanded")=="false": f.click()
    pg.wait_for_timeout(100)
    print("now buttons:", pg.locator("[data-secnow]").count())
    F("#ts-o-0","16:45"); F("#ts-n-0","21:40")
    pg.clock.set_system_time(datetime.datetime(2026,11,12,23,30)); pg.wait_for_timeout(200)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(200)
    t=pg.inner_text("main"); i=t.find("Off duty around"); print("home:", t[i:i+200].replace("\n"," "))
    pg.evaluate("()=>0")
    # Timer sound path
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(100)
    # Words and news
    gm()
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    f=pg.locator('[data-fold^="news"]'); print("news fold:", f.count())
    if f.count():
        f.click(); pg.wait_for_timeout(600); print("news:", f.locator("xpath=..").inner_text()[:300].replace("\n"," | "))
    f=pg.locator('[data-fold^="words"]')
    if f.count():
        f.click(); pg.wait_for_timeout(200); print("words:", f.locator("xpath=..").inner_text()[:200].replace("\n"," | "))
    b.close()
print("ERRORS:", errs or "none")
