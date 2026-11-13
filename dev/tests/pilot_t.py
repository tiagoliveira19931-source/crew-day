import datetime,json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
txt="2026-11-12 | DUTY | 06:05 | 16:55 | FR2232 STN-NTE 06:50-08:15; FR2231 NTE-STN 08:40-10:05; FR1261 STN-OPO 11:10-13:35; FR1262 OPO-STN 14:00-16:25"
def wx(u):
    times=[(datetime.datetime(2026,11,12)+datetime.timedelta(hours=h)).strftime("%Y-%m-%dT%H:00") for h in range(72)]
    n=len(times); fog="44.2" in u or "47." in u  # Nantes-ish lat -> fog
    return {"hourly":{"time":times,"precipitation_probability":[50]*n,"precipitation":[0.4]*n,"temperature_2m":[2 if fog else 8]*n,"wind_gusts_10m":[60]*n,"wind_speed_10m":[37]*n,"wind_direction_10m":[310]*n,"weather_code":[45 if fog else 61]*n,"visibility":[800 if fog else 9000]*n,"cloud_cover_low":[90]*n,"dew_point_2m":[1.5 if fog else 6]*n,"pressure_msl":[1008.6]*n,"freezing_level_height":[900]*n,"cape":[0]*n},
            "daily":{"time":times[::24],"temperature_2m_max":[9,9,9],"temperature_2m_min":[2,2,2],"precipitation_probability_max":[50,50,50],"weather_code":[61,61,61],"wind_gusts_10m_max":[60,60,60],"sunrise":["2026-11-12T07:00"]*3,"sunset":["2026-11-12T16:20"]*3}}
def handle(r):
    u=r.request.url
    if "open-meteo" in u and "forecast" in u: return r.fulfill(status=200,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"},body=json.dumps(wx(u)))
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",handle)
    pg.clock.install(time=datetime.datetime(2026,11,12,4,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A")
    if pg.locator('[data-role="pilot"]').count(): pg.click('[data-role="pilot"]')
    pg.click("#setupdone")
    pg.evaluate("()=>0")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p",txt); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(300)
    f=pg.locator('[data-fold^="pilot"]')
    print("pilot fold:",f.count())
    if f.count():
        f.click(); pg.wait_for_timeout(600)
        box=f.locator("xpath=..")
        print(box.inner_text()[:1500]); box.screenshot(path="/tmp/pilot.png")
    b.close()
print("ERRORS:", errs or "none")
