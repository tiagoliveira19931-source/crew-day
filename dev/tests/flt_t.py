import datetime,json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]; hits=[]
def handle(r):
    u=r.request.url
    if "adsbdb" in u:
        hits.append(u.rsplit("/",1)[1])
        if u.endswith("RYR1234"): return r.fulfill(status=200,content_type="application/json",headers={"Access-Control-Allow-Origin":"*"},body=json.dumps({"response":{"flightroute":{"origin":{"iata_code":"STN"},"destination":{"iata_code":"BCN"}}}}))
        return r.fulfill(status=404,headers={"Access-Control-Allow-Origin":"*"},body='{"response":"unknown callsign"}')
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",handle)
    pg.clock.install(time=datetime.datetime(2026,11,11,19,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(200)
    def day(d):
        pg.click(f'[data-pick="{d}"]'); pg.wait_for_timeout(100)
        if pg.locator('[data-setkind="flying"]').count(): pg.click('[data-setkind="flying"]')
    def f(i,k,v): pg.fill(f"#sc-{k}-{i}",v); pg.locator(f"#sc-{k}-{i}").dispatch_event("change"); pg.wait_for_timeout(150)
    day("2026-11-12"); pg.click('[data-addsec]')
    f(0,"flt","fr7633"); f(0,"to","AGP"); f(0,"dep","06:30"); f(0,"arr","09:20")
    pg.click('[data-addsec]'); pg.wait_for_timeout(100)
    print("return guess:", pg.input_value("#sc-flt-1"), pg.input_value("#sc-from-1"), pg.input_value("#sc-to-1"), "|", pg.inner_text("#sc-fn-1"))
    f(1,"dep","10:00"); f(1,"arr","12:50")
    pg.click('[data-saveday="2026-11-12"]'); pg.wait_for_timeout(100)
    # next week same flights
    day("2026-11-19"); pg.click('[data-addsec]'); f(0,"flt","FR7633")
    print("learned:", pg.input_value("#sc-from-0"), pg.input_value("#sc-to-0"), pg.input_value("#sc-dep-0"), pg.input_value("#sc-arr-0"), "|", pg.inner_text("#sc-fn-0"))
    pg.click('[data-addsec]'); pg.wait_for_timeout(100)
    print("return from memory:", pg.input_value("#sc-flt-1"), pg.input_value("#sc-from-1"), pg.input_value("#sc-to-1"), pg.input_value("#sc-dep-1"), "|", pg.inner_text("#sc-fn-1"))
    # unknown flight -> online lookup
    day("2026-11-20"); pg.click('[data-addsec]'); 
    pg.fill("#sc-from-0",""); f(0,"flt","FR1234"); pg.wait_for_timeout(400)
    print("online:", pg.input_value("#sc-from-0"), pg.input_value("#sc-to-0"), "|", pg.inner_text("#sc-fn-0"), hits)
    f(0,"flt","FR9999"); pg.wait_for_timeout(400); print("miss:", pg.inner_text("#sc-fn-0"))
    b.close()
print("ERRORS:", errs or "none")
