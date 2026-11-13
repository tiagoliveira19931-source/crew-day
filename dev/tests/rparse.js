// Reads roster text copied from a crew app screenshot (Google Lens / iPhone Live Text). Works offline.
const RP_MON={jan:1,feb:2,mar:3,apr:4,may:5,jun:6,jul:7,aug:8,sep:9,oct:10,nov:11,dec:12};
const RP_KIND={OFF:"off",DO:"off",HSBY:"standby",SBY:"standby",HS:"standby",ASBY:"asby",ADTY:"adty",TRNG:"training",TRG:"training",SIM:"training",L:"leave",AL:"leave",LVE:"leave",VTO:"vto",SICK:"sick",SCK:"sick",DUTY:"flying",FLY:"flying"};
function rpPad(n){return String(n).padStart(2,"0")}
function rpYear(m,y){if(y)return y<100?2000+y:y;const t=new Date(),cy=t.getFullYear(),cm=t.getMonth()+1;return m<cm-6?cy+1:m>cm+6?cy-1:cy}
function rpNorm(txt){return String(txt||"").replace(/\r/g,"").replace(/[✈✈️🛫🛬]/g," ").replace(/[|•·]/g," ").replace(/(\d)\s*[.:]\s*(\d\d)(?!\d)/g,"$1:$2")}
// List view: "12 Nov 26, Thu" headed blocks with Z times, airports, flight numbers and registrations.
function rpList(txt){
  const t=rpNorm(txt),re=/\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*,?\s*(\d{2,4})?\b/gi;
  const heads=[];let m;while((m=re.exec(t))){heads.push({i:m.index,end:re.lastIndex,date:rpYear(RP_MON[m[2].toLowerCase().slice(0,3)],m[3]?+m[3]:0)+"-"+rpPad(RP_MON[m[2].toLowerCase().slice(0,3)])+"-"+rpPad(+m[1])})}
  const out=[];
  heads.forEach((h,k)=>{
    const before=t.slice(k?heads[k-1].end:0,h.i),body=t.slice(h.end,k+1<heads.length?heads[k+1].i:t.length);
    // the block's type label sits just above the date (e.g. "DUTY  FLIGHT TIME: 8H 45M")
    const lab=(before.match(/\b(DUTY|HSBY|SBY|ASBY|ADTY|TRNG|TRG|SIM|OFF|VTO|SICK|LVE|AL)\b(?![\s\S]*\b(DUTY|HSBY|SBY|ASBY|ADTY|TRNG|TRG|SIM|OFF|VTO|SICK|LVE|AL)\b)/i)||[])[1];
    const times=[];const tr=/\b([01]?\d|2[0-3]):([0-5]\d)\b(\s*(LT|L\b|LCL))?/gi;let x;while((x=tr.exec(body))){if(!x[4])times.push(rpPad(+x[1])+":"+x[2])}
    const flts=(body.match(/\b(FR|RK|LS|EXS|RYR|RUK|U2|EZY|BA|W6)\s?\d{1,4}[A-Z]?\b/gi)||[]).map(f=>f.toUpperCase().replace(/\s/g,""));
    const aps=(body.replace(/\b(CHECK|IN|OUT|LT|DUTY|FLIGHT|TIME|MORE|ACTIONS|OFF|HSBY|ASBY|TRNG|VTO|SBY|UTC|THU|FRI|SAT|SUN|MON|TUE|WED)\b/gi," ").match(/\b[A-Z]{3}\b/g)||[]).filter(a=>!/^(FR|RK|LS|EXS|RYR|RUK|EZY)/.test(a)||a.length===3).filter(a=>IATA_OK(a));
    const regs=(body.match(/\b(9H[A-Z]{3}|EI[A-Z]{3}|G[A-Z]{4}|SP[A-Z]{3}|OE[A-Z]{3}|9H-[A-Z]{3}|EI-[A-Z]{3}|G-[A-Z]{4})\b/g)||[]).map(r=>r.replace("-",""));
    const kind=lab?(RP_KIND[lab.toUpperCase()]||"flying"):(flts.length?"flying":"");
    if(!kind)return;
    const e={date:h.date,kind,report:"",off:"",sectors:[]};
    if(kind==="flying"&&flts.length){
      const n=flts.length,ci=/CHECK\s*IN/i.test(body),co=/CHECK\s*OUT/i.test(body);
      let T=times.slice();if(ci)e.report=T.shift()||"";if(co&&T.length>2*n)e.off=T.pop()||"";
      // row order (dep,arr,dep,arr) or column order (deps… then arrs…): pick the one that runs forward in time
      const mins=s=>{const [a,b]=s.split(":").map(Number);return a*60+b};
      const fwd=arr=>{let ok=0;for(let i=0;i+1<arr.length;i++){const d=(mins(arr[i+1])-mins(arr[i])+1440)%1440;if(d>0&&d<10*60)ok++}return ok};
      let row=[],col=[];for(let i=0;i<n;i++){row.push(T[2*i],T[2*i+1])}
      // column reading puts check-out among the departures
      let C=times.slice();if(ci)C.shift();const left=C.slice(0,n+(co?1:0)),right=C.slice(n+(co?1:0));
      for(let i=0;i<n;i++)col.push(left[i],right[i]);
      const useCol=co&&C.length>=2*n+1&&fwd([e.report].concat(col,[left[n]]).filter(Boolean))>fwd([e.report].concat(row,[e.off]).filter(Boolean));
      const P=useCol?col:row;if(useCol){e.off=left[n]||"";}
      // airports: row reading = [ci, f1,t1, f2,t2, …, co]; column = [ci, f1, f2, …, co, t1, t2, …]
      let A=aps.slice();if(ci&&A.length>2*n)A.shift();
      const ar=[],ac=[];for(let i=0;i<n;i++){ar.push([A[2*i],A[2*i+1]])}
      const L=A.slice(0,n),R=A.slice(n+(co?1:0));for(let i=0;i<n;i++)ac.push([L[i],R[i]]);
      const chain=s=>s.reduce((ok,p,i)=>ok+(i&&s[i-1][1]===p[0]?1:0)+(p[0]&&p[1]&&p[0]!==p[1]?1:0),0);
      const AP=chain(ac)>chain(ar)?ac:ar;
      for(let i=0;i<n;i++)e.sectors.push({flt:flts[i],from:(AP[i]||[])[0]||"",to:(AP[i]||[])[1]||"",dep:P[2*i]||"",arr:P[2*i+1]||"",reg:regs[i]||regs[0]||""});
    }else{e.report=times[0]||"";e.off=times.length>1?times[times.length-1]:""}
    out.push(e);
  });
  return out;
}
function IATA_OK(a){return typeof IATA==="undefined"||!!IATA[a]||(typeof ICAO!=="undefined"&&!!ICAO[a])||/^(STN|LTN|LGW|LHR|MAN|BHX|EMA|LBA|NCL|GLA|EDI|BRS|BFS)$/.test(a)}
// Calendar view: "November 2026" then day numbers and codes (OFF, HSBY, VTO, TRNG, L, DUTY, or a number of flights).
function rpCal(txt){
  const t=rpNorm(txt),tok=t.split(/\s+/).filter(Boolean),out=[];
  const MN=["january","february","march","april","may","june","july","august","september","october","november","december"];
  let y=0,mo=0,next=1,pend=[],lastDay=false;
  for(let i=0;i<tok.length;i++){
    const w=tok[i],lw=w.toLowerCase().replace(/[^a-z]/g,"");
    const mi=MN.indexOf(lw);if(mi>=0&&/^\d{4}$/.test(tok[i+1]||"")){mo=mi+1;y=+tok[i+1];i++;next=1;pend=[];lastDay=false;continue}
    if(!mo)continue;
    if(/^(mon|tue|wed|thu|fri|sat|sun)$/i.test(w)){lastDay=false;continue}
    const n=/^\d{1,2}$/.test(w)?+w:null,code=w.toUpperCase().replace(/[^A-Z0-9]/g,"");
    if(n!==null&&n===next&&(!pend.length||lastDay)){pend.push(n);next++;lastDay=true;continue}
    let kind=null;
    if(n!==null&&n>=1&&n<=8)kind="flying";else if(RP_KIND[code])kind=RP_KIND[code];
    if(kind&&pend.length){const d=pend.shift();out.push({date:y+"-"+rpPad(mo)+"-"+rpPad(d),kind,report:"",off:"",sectors:[],n:kind==="flying"&&n?n:0});lastDay=false;continue}
    lastDay=false;
  }
  return out;
}
function rpParse(txt){const L=rpList(txt),C=rpCal(txt);return {list:L,cal:C}}
if(typeof module!=="undefined")module.exports={rpParse,rpList,rpCal};
