import sys,datetime,json
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
t0=datetime.datetime(2026,11,11)
times=[(t0+datetime.timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(72)]
def wx(lat):
    n=72;cold=lat>50
    return {"hourly":{"time":times,"precipitation_probability":[80 if cold and 26<=i<=40 else 5 for i in range(n)],"precipitation":[1.0 if cold and 26<=i<=40 else 0 for i in range(n)],"temperature_2m":[0 if cold else 19]*n,"wind_gusts_10m":[50]*n,"wind_speed_10m":[30]*n,"wind_direction_10m":[250]*n,"weather_code":[45 if cold and 27<=i<=30 else 1 for i in range(n)]}}
def handle(r):
    u=r.request.url
    if "open-meteo" in u:
        lat=float(u.split("latitude=")[1].split("&")[0]); return r.fulfill(status=200,content_type="application/json",body=json.dumps(wx(lat)),headers={"Access-Control-Allow-Origin":"*"})
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",handle)
    pg.clock.install(time=datetime.datetime(2026,11,11,19,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.click('[data-role="pilot"]'); pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.set_input_files("#ics",sys.argv[2]); pg.wait_for_timeout(200); pg.click('[data-more=""]')
    pg.click("[data-tab=plan]"); pg.wait_for_timeout(300); pg.click("[data-tab=plan]")
    if pg.locator('[data-fold="weather"][aria-expanded="false"]').count(): pg.click('[data-fold="weather"]')
    lv=pg.inner_text(".pass") if pg.locator(".pass").count() else ""
    wb=pg.locator('[data-fold="weather"]').locator("xpath=..").inner_text().replace("\n"," | ")
    print("PLAN WX:",wb[:420])
    pg.click('[data-wxextra="15"]'); print("after +15 alarms fold:",pg.locator('[data-fold="alarms"]').inner_text().replace("\n"," "))
    pg.clock.set_system_time(datetime.datetime(2026,11,12,6,30)); pg.click("[data-tab=trip]"); pg.wait_for_timeout(300); pg.click("[data-tab=trip]")
    print("TRIP folds:",[x.inner_text().split("\n")[0] for x in pg.locator("main .foldh").all()])
    pg.fill("#ts-o-0","06:05"); pg.locator("#ts-o-0").dispatch_event("change"); pg.fill("#ts-n-0","08:50"); pg.locator("#ts-n-0").dispatch_event("change"); pg.fill("#ts-c-0","06:15"); pg.locator("#ts-c-0").dispatch_event("change")
    pg.fill("#ts-n-0",""); pg.locator("#ts-n-0").dispatch_event("change"); print("expected:",pg.locator(".seccard p").first.inner_text()); pg.fill("#ts-n-0","08:50"); pg.locator("#ts-n-0").dispatch_event("change")
    print("flights:",pg.locator('[data-fold^="flights"]').locator("xpath=..").inner_text().replace("\n"," | ")[:300])
    pg.click('[data-fold^="pilot"]'); pg.wait_for_timeout(200)
    print("pilot:",pg.locator('[data-fold^="pilot"]').locator("xpath=..").inner_text().replace("\n"," | ")[:600])
    pg.locator('[data-fold^="pilot"]').locator("xpath=..").screenshot(path="/tmp/pilot.png")
    pg.click('[data-fold^="timers"]'); print("timers:",pg.locator("[data-timer]").all_inner_texts())
    pg.click('[data-fold^="wxtoday"]'); print("wx today:",pg.locator('[data-fold^="wxtoday"]').locator("xpath=..").inner_text().replace("\n"," | ")[:300])
    ws=[]
    for t in ["today","trip","plan","me"]:
        pg.click(f"[data-tab={t}]"); ws.append(pg.evaluate("document.documentElement.scrollWidth"))
    pg.click("[data-tab=more]")
    for m in ["profile","roster","money","issues","sick","layover"]:
        pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None; pg.click(f'[data-more="{m}"]'); ws.append(pg.evaluate("document.documentElement.scrollWidth"))
    print("widths:",ws)
    print("ERRORS:",errs or "none")
