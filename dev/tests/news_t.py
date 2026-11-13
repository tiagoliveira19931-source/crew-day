# News: UK and Europe first; full article saved offline (from the feed or the reader service); readable with no signal.
import datetime,json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]; jina=[]
LONG="<p>"+"Stansted crew news paragraph. "*80+"</p><p>Second paragraph.</p>"
def handle(r):
    u=r.request.url;H={"Access-Control-Allow-Origin":"*"}
    if "rss2json" in u:
        if "ukaviation" in u: items=[{"title":"Stansted runway works","description":"<p>Short summary.</p>","content":"","link":"https://www.ukaviation.news/a1","pubDate":"2026-11-13 08:00:00"}]
        elif "aerotime" in u: items=[{"title":"EU261 changes agreed","description":"<p>Summary</p>","content":LONG,"link":"https://www.aerotime.aero/a2","pubDate":"2026-11-13 07:00:00"}]
        elif "airlive" in u: items=[{"title":"French ATC strike Friday","description":"<p>Strike summary</p>","content":"","link":"https://www.airlive.net/a3","pubDate":"2026-11-13 06:00:00"}]
        else: items=[]
        return r.fulfill(status=200,content_type="application/json",headers=H,body=json.dumps({"status":"ok","items":items}))
    if "r.jina.ai" in u:
        jina.append(u); return r.fulfill(status=200,content_type="text/plain",headers=H,body="Title: Stansted runway works\nURL Source: x\nMarkdown Content:\n# Stansted runway works\n\n"+("Full article line about overnight runway closures at Stansted. "*60))
    return r.abort() if u.startswith("http") else r.continue_()
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":390,"height":844}); pg=ctx.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",handle)
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(100)
    f=pg.locator('[data-fold^="news"]'); f.click(); pg.wait_for_timeout(100)
    pg.click("#newsrf"); pg.wait_for_timeout(1500)
    box=f.locator("xpath=..").inner_text().replace("\n"," | ")
    print(box[:500]); print("reader fetches:",jina)
    assert "UK (1)" in box and "Europe (1)" in box, "UK and Europe filters"
    assert box.index("UK (1)")<box.index("Disruption"), "UK and Europe come first"
    assert len(jina)==1 and "ukaviation" in jina[0], "full text fetched only for the short UK article"
    ctx.set_offline(True)
    pg.click('[data-newscat="uk"]'); pg.wait_for_timeout(100)
    pg.locator("details.ex summary").first.click(); pg.wait_for_timeout(100)
    txt=pg.locator("details.ex").first.inner_text(); print("offline UK:", len(txt), txt[:120].replace("\n"," "))
    assert "full article saved" in txt and len(txt)>2000
    pg.click('[data-newscat="europe"]'); pg.wait_for_timeout(100); pg.locator("details.ex summary").first.click()
    t2=pg.locator("details.ex").first.inner_text(); assert "Second paragraph" in t2, "feed full text kept with paragraphs"
    b.close()
print("ERRORS:", errs or "none")
