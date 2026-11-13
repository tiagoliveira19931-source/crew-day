import sys,datetime
from playwright.sync_api import sync_playwright
html=open(sys.argv[1]).read(); errs=[]
mock='''<script>
(()=>{const store={};const snap=(p)=>({id:p.split("/").pop(),exists:p in store,data:()=>store[p]&&JSON.parse(JSON.stringify(store[p])),metadata:{}});
const doc=p=>({path:p,get:async()=>snap(p),set:async d=>{store[p]=JSON.parse(JSON.stringify(d))},onSnapshot:()=>()=>{}});
store["issues/other"]={name:"Ana",airline:"Jet2",reports:[{id:"x1",date:"2026-10-20",kind:"idea",area:"Plan",text:"Dark mode schedule"}]};
const db={doc,collection:c=>({get:async()=>{const docs=Object.keys(store).filter(k=>k.startsWith(c+"/")&&k.split("/").length===2).map(snap);return {docs,size:docs.length,empty:!docs.length,docChanges:()=>[],metadata:{}}},doc:i=>doc(c+"/"+i)})};
const user={id:async()=>"me1",isOwner:async()=>true,canEdit:async()=>true};
window.__store=store;window.claude={use:async n=>n==="db"?db:n==="user"?user:null};})();
</script>'''
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844})
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.route("**/*",lambda r:r.abort() if r.request.url.startswith("http") else r.continue_())
    pg.clock.install(time=datetime.datetime(2026,11,11,15,0))
    pg.set_content("<!doctype html><html><head><meta charset=utf-8></head><body>"+mock+html+"</body></html>"); pg.wait_for_timeout(500)
    pg.fill("#pr-n","Tiago"); pg.fill("#pr-s","AB1"); pg.click("#setupdone")
    pg.click("[data-tab=more]"); pg.click('[data-more="issues"]')
    pg.click('[data-ikind="idea"]'); pg.select_option("#is-a","Trip"); pg.fill("#is-t","Add a gate change alert"); pg.click("#issend"); pg.wait_for_timeout(300)
    pg.click('[data-more=""]'); pg.click('[data-more="issues"]'); pg.wait_for_timeout(300)
    print(pg.inner_text("main").replace("\n"," | ")[:900])
    pg.click('[data-ist="x1:planned"]'); pg.wait_for_timeout(100); print("status store:",pg.evaluate("JSON.stringify(window.__store['issueStatus/main'])"))
    pg.screenshot(path="issues.png",full_page=True)
    print("ERRORS:",errs or "none")
