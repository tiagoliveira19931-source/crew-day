import sys,datetime,json
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
t0=datetime.datetime(2026,11,11)
times=[(t0+datetime.timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(72)]
def wx(lat):
    rain=[80 if (lat>50 and 26<=i<=31) else 5 for i in range(72)]
    return {"hourly":{"time":times,"precipitation_probability":rain,"precipitation":[1.2 if r>50 else 0 for r in rain],"temperature_2m":[0 if lat>50 else 18]*72,"wind_gusts_10m":[30]*72}}
def handle(r):
    u=r.request.url
    if "open-meteo" in u:
        lat=float(u.split("latitude=")[1].split("&")[0]); return r.fulfill(status=200,content_type="application/json",body=json.dumps(wx(lat)),headers={"Access-Control-Allow-Origin":"*"})
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",handle)
    pg.clock.install(time=datetime.datetime(2026,11,11,20,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.set_input_files("#ics",sys.argv[2]); pg.wait_for_timeout(200); pg.click('[data-pick="2026-11-13"]'); pg.click('[data-setkind=standby]'); pg.fill("#rw-r","04:00"); pg.fill("#rw-o","12:00"); pg.click("[data-saveday]"); pg.click('[data-more=""]')
    pg.click("[data-tab=plan]"); pg.wait_for_timeout(300); pg.click("[data-tab=plan]")
    print("PLAN:", pg.inner_text(".nudges") if pg.locator(".nudges").count() else "none")
    def N(lbl):
        print(lbl, pg.inner_text(".nudges").replace("\n"," | ") if pg.locator(".nudges").count() else "none")
    for hh,mm,l in [(3,10,"READY 03:10"),(4,10,"GO 04:10"),(6,30,"DUTY 06:30"),(9,45,"DUTY 09:45")]:
        pg.clock.set_system_time(datetime.datetime(2026,11,12,hh,mm)); pg.click("[data-tab=today]"); pg.wait_for_timeout(200); pg.click("[data-tab=today]"); N(l)
        if hh==9: pg.locator(".nudges").screenshot(path="/tmp/nudge_duty.png"); pg.click('.nudges [data-add="250"]'); N("  after +250:")
    pg.clock.set_system_time(datetime.datetime(2026,11,13,5,10)); pg.click("[data-tab=today]"); pg.click("#called"); pg.wait_for_timeout(200); pg.click("[data-tab=today]"); N("CALLED")
    pg.locator(".nudges").screenshot(path="/tmp/nudge_called.png")
    print("ERRORS:",errs or "none")
