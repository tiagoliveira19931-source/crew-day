import datetime,json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]; hits=[]
WV="Cologne is Germany's fourth largest city.\n\n== Understand ==\nFounded by the Romans in 50 AD.\n\n== Get around ==\nThe KVB runs trams.\n\n== See ==\nCologne Cathedral.\n\n== Do ==\nRhine walks.\n\n=== Festivals ===\nCarnival: the season opens on 11.11 at 11:11 in Heumarkt.\nChristmas markets: from late November at the cathedral.\n\n== Eat ==\nTry Halve Hahn.\n\n== Stay safe ==\nWatch for pickpockets at the main station."
def handle(r):
    u=r.request.url
    if u.startswith("http"): hits.append(u.split("?")[0])
    H={"Access-Control-Allow-Origin":"*"}
    if "wikivoyage" in u: return r.fulfill(status=200,content_type="application/json",headers=H,body=json.dumps({"query":{"pages":{"1":{"title":"Cologne","extract":WV}}}}))
    if "nager" in u: return r.fulfill(status=200,content_type="application/json",headers=H,body=json.dumps([{"date":"2026-11-11","localName":"Sankt Martin","name":"St Martin's Day","global":False},{"date":"2026-12-25","localName":"Weihnachten","name":"Christmas Day","global":True},{"date":"2026-11-18","localName":"Buß- und Bettag","name":"Repentance Day","global":False}]))
    if "open-meteo" in u and "daily" in u: return r.fulfill(status=200,content_type="application/json",headers=H,body=json.dumps({"daily":{"time":["2026-11-11","2026-11-12","2026-11-13"],"sunrise":["2026-11-11T07:35"]*3,"sunset":["2026-11-11T16:45"]*3,"temperature_2m_max":[9,8,7],"temperature_2m_min":[3,2,2]}}))
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",handle)
    pg.clock.install(time=datetime.datetime(2026,11,11,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    if pg.locator('[data-fold="dest"][aria-expanded="false"]').count(): pg.click('[data-fold="dest"]')
    pg.select_option("#tr-c","Germany"); pg.wait_for_timeout(150); pg.fill("#tr-city","Cologne"); pg.locator("#tr-city").dispatch_event("change"); pg.wait_for_timeout(800)
    pg.click('[data-fold^="destfacts"]'); pg.wait_for_timeout(500)
    box=pg.locator('[data-fold^="destfacts"]').locator("xpath=..")
    t=box.inner_text(); print(t[:1100]); 
    pg.locator("summary").filter(has_text="Stay safe").click()
    box.screenshot(path="/tmp/dl.png")
    print("fold hint:",pg.locator('[data-fold^="destfacts"]').inner_text().replace("\n"," "))
    # go offline, reload state-wise: data stays
    pg.context.set_offline(True)
    pg.click('[data-dl]'); pg.wait_for_timeout(300); print("offline press:", "Saved" in box.inner_text(), box.inner_text().count("offline"))
    print("hits",sorted(set(hits)))
    b.close()
print("ERRORS:", errs or "none")
