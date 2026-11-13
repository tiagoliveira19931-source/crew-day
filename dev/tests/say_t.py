# Useful words: each phrase has a speaker button that reads it in the local language with the phone's voice.
import datetime
from playwright.sync_api import sync_playwright
html=open("/home/claude/crew-day.html").read(); errs=[]
STUB="""<script>window.__said=[];window.SpeechSynthesisUtterance=function(t){this.text=t};
Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{getVoices:()=>[{lang:'pt-PT',name:'Joana',localService:true}],speak:u=>window.__said.push([u.text,u.lang,u.voice&&u.voice.name,u.rate]),cancel:()=>{},onvoiceschanged:null}});</script>"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,13,9,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+STUB+html+"</body></html>")
    pg.fill("#pr-n","T"); pg.fill("#pr-s","A"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="roster"]'); pg.wait_for_timeout(150)
    pg.fill("#rost-p","2026-11-13 | DUTY | 15:00 | 23:30 | FR10 STN-LIS 15:45-18:50; FR11 LIS-STN 19:30-22:30"); pg.click("#pasteroster"); pg.wait_for_timeout(150)
    pg.click("[data-tab=trip]"); pg.wait_for_timeout(200)
    f=pg.locator('[data-fold^="words"]')
    if not f.count(): print("no words fold"); raise SystemExit
    if f.get_attribute("aria-expanded")=="false": f.click()
    pg.wait_for_timeout(100); n=pg.locator("[data-say]").count(); print("speak buttons:",n); assert n>=10
    pg.locator('[data-say^="p|1"]').click(); pg.wait_for_timeout(100)
    said=pg.evaluate("window.__said"); print(said); assert said and said[-1][0]=="Obrigado, Obrigada" and said[-1][1]=="pt-PT" and said[-1][2]=="Joana"
    pg.uncheck("#sayslow"); pg.locator('[data-say^="p|0"]').click(); pg.wait_for_timeout(100)
    said=pg.evaluate("window.__said"); assert said[-1][3]>0.9, said[-1]
    b.close()
print("ERRORS:", errs or "none")
