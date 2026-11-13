# Read roster screenshots on the phone. Uses a saved engine reading with the quirks seen on real Ryanair screens
# (dark mode): O for 0, S/E inside flight numbers, "vIo" for VTO, flight numbers a line below their times, LT lines,
# a duty checking out after midnight, and a second picture starting mid-month. All flights and dates are invented.
# Also checks the app's picture preparation turns a dark screen with a coloured badge into black-on-white.
import datetime, json, base64, os, tempfile
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
PIC1="""€ Rester Legend C
DUTY FLIGHT TIME: 4H 20M
16 Nov 26, Mon —— —
05:10 Z STN CHECK IN
05:10 LT
05:55 Z STN “ + FRS5101 DUB 07:10 Z
05:55 LT 9HAAA 07:10 LT
07:45 Z DUB ~ »FRE102 > STN 09:00 Z
09:30 Z STN CHECK OUT
DUTY
17 Nov 26, Tue —— —
04:00 Z STN ~ HSBY 15:00 Z
04:00 LT HSBY 15:00 LT
DAY OFF
18 Nov 26, Wed —— —
02:00 Z STN “ vIo 22:00 Z
02:00 LT — WO 22:00 LT
DUTY FLIGHT TIME: 3H 40M
19 Nov 26, Thu —— —
18:20 Z STN CHECK IN
19:05 Z STN a ~ BGY 20:45 Z
19:05 LT FR2301 21:45 LT
21:25 Z BGY c > STN 23:33 Z
21:25 LT FR2302 23:33 LT
20 Nov 26, Fri —— —
00:03 Z STN CHECK OUT
DUTY
21 Nov 26, Sat —— —
08:00 Z STN CHECK IN
Calendar VTO Hub"""
PIC2="""€ Rester Legend C
DAY OFF
24 Nov 26, Tue —— —
00:00 Z | OFF ) 21:00 Z
_ OFF _
25 Nov 26, Wed —— —
08:00 Z STN CHECK IN
08:00 Z STN Training 17:25 Z
17:25 Z CHECK OUT
26 Nov 26, Thu
05:4O Z STN CHECK IN
05:40 Z STN ~ Airport Duty 13:40 Z
13:40 Z CHECK OUT"""
WANT={"2026-11-16":("flying","05:10","09:30",["FR5101","FR6102"]),"2026-11-17":("standby","04:00","15:00",[]),"2026-11-18":("vto","","",[]),
      "2026-11-19":("flying","18:20","00:03",["FR2301","FR2302"]),"2026-11-24":("off","","",[]),"2026-11-25":("training","08:00","17:25",[]),"2026-11-26":("adty","05:40","13:40",[])}
STUB="<script>window.__r=%s;window.Tesseract={createWorker:async()=>({setParameters:async()=>{},recognize:async()=>({data:{text:window.__r.shift()||''}}),terminate:async()=>{}})};</script>"%json.dumps([PIC1,PIC2])
PAGE="<!doctype html><html><head><meta charset=utf-8></head><body>"+STUB+html+"</body></html>"
DARK="<body style='margin:0;background:#212226;width:400px;height:120px'><div style='margin:30px;width:160px;height:56px;border-radius:10px;background:#607fbc;color:#242a3b;font:700 20px Arial;display:grid;place-items:center'>FR1234</div></body>"
d=tempfile.mkdtemp()
with sync_playwright() as p:
    b=p.chromium.launch()
    sp=b.new_page(viewport={"width":400,"height":120}); sp.set_content(DARK); shot=sp.screenshot(); sp.close()
    pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.fulfill(body=PAGE,content_type="text/html") if r.request.url=="https://t.test/" else r.abort())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0)); pg.goto("https://t.test/")
    # picture preparation: only black and white, mostly white, with dark marks where the badge text is
    st=pg.evaluate("""async d=>{const b=await (await fetch('data:image/png;base64,'+d)).blob();const c=await window.CREWDAY_TEST.ocrPrep(new File([b],'s.png',{type:'image/png'}));
      const x=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let bw=0,blk=0,n=0,mid=0;for(let i=0;i<x.length;i+=4){n++;if(x[i]===0||x[i]===255)bw++;if(x[i]===0)blk++}
      const W=c.width,y0=Math.round(c.height*0.4),y1=Math.round(c.height*0.6);for(let yy=y0;yy<y1;yy++)for(let xx=Math.round(W*0.1);xx<Math.round(W*0.45);xx++)if(x[(yy*W+xx)*4]===0)mid++;
      return {bw:bw/n,black:blk/n,mid}}""",base64.b64encode(shot).decode())
    print("prep:",st); assert st["bw"]==1 and st["black"]<0.25 and st["mid"]>50, st
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    fp=os.path.join(d,"s.png"); open(fp,"wb").write(shot)
    pg.set_input_files("#ocr-f",[fp,fp]); pg.wait_for_function("document.querySelector('main').innerText.includes('Read 2 pictures')||document.querySelector('main').innerText.includes('Couldn')||document.querySelector('main').innerText.includes('went wrong')",timeout=20000)
    print("app:",pg.inner_text("#rostmsg"))
    R=pg.evaluate("(()=>{for(const k of Object.keys(localStorage)){try{const j=JSON.parse(localStorage.getItem(k));if(j&&j.roster)return j.roster}catch(e){}}return {}})()")
    got={k:(v.get("kind"),v.get("report") or "",v.get("off") or "",[s.get("flt") for s in v.get("sectors",[])]) for k,v in R.items()}
    for k in sorted(got): print(k,got[k])
    for k,v in WANT.items(): assert got.get(k)==v, (k,got.get(k),v)
    assert got.get("2026-11-21",("",))[0]=="flying" and "2026-11-20" not in got, "21 Nov cut off; 20 Nov is the overnight end of 19 Nov"
    b.close()
print("ERRORS:", errs or "none")
