"""Builds the installable Crew Day app (PWA) from the shared source file.

Usage: python3 build.py <source html> <output folder> <version>
All output files sit in one flat folder so they are easy to upload from a phone.
"""
import json, os, re, sys
from PIL import Image, ImageDraw

src, out, version = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
body = open(src, encoding="utf-8").read()

# Pull the <title> and the font link into <head>; everything else is page content.
body = re.sub(r"^<title>.*?</title>\n", "", body, count=1)
body = re.sub(r'^<meta name="claude:viewport-fit-sides"[^>]*>\n', "", body, count=1, flags=re.M)

head = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Crew Day</title>
<meta name="description" content="Your duty day, planned: alarms, roster, kit, pay and more for cabin crew.">
<meta name="theme-color" content="#F4F8F8">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Crew Day">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<style>
:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);color-scheme:light}}
body{{margin:0;font:14px system-ui,-apple-system,sans-serif}}
img{{max-width:100%}}
[hidden]{{display:none!important}}
</style>
<script>window.CREWDAY_PWA=true;window.CREWDAY_VERSION="{version}";</script>
</head>
<body>
"""
tail = """
<script>
if("serviceWorker" in navigator){window.addEventListener("load",()=>{navigator.serviceWorker.register("sw.js").catch(()=>{})})}
</script>
</body>
</html>
"""
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(head + body + tail)

manifest = {
    "name": "Crew Day",
    "short_name": "Crew Day",
    "description": "Your duty day, planned: alarms, roster, kit, pay and more for cabin crew.",
    "start_url": "./",
    "scope": "./",
    "id": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#F4F8F8",
    "theme_color": "#2E7D84",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
    "shortcuts": [
        {"name": "I've been called", "short_name": "Called", "description": "Start the standby call-out countdown", "url": "./?called=1", "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}]},
    ],
}
open(os.path.join(out, "manifest.webmanifest"), "w").write(json.dumps(manifest, indent=2))

CDN = [
    "https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js",
]
sw = f"""/* Crew Day service worker: keeps the app working offline. Bump VERSION on every upload. */
const VERSION="{version}";
const CACHE="crewday-"+VERSION;
const SHELL=["./","./index.html","./manifest.webmanifest","./icon-192.png","./icon-512.png","./icon-maskable-512.png","./apple-touch-icon.png"];
const CDN={json.dumps(CDN)};
const RUNTIME_HOSTS=["cdnjs.cloudflare.com","cdn.jsdelivr.net","fonts.googleapis.com","fonts.gstatic.com"];

self.addEventListener("install",e=>{{
  e.waitUntil((async()=>{{
    const c=await caches.open(CACHE);
    await c.addAll(SHELL);
    await Promise.all(CDN.map(u=>fetch(u,{{mode:"no-cors"}}).then(r=>c.put(u,r)).catch(()=>{{}})));
    await self.skipWaiting();
  }})());
}});
self.addEventListener("activate",e=>{{
  e.waitUntil((async()=>{{
    for(const k of await caches.keys())if(k.startsWith("crewday-")&&k!==CACHE)await caches.delete(k);
    await self.clients.claim();
  }})());
}});
self.addEventListener("fetch",e=>{{
  const req=e.request;if(req.method!=="GET")return;
  const url=new URL(req.url);
  if(req.mode==="navigate"){{
    /* app page: try the network for updates, fall back to the saved copy offline */
    e.respondWith(fetch(req).then(r=>{{const copy=r.clone();caches.open(CACHE).then(c=>c.put("./index.html",copy));return r}}).catch(()=>caches.match("./index.html")));
    return;
  }}
  if(url.origin===location.origin){{
    e.respondWith(caches.match(req).then(hit=>hit||fetch(req)));
    return;
  }}
  if(RUNTIME_HOSTS.includes(url.hostname)){{
    /* libraries and fonts: use the saved copy, refresh it in the background */
    e.respondWith(caches.open(CACHE).then(async c=>{{
      const hit=await c.match(req);
      const net=fetch(req).then(r=>{{c.put(req,r.clone());return r}}).catch(()=>hit);
      return hit||net;
    }}));
  }}
}});
"""
open(os.path.join(out, "sw.js"), "w").write(sw)


def icon(size, maskable=False):
    """Navy tile, amber sun rising over the horizon: an early report."""
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    navy, amber, white = (27, 42, 74, 255), (242, 169, 59, 255), (244, 241, 234, 255)
    if maskable:
        d.rectangle([0, 0, s, s], fill=navy)
        k = 0.72
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=navy)
        k = 0.86
    cx, hy = s / 2, s * (0.5 + 0.12 * k)
    r = s * 0.27 * k
    d.pieslice([cx - r, hy - r, cx + r, hy + r], 180, 360, fill=amber)
    for i in range(1, 6):
        import math
        a = math.radians(180 + 30 * i)
        r1, r2 = r * 1.22, r * 1.48
        d.line([cx + r1 * math.cos(a), hy + r1 * math.sin(a), cx + r2 * math.cos(a), hy + r2 * math.sin(a)], fill=amber, width=int(s * 0.03 * k))
    lw = int(s * 0.035 * k)
    d.line([cx - s * 0.36 * k, hy, cx + s * 0.36 * k, hy], fill=white, width=lw)
    d.line([cx - s * 0.22 * k, hy + s * 0.1 * k, cx + s * 0.22 * k, hy + s * 0.1 * k], fill=white, width=int(lw * 0.8))
    return im.resize((size, size), Image.LANCZOS)


icon(192).save(os.path.join(out, "icon-192.png"))
icon(512).save(os.path.join(out, "icon-512.png"))
icon(512, maskable=True).save(os.path.join(out, "icon-maskable-512.png"))
ap = Image.new("RGBA", (180, 180), (27, 42, 74, 255))
ap.alpha_composite(icon(180, maskable=True))
ap.convert("RGB").save(os.path.join(out, "apple-touch-icon.png"))
print("built", out)
