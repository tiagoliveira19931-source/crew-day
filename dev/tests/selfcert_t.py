# Self-certificate (Ryanair group): Profile fields + drawn signature fill the form; days off inside the sickness are
# counted; the PDF is saved in Documents › Self-certificates as Self-Certificate-<reason>-<first day>.pdf.
# All details are made up. pdf-lib is served from the local copy (the app loads it from cdnjs).
import datetime, os, subprocess
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
LIB=open("/opt/npm-tools/node_modules/pdf-lib/dist/pdf-lib.min.js").read()
PAGE="<!doctype html><html><head><meta charset=utf-8></head><body><script>window.CREWDAY_PWA=true</script>"+html+"</body></html>"
OUT="/tmp/claude-0/-home-claude/826586fa-4961-5511-84d6-a37445adb4b2/scratchpad/sc_test.pdf"
def route(r):
    u=r.request.url
    if u=="https://t.test/": return r.fulfill(body=PAGE,content_type="text/html")
    if "pdf-lib" in u: return r.fulfill(body=LIB,content_type="application/javascript")
    return r.abort()
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":390,"height":844},accept_downloads=True); pg=ctx.new_page(); pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",route)
    pg.clock.install(time=datetime.datetime(2026,11,22,8,0)); pg.goto("https://t.test/")
    pg.fill("#pr-n","Alex Smith"); pg.click("#pr-s"); pg.keyboard.type("ABCDE"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p","2026-11-22 | DUTY | 06:00 | 15:00 | FR8001 STN-TFS 06:45-11:10\n2026-11-23 | OFF | | |\n2026-11-24 | DUTY | 06:00 | 12:00 | FR8003 STN-DUB 06:45-08:00"); pg.click("#pasteroster"); pg.wait_for_timeout(200)
    pg.click("[data-tab=more]"); pg.click('[data-more=""]') if pg.locator('[data-more=""]').count() else None
    pg.click('[data-more="profile"]'); pg.wait_for_timeout(150)
    f=pg.locator('[data-fold="pf_sc"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    def F(sel,v): pg.fill(sel,v); pg.locator(sel).dispatch_event("change"); pg.wait_for_timeout(60)
    F("#sc-emp","12345"); F("#sc-dept","Inflight"); F("#sc-rank","JU"); F("#sc-entry","2020-03-01"); pg.select_option("#sc-con","FR"); F("#sc-med","medical@example.com")
    f=pg.locator('[data-fold="pf_sc"]')
    if f.get_attribute("aria-expanded")=="false": f.click()
    c=pg.locator("#sigpad"); c.scroll_into_view_if_needed(); pg.wait_for_timeout(100); bb=c.bounding_box(); print("box",bb); pg.mouse.move(bb["x"]+30,bb["y"]+80); pg.mouse.down()
    for i in range(40): pg.mouse.move(bb["x"]+30+i*7,bb["y"]+80+((-1)**i)*18*(i%5)/4)
    pg.mouse.up(); pg.click("#sigsave"); pg.wait_for_timeout(200); assert pg.locator('img[alt="Your saved signature"]').count()==1
    # sick 22–24 Nov (a day off on the 23rd), self-certified
    pg.click('[data-more=""]'); pg.click('[data-more="sick"]'); pg.wait_for_timeout(200)
    pg.fill("#sk-from","2026-11-22"); pg.fill("#sk-to","2026-11-24"); pg.select_option("#sk-type","self")
    pg.fill("#sk-reason","Viral infection: high temperature, sore throat and headache since the evening of 21/11/26.")
    pg.click("#addsick"); pg.wait_for_timeout(300)
    t=pg.inner_text("main"); assert "Self-certificate form" in t and "3 days, 1 day off included, 2 working days" in t, t[:900]
    pg.click("#scmake"); pg.wait_for_function("document.querySelector('main').innerText.includes('Self-Certificate-')",timeout=20000)
    t=pg.inner_text("main"); assert "Open Self-Certificate-Viral infection-2026-11-22.pdf" in t, t[:900]
    assert "Email medical@example.com" in t
    href=pg.locator('a[href^="mailto:"]').get_attribute("href"); assert "subject=Self-certificate" in href and "2026" in href, href
    # the saved PDF: read it back from the phone's storage and check its pages and text
    data=pg.evaluate("""async()=>{const D=JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>localStorage.getItem(k).includes('fileStore'))));
      const f=D.fileStore.files.find(x=>/Self-Certificate/.test(x.name));const db=await new Promise(r=>{const q=indexedDB.open('crewday-files',1);q.onsuccess=()=>r(q.result)});
      const v=await new Promise(r=>{const q=db.transaction('files').objectStore('files').get(f.asset);q.onsuccess=()=>r(q.result)});const b=new Uint8Array(await v.arrayBuffer());let s='';for(const x of b)s+=String.fromCharCode(x);return btoa(s)}""")
    import base64; open(OUT,"wb").write(base64.b64decode(data))
    txt=subprocess.run(["pdftotext",OUT,"-"],capture_output=True,text=True).stdout
    assert "21/11/26." in txt, "full reason, not cut at 80 characters"
    for want in ["SELF-CERTIFICATE ABSENCE FORM","12345","ABCDE","ALEX SMITH","INFLIGHT","JU","01/03/2020","22/11/26","24/11/26","Viral infection: high temperature"]:
        assert want in txt, (want, txt[:1500])
    b.close()
print("ERRORS:", errs or "none")
