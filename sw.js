/* Crew Day service worker: keeps the app working offline. Bump VERSION on every upload. */
const VERSION="1.19.6";
const CACHE="crewday-"+VERSION;
const SHELL=["./","./index.html","./manifest.webmanifest","./icon-192.png","./icon-512.png","./icon-maskable-512.png","./apple-touch-icon.png"];
const CDN=["https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js"];
const RUNTIME_HOSTS=["cdnjs.cloudflare.com","cdn.jsdelivr.net","fonts.googleapis.com","fonts.gstatic.com"];

self.addEventListener("install",e=>{
  e.waitUntil((async()=>{
    const c=await caches.open(CACHE);
    await c.addAll(SHELL);
    await Promise.all(CDN.map(u=>fetch(u,{mode:"no-cors"}).then(r=>c.put(u,r)).catch(()=>{})));
    await self.skipWaiting();
  })());
});
self.addEventListener("activate",e=>{
  e.waitUntil((async()=>{
    for(const k of await caches.keys())if(k.startsWith("crewday-")&&k!==CACHE)await caches.delete(k);
    await self.clients.claim();
  })());
});
self.addEventListener("fetch",e=>{
  const req=e.request;if(req.method!=="GET")return;
  const url=new URL(req.url);
  if(req.mode==="navigate"){
    /* app page: try the network for updates, fall back to the saved copy offline */
    e.respondWith(fetch(req).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put("./index.html",copy));return r}).catch(()=>caches.match("./index.html")));
    return;
  }
  if(url.origin===location.origin){
    e.respondWith(caches.match(req).then(hit=>hit||fetch(req)));
    return;
  }
  if(RUNTIME_HOSTS.includes(url.hostname)){
    /* libraries and fonts: use the saved copy, refresh it in the background */
    e.respondWith(caches.open(CACHE).then(async c=>{
      const hit=await c.match(req);
      const net=fetch(req).then(r=>{c.put(req,r.clone());return r}).catch(()=>hit);
      return hit||net;
    }));
  }
});
