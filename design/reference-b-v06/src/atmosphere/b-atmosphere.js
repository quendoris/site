/* Quendoris temporal light. No telemetry, network access, geolocation or runtime libraries.
 * When dark scene=1, the accepted B v0.2 stylesheet and particle art are untouched. */
(function(){
'use strict';
const root=document.documentElement;
const KEY='quendoris.b.v06.';
const storage=(name)=>{try{return window[name]}catch{return {getItem(){return null},setItem(){},removeItem(){}}}};
const local=storage('localStorage'),session=storage('sessionStorage');
const get=(s,k)=>{try{return s.getItem(KEY+k)}catch{return null}};
const put=(s,k,v)=>{try{s.setItem(KEY+k,String(v))}catch{}};
const query=new URLSearchParams(location.search);
const number=String(query.get('qscene')??query.get('scene')??'');
const forced=/^[1-6]$/.test(number)?Number(number):null;
const requested=query.get('qtheme')||query.get('mode');
const forceMode=(requested==='dark'||requested==='light')?requested:null;
if(forced!==null)put(session,'scene',forced);
if(forceMode)put(session,'forced',forceMode);
let scene=forced ?? Number(get(session,'scene'));
if(!(scene>=1 && scene<=6)){
 const prior=Number(get(local,'counter'));
 scene=((Number.isFinite(prior)?prior:0)%6)+1;
 put(local,'counter',scene);
 put(session,'scene',scene);
}
const modes=['clock','system','light','dark'];
const saved=get(local,'mode');
let mode=forceMode||get(session,'forced')||(modes.includes(saved)?saved:'clock');
const sys=typeof matchMedia==='function'?matchMedia('(prefers-color-scheme: dark)'):null;
let timer=null;
function effective(){
 if(mode==='light'||mode==='dark')return mode;
 if(mode==='system')return sys?.matches?'dark':'light';
 const hour=new Date().getHours();
 return hour>=7&&hour<19?'light':'dark';
}
function apply(){
 root.dataset.qtheme=effective();
 root.dataset.qscene=String(scene);
 const meter=document.getElementById('qnd-scene');
 if(meter)meter.textContent=(effective()==='dark'?'NIGHT':'DAY')+' / '+String(scene).padStart(2,'0');
 const select=document.getElementById('qnd-mode');
 if(select)select.value=mode;
}
function schedule(){
 if(timer!==null)clearTimeout(timer);
 if(mode!=='clock')return;
 const now=new Date(),next=new Date(now);
 if(now.getHours()<7)next.setHours(7,0,0,20);
 else if(now.getHours()<19)next.setHours(19,0,0,20);
 else {next.setDate(next.getDate()+1);next.setHours(7,0,0,20);}
 timer=setTimeout(()=>{apply();schedule()},Math.max(500,Number(next)-Number(now)));
}
function ready(){
 apply();schedule();
 document.getElementById('qnd-mode')?.addEventListener('change',ev=>{
  if(!modes.includes(ev.target.value))return;
  mode=ev.target.value;
  put(local,'mode',mode);
  try{session.removeItem(KEY+'forced')}catch{}
  apply();schedule();
 });
 document.getElementById('qnd-next')?.addEventListener('click',()=>{
  scene=scene%6+1;
  put(session,'scene',scene);put(local,'counter',scene);
  const url=new URL(location.href);['qscene','scene','qtheme','mode'].forEach(k=>url.searchParams.delete(k));
  try{history.replaceState(null,'',url.pathname+url.search+url.hash)}catch{}
  apply();
 });
 document.getElementById('qnd-copy')?.addEventListener('click',event=>{
  const url=new URL(location.href);
  url.searchParams.set('qscene',String(scene));
  url.searchParams.set('qtheme',effective());
  const button=event.currentTarget;
  if(navigator.clipboard?.writeText)
   navigator.clipboard.writeText(url.href).then(()=>button.textContent='Скопировано')
    .catch(()=>button.textContent='Адрес: '+url.href);
  else button.textContent='Адрес: '+url.href;
 });
 document.addEventListener('visibilitychange',()=>{if(!document.hidden){apply();schedule()}});
 sys?.addEventListener?.('change',()=>{if(mode==='system')apply()});
}
// Run immediately in <head>: avoids theme flash. No modification to B geometry.
apply();
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});
else ready();
})();
