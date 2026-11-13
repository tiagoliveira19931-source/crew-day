# Read roster screenshots on the phone: made-up Ryanair-style roster screens (light and dark) go through the real
# Tesseract engine (the same one the app downloads), and the app's own reader must turn the text into the right days.
# In the page the Tesseract library is replaced by a stand-in that returns the engine's text, so no network is needed.
import datetime, subprocess, shutil, tempfile, os, json
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
SCREEN="""<html><body style="margin:0;font-family:Arial,sans-serif;background:{bg};color:{fg};width:390px">
<div style="padding:12px 16px;font-size:18px;font-weight:bold">Roster</div>
{blocks}</body></html>"""
BLOCK="""<div style="border-top:1px solid #8888;padding:10px 16px;font-size:14px">
<div style="font-size:12px;opacity:.8">{lab} &nbsp; FLIGHT TIME: {ft}</div>
<div style="font-size:16px;font-weight:bold;margin:4px 0">{date}</div>
<div>CHECK IN &nbsp; {ci}</div>{secs}
<div>CHECK OUT &nbsp; {co}</div></div>"""
SEC="<div>{flt} &nbsp; {a} {dep} &nbsp; → &nbsp; {b} {arr} &nbsp; {reg}</div>"
DAYS=[("DUTY","4H 50M","16 Nov 26, Mon","05:10","13:05",[("FR1001","STN","05:55","DUB","07:10","EIEKL"),("FR1002","DUB","07:45","STN","09:00","EIEKL")]),
      ("DUTY","6H 10M","17 Nov 26, Tue","13:30","22:40",[("FR2201","STN","14:15","LIS","17:05","EIDCL"),("FR2202","LIS","17:40","STN","20:25","EIDCL")])]
def page(bg,fg):
    bl="".join(BLOCK.format(lab=l,ft=ft,date=d,ci=ci,co=co,secs="".join(SEC.format(flt=s[0],a=s[1],dep=s[2],b=s[3],arr=s[4],reg=s[5]) for s in ss)) for l,ft,d,ci,co,ss in DAYS)
    return SCREEN.format(bg=bg,fg=fg,blocks=bl)
have=bool(shutil.which("tesseract")); d=tempfile.mkdtemp(); texts={}
with sync_playwright() as p:
    b=p.chromium.launch()
    if have:
        sp=b.new_page(viewport={"width":390,"height":520},device_scale_factor=3)
        for name,bg,fg in [("light","#ffffff","#1a1a2e"),("dark","#ffffff","#1a1a2e")]:
            # the dark screenshot is made dark, then flipped back the way the app does before reading
            sp.set_content(page(bg,fg)); f=os.path.join(d,name+".png"); sp.screenshot(path=f)
            texts[name]=subprocess.run(["tesseract",f,"-","--psm","4"],capture_output=True,text=True).stdout
        print("OCR light:\n"+texts["light"][:400])
    else:
        print("tesseract not installed here: using a saved text sample")
        texts["light"]="DUTY FLIGHT TIME: 4H 50M\n16 Nov 26, Mon\nCHECK IN 05:10\nFR1001 STN 05:55 → DUB 07:10 EIEKL\nFR1002 DUB 07:45 → STN 09:00 EIEKL\nCHECK OUT 13:05\nDUTY FLIGHT TIME: 6H 10M\n17 Nov 26, Tue\nCHECK IN 13:30\nFR2201 STN 14:15 → LIS 17:05 EIDCL\nFR2202 LIS 17:40 → STN 20:25 EIDCL\nCHECK OUT 22:40"
    STUB="<script>window.__ocr=%s;window.Tesseract={createWorker:async()=>({recognize:async f=>({data:{text:window.__ocr[(f&&f.name)||'light']||window.__ocr.light}}),terminate:async()=>{}})};</script>"%json.dumps(texts)
    pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+STUB+html+"</body></html>"); pg.wait_for_timeout(500); print("errs:",errs[:2])
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    shot=os.path.join(d,"pick.png"); open(shot,"wb").write(b"\x89PNG\r\n\x1a\n")
    pg.set_input_files("#ocr-f",[shot]); pg.wait_for_timeout(1500)
    msg=pg.inner_text("#rostmsg"); print("app:",msg)
    assert "Read 1 picture" in pg.inner_text("main"), pg.inner_text("main")[:500]
    assert "brought in" in msg, msg
    import re
    n=int(re.search(r"(\d+) days? with times",msg).group(1)); print("days with times:",n); assert n==2, msg
    pg.clock.set_system_time(datetime.datetime(2026,11,16,4,0)); pg.wait_for_timeout(1200)
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(200); t=pg.inner_text("main").replace(" ","")
    for want in ["FR1001","FR1002","DUB"]: assert want in t, (want, t[:400])
    b.close()
print("ERRORS:", errs or "none")
