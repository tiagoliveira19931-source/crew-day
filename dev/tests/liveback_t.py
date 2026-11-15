# With a flight key, the day's flights fill in from online when Crew Day is opened, even when the feed still says
# "en-route" long after the expected landing; a timer left running stops. Made-up flights and answers.
import datetime, json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]; calls=[]
FEED={
 "FR147":{"flight_iata":"FR147","status":"landed","dep_time_utc":"2026-11-14 13:30","dep_actual_utc":"2026-11-14 13:31","arr_time_utc":"2026-11-14 15:15","arr_estimated_utc":"2026-11-14 15:12"},
 "FR146":{"flight_iata":"FR146","status":"en-route","dep_time_utc":"2026-11-14 15:40","dep_actual_utc":"2026-11-14 15:43","arr_time_utc":"2026-11-14 17:30","arr_estimated_utc":"2026-11-14 17:35"},
}
def route(r):
    u=r.request.url
    if u.startswith("https://airlabs.co/api/v9/flight"):
        f=u.split("flight_iata=")[1].split("&")[0]; calls.append(f)
        return r.fulfill(body=json.dumps({"response":FEED[f]}),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    return r.abort() if u.startswith("http") else r.continue_()
U=lambda d,h,m:datetime.datetime(2026,11,d,h,m)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",route)
    pg.clock.install(time=U(14,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p","2026-11-14 | DUTY | 12:45 | 18:00 | FR147 STN-BER 13:30-15:15; FR146 BER-STN 15:40-17:30"); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="profile"]'); pg.wait_for_timeout(150)
    f=pg.locator('[data-fold="pf_key"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    pg.fill("#pr-fk","test-key-123"); pg.locator("#pr-fk").dispatch_event("change"); pg.wait_for_timeout(100)
    # a timer started by hand on FR146 and left running
    pg.clock.set_system_time(U(14,15,50)); pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    fl=pg.locator('[data-fold="flights"]')
    if fl.get_attribute("aria-expanded")=="false": fl.click()
    pg.fill("#ts-o-0","13:31"); pg.locator("#ts-o-0").dispatch_event("change"); pg.fill("#ts-n-0","15:12"); pg.locator("#ts-n-0").dispatch_event("change"); pg.wait_for_timeout(100)
    pg.click("[data-tab=today]"); pg.click("[data-tab=trip]"); pg.wait_for_timeout(100)
    if pg.locator("#ftmanual").count(): pg.click("#ftmanual"); pg.wait_for_timeout(100)
    pg.click("#ftgo"); pg.wait_for_timeout(200)
    assert pg.evaluate("!!window.CREWDAY_TEST.ft()"), "timer running"
    # Crew Day opened again at 18:30: the feed still says en-route, expected 17:35 is over 30 min ago
    pg.clock.set_system_time(U(14,18,30)); pg.clock.run_for(65000); pg.wait_for_timeout(600)
    R=pg.evaluate("window.CREWDAY_TEST.roster()['2026-11-14'].sectors"); print([(x.get("offb"),x.get("onb")) for x in R])
    assert R[1].get("offb")=="15:43" and R[1].get("onb")=="17:35", R[1]
    assert not pg.evaluate("window.CREWDAY_TEST.ft()"), "the running timer stopped"
print("ERRORS:", "; ".join(errs) if errs else "none")
