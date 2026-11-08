/* Quendoris Atmosphere v0.4 — local, deterministic, no telemetry.
   Stable identity, visit-dependent light fields. System time (not sunrise) defines
   07:00–18:59 light and 19:00–06:59 dark. No external requests. */
(function(){
 "use strict";
 const root=document.documentElement;
 const q=new URLSearchParams(location.search);
 const KEY="quendoris.atmosphere.v04.";
 const themes=["clock","system","light","dark"];
 const day=[
  ["#a8b5a6","#e8eee0","#f7f4ec","72%","26%","154deg"],
  ["#b5baa9","#e5e8d9","#f9f5ec","60%","25%","125deg"],
  ["#adbebc","#e3eeeb","#f9f8f0","83%","40%","164deg"],
  ["#c0b5a8","#eee8df","#fcf9f1","38%","19%","131deg"],
  ["#b1c0a8","#edf0e3","#f6f6ee","67%","50%","147deg"],
  ["#a9bfba","#e5edeb","#f7f7ed","48%","31%","120deg"]
 ];
 const night=[
  ["#4a6565","#213b40","#14272e","73%","24%","139deg"],
  ["#424952","#252536","#10121a","76%","36%","154deg"],
  ["#2e4e4e","#162d31","#0b141b","52%","24%","132deg"],
  ["#46505d","#222738","#11131a","69%","56%","168deg"],
  ["#394842","#1f3029","#0c1718","34%","23%","127deg"],
  ["#3a5053","#21313b","#10121b","80%","36%","145deg"]
 ];
 const sGet=(store,key)=>{try{return store.getItem(KEY+key)}catch{return null}};
 const sSet=(store,key,val)=>{try{store.setItem(KEY+key,val)}catch{}};
 const qScene=q.get("qscene"); const pinned=qScene!==null&&/^\d{1,7}$/.test(qScene)?Number(qScene):null;
 const qTheme=q.get("qtheme");const forcedMode=["light","dark"].includes(qTheme)?qTheme:null;
 if(forcedMode)sSet(sessionStorage,"preview",forcedMode);
 if(pinned!==null)sSet(sessionStorage,"scene",String(pinned));
 function visitIndex(){
  if(pinned!==null)return pinned;
  const cached=sGet(sessionStorage,"scene");
  if(cached!==null&&/^\d{1,7}$/.test(cached))return Number(cached);
  const old=sGet(localStorage,"counter");
  const next=old!==null&&/^\d{1,7}$/.test(old)?(Number(old)+1)%10000000:0;
  sSet(sessionStorage,"scene",String(next));sSet(localStorage,"counter",String(next));
  return next;
 }
 let index=visitIndex();
 const valid=(m)=>themes.includes(m);
 const preferred=sGet(localStorage,"mode");
 let mode=forcedMode||sGet(sessionStorage,"preview")||(valid(preferred)?preferred:"clock");
 if(!valid(mode))mode="clock";
 const media=typeof matchMedia==="function"?matchMedia("(prefers-color-scheme: dark)"):null;
 function effective(){
  if(mode==="light"||mode==="dark")return mode;
  if(mode==="system")return media&&media.matches?"dark":"light";
  const h=new Date().getHours();return h>=7&&h<19?"light":"dark";
 }
 const cleanHash=(n)=>{let z=(n+0x9e3779b9)>>>0;z^=z>>>16;z=Math.imul(z,0x85ebca6b);z^=z>>>13;return z>>>0;};
 function renderDots(theme){
  const field=document.querySelector(".identity-field");
  if(!field)return;
  const old=field.querySelector(".qnd-particles");if(old)old.remove();
  const ns="http://www.w3.org/2000/svg";const svg=document.createElementNS(ns,"svg");
  svg.setAttribute("class","qnd-particles");svg.setAttribute("aria-hidden","true");
  svg.setAttribute("focusable","false");svg.setAttribute("viewBox","0 0 500 500");
  let state=cleanHash(index^((theme==="dark")?0x53f41a:0x42a187));
  function rand(){state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;}
  for(let k=0;k<94;k++){
   const x=18+rand()*466;
   const y=20+rand()*459;
   const r=.45+Math.pow(rand(),3)*2.8;
   const c=document.createElementNS(ns,"circle");
   c.setAttribute("cx",x.toFixed(2));c.setAttribute("cy",y.toFixed(2));c.setAttribute("r",r.toFixed(2));
   c.setAttribute("fill","currentColor");
   c.setAttribute("opacity",(.12+rand()*.55).toFixed(2));
   svg.appendChild(c);
  }
  field.prepend(svg);
 }
 function apply(){
  const t=effective();const palette=(t==="dark"?night:day)[index%6];
  root.dataset.qtheme=t;root.dataset.qmode=mode;root.dataset.qscene=String(index%6+1);
  const keys=["--q-field-a","--q-field-b","--q-field-c","--q-light-x","--q-light-y","--q-angle"];
  keys.forEach((k,i)=>root.style.setProperty(k,palette[i]));
  root.style.setProperty("--q-dots-opacity",t==="dark"?.68:.42);
  root.style.setProperty("--q-shard-a",t==="dark"?"#eff4d0":"#42665a");
  root.style.setProperty("--q-shard-b",t==="dark"?"#658779":"#f5f2dc");
  const label=document.getElementById("qnd-scene-label");
  if(label)label.textContent=(t==="dark"?"NIGHT":"DAY")+" / "+String(index%6+1).padStart(2,"0");
  const ctl=document.getElementById("qnd-mode");if(ctl)ctl.value=mode;
  renderDots(t);
  return t;
 }
 // Set CSS variables in the document head to avoid theme flash.
 apply();
 function nextBoundary(){
  if(mode!=="clock")return;
  const now=new Date(),next=new Date(now);
  if(now.getHours()<7)next.setHours(7,0,0,100);
  else if(now.getHours()<19)next.setHours(19,0,0,100);
  else{next.setDate(next.getDate()+1);next.setHours(7,0,0,100)}
  const ms=Math.max(1000,next-now);
  // setTimeout maximum is approximately 24.8 days; our next boundary is <=12 h.
  timer=setTimeout(()=>{apply();nextBoundary();},ms);
 }
 let timer=null;
 function reschedule(){if(timer!==null)clearTimeout(timer);timer=null;nextBoundary()}
 function init(){
  apply();reschedule();
  document.getElementById("qnd-mode")?.addEventListener("change",(ev)=>{
   if(!valid(ev.target.value))return;
   mode=ev.target.value;
   sSet(localStorage,"mode",mode);
   try{sessionStorage.removeItem(KEY+"preview")}catch{}
   apply();reschedule();
  });
  document.getElementById("qnd-another")?.addEventListener("click",()=>{
   index=(index+1)%10000000;
   sSet(sessionStorage,"scene",String(index));sSet(localStorage,"counter",String(index));
   const url=new URL(location.href);url.searchParams.delete("qscene");url.searchParams.delete("qtheme");
   // Navigation drops pinned parameters and keeps all site pages consistent.
   history.replaceState(null,"",url.pathname+url.search+url.hash);
   apply();
  });
  document.getElementById("qnd-share")?.addEventListener("click",(ev)=>{
   const url=new URL(location.href);
   url.searchParams.set("qscene",String(index));url.searchParams.set("qtheme",effective());
   const btn=ev.currentTarget;
   if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(url.href).then(()=>{btn.textContent="Скопировано"}).catch(()=>{btn.textContent="Адрес: "+url.href});
   }else btn.textContent="Адрес: "+url.href;
  });
  document.addEventListener("visibilitychange",()=>{if(!document.hidden){apply();reschedule()}});
  media?.addEventListener?.("change",()=>{if(mode==="system")apply()});
 }
 if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});
 else init();
})();
