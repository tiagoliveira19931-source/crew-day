import datetime,json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]; hits=[]
def handle(r):
    u=r.request.url; H={"Access-Control-Allow-Origin":"*"}
    if "airlabs" in u:
        hits.append(u.split("?")[1])
        if "BADKEY" in u: return r.fulfill(status=200,content_type="application/json",headers=H,body=json.dumps({"error":{"message":"Unknown api_key","code":"unknown_api_key"}}))
        if "FR1882" in u: return r.fulfill(status=200,content_type="application/json",headers=H,body=json.dumps({"response":[{"flight_iata":"FR1882","dep_iata":"STN","arr_iata":"LIS","dep_time":"16:10","dep_time_utc":"16:10","arr_time":"19:00","arr_time_utc":"19:00","duration":170,"days":["mon","wed","fri"]}]}))
        return r.fulfill(status=200,content_type="application/json",headers=H,body=json.dumps({"response":[]}))
    if "adsbdb" in u: return r.fulfill(status=404,headers=H,body="{}")
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",handle)
    pg.clock.install(time=datetime.datetime(2026,11,11,19,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="profile"]'); pg.wait_for_timeout(200); pg.click('[data-fold^="pf_key"]'); pg.wait_for_timeout(100)
    pg.fill("#pr-fk","GOODKEY"); pg.locator("#pr-fk").dispatch_event("change"); pg.wait_for_timeout(100)
    pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="roster"]'); pg.wait_for_timeout(200)
    def day(d):
        pg.click(f'[data-pick="{d}"]'); pg.wait_for_timeout(100)
        if pg.locator('[data-setkind="flying"]').count(): pg.click('[data-setkind="flying"]')
    def f(i,k,v): pg.fill(f"#sc-{k}-{i}",v); pg.locator(f"#sc-{k}-{i}").dispatch_event("change"); pg.wait_for_timeout(300)
    day("2026-11-13"); pg.click('[data-addsec]'); f(0,"flt","fr1882")
    print("airlabs:", [pg.input_value(f"#sc-{k}-0") for k in ["from","to","dep","arr"]], "|", pg.inner_text("#sc-fn-0"))
    f(0,"flt","FR5555"); print("not found:", pg.inner_text("#sc-fn-0"))
    pg.evaluate("()=>{}")
    b.close()
print("hits",hits); print("ERRORS:", errs or "none")
