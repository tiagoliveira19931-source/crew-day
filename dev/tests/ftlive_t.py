# Live times trial: with a flight lookup key and signal, the flight's real off-block time starts or corrects the
# timer; the timer no longer writes the block times crew type in. AirLabs is replaced by a made-up answer.
import datetime, json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]; calls=[]
ANS={"response":{"flight_iata":"FR147","reg_number":"9H-VUC","status":"en-route","dep_time_utc":"2026-11-14 13:30","dep_estimated_utc":"2026-11-14 13:41","dep_actual_utc":"2026-11-14 13:38","arr_time_utc":"2026-11-14 15:15","arr_estimated_utc":"2026-11-14 15:22"}}
def route(r):
    u=r.request.url
    if u.startswith("https://airlabs.co/api/v9/flight"):
        calls.append(u); return r.fulfill(body=json.dumps(ANS),content_type="application/json",headers={"Access-Control-Allow-Origin":"*"})
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",route)
    pg.clock.install(time=datetime.datetime(2026,11,14,11,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p","2026-11-14 | DUTY | 12:45 | 18:00 | FR147 STN-BER 13:30-15:15; FR146 BER-STN 15:40-17:30"); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    pg.evaluate("()=>{}")
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="profile"]'); pg.wait_for_timeout(150)
    f=pg.locator('[data-fold="pf_key"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    pg.fill("#pr-fk","test-key-123"); pg.locator("#pr-fk").dispatch_event("change"); pg.wait_for_timeout(100)
    # 3 h before departure the aircraft is looked up once, and Today shows it with a tracking link
    pg.clock.set_system_time(datetime.datetime(2026,11,14,10,40)); pg.wait_for_timeout(300)
    pg.click("[data-tab=today]"); pg.clock.run_for(50000); pg.wait_for_timeout(500)
    t=pg.inner_text("main"); assert "9H-VUC" in t and "Where is it now" in t, [l for l in t.split("\n") if "aircraft" in l.lower()]
    href=pg.locator('a:has-text("Where is it now")').get_attribute("href"); assert href.endswith("/aircraft/9hvuc"), href
    n0=len(calls); pg.clock.run_for(200000); assert len(calls)==n0, "no more aircraft checks once known"
    calls.clear()
    pg.clock.set_system_time(datetime.datetime(2026,11,14,13,15)); pg.wait_for_timeout(1200)
    pg.click("[data-tab=today]"); pg.wait_for_timeout(300); pg.click("[data-tab=trip]"); pg.wait_for_timeout(300)
    print("duty:",pg.evaluate("JSON.stringify(window.CREWDAY_TEST.duty?window.CREWDAY_TEST.duty():null)"))
    t=pg.inner_text("main"); assert "live times" in t.lower(), t[:900]
    # automatic: 10 minutes before departure the app checks by itself and starts the timer from off blocks
    pg.clock.set_system_time(datetime.datetime(2026,11,14,13,21)); pg.wait_for_timeout(200)
    assert not calls, "no checks earlier than 10 min before departure"
    pg.clock.run_for(35000); pg.wait_for_timeout(500)
    assert calls, "should check from 10 min before departure"
    t=pg.inner_text("main"); assert "started by itself" in t and "On blocks" in t, [l for l in t.split("\n") if "blocks" in l or "itself" in l]
    n=len(calls); pg.clock.run_for(400000); pg.wait_for_timeout(300); assert len(calls)==n, ("stops checking once off blocks is known",len(calls)-n)
    pg.click("#ftundo") if pg.locator("#ftundo").count() else None; pg.wait_for_timeout(200)
    pg.click("#ftlive"); pg.wait_for_timeout(500)
    assert calls and "flight_iata=FR147" in calls[-1] and "test-key-123" in calls[-1], calls
    t=pg.inner_text("main"); print([l for l in t.split("\n") if "blocks" in l][:4])
    assert "Off blocks 13:38" in t, t
    pg.click("[data-ftlivego]"); pg.wait_for_timeout(300)
    t=pg.inner_text("main"); assert "Running from online times" in t, [l for l in t.split("\n") if "online" in l]
    assert pg.locator("#ftgo").count()==0 and pg.locator("#ftrestart").count()==0
    t=pg.inner_text("main"); assert "On blocks" in t and "off blocks ~13:38" in t, [l for l in t.split("\n") if "13:" in l]
    # with a key, off blocks is filled from online (roster time is Zulu: 13:38Z)
    R=pg.evaluate("window.CREWDAY_TEST.roster()['2026-11-14'].sectors[0]"); print("sector:",{k:R.get(k) for k in ("offb","onb")})
    assert R.get("offb")=="13:38" and not R.get("onb"), R
    # after landing the app checks once more; the online on-block time stops the timer by itself
    ANS["response"]["arr_actual_utc"]="2026-11-14 15:19"
    pg.clock.set_system_time(datetime.datetime(2026,11,14,15,30)); pg.clock.run_for(400000); pg.wait_for_timeout(500)
    if pg.evaluate("!!window.CREWDAY_TEST.ft&&!!window.CREWDAY_TEST.ft()"): pg.click("#ftlive"); pg.wait_for_timeout(500)
    t=pg.inner_text("main"); assert "Running from online times" not in t, [l for l in t.split("\n") if "online" in l or "blocks" in l]
    assert "1:41" in t or "101" in t, [l for l in t.split("\n") if "block" in l.lower()]
    R=pg.evaluate("window.CREWDAY_TEST.roster()['2026-11-14'].sectors[0]"); assert R.get("onb")=="15:19", R
    # the saved note shows after a change
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="profile"]'); pg.wait_for_timeout(150)
    pg.fill("#pr-fk","test-key-123 "); pg.locator("#pr-fk").dispatch_event("change"); pg.wait_for_timeout(100)
    assert "Saved" in pg.evaluate("(document.getElementById('savedpill')||{}).textContent||''")
    b.close()
print("ERRORS:", errs or "none")
