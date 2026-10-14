
/* =====================================================================
   MAP-A CARE
   ---------------------------------------------------------------------
   The hospital app of the revised paper, "Right Hospital, Right Bed,
   Right Time". It runs on the MAP-A network, places and registry records
   above and adds what the revision defines:

     Definition 13, Equation 12  the service list of each hospital
     Definition 16               the patient profile: acuity, needed
                                 services, payment class and walking ability
     Definition 17               suitability with the service factor
     Definition 18               the nearest suitable hospital and backups
     Definition 20               the payment, need and mobility gaps
     Definitions 21 to 23        catchments, beds per person, bed deserts
     Definition 24               surge assignment of many patients
     Definition 25               critical roads
     Definition 26               Malasakit Center site selection

   Function declarations below replace the MAP-A ones of the same name;
   everything else in the file is the MAP-A engine, unchanged.
   This is navigation and planning support. It does not diagnose, triage
   or advise on treatment, and it never replaces a call to 911.
   ===================================================================== */
const CARE_VERSION="1.0";

/* Table 8. The services a patient can need, with the lowest level that
   offers each by default under the DOH (2012) classification. */
const NEEDS=[
  {c:"ISO", t:"Isolation",            d:"A contagious illness that must be kept apart", lv:1},
  {c:"MAT", t:"Normal delivery",      d:"A woman in uncomplicated labor",                lv:1},
  {c:"OR",  t:"Operation",            d:"A condition that needs an operating room",       lv:1},
  {c:"ICU", t:"Intensive care",       d:"Needs close monitoring or life support",         lv:2},
  {c:"NICU",t:"Newborn intensive care",d:"A premature or sick newborn",                   lv:2},
  {c:"HRP", t:"High-risk pregnancy",  d:"Bleeding, very high blood pressure, other complications", lv:2},
  {c:"DIA", t:"Dialysis",             d:"Kidney failure",                                 lv:3},
  {c:"BB",  t:"Blood bank",           d:"Has lost a large amount of blood",               lv:3}
];
const needName=c=>{ const n=NEEDS.find(x=>x.c===c); return n?n.t:c; };
/* Equation 12. A hospital offers the default list of its level unless a
   published register entry for that facility adds or removes a service.
   No such entry is on record for any Albay facility, so both are empty;
   an entry goes here as SVC_ADD.brhmc=["..."] with its source in a comment. */
const SVC_ADD={}, SVC_DEL={};
function servicesOf(id){
  const H=HOSP[id];
  if (!H||H.svcU) return [];
  const out=NEEDS.filter(n=>H.svc>=n.lv&&H.svc>0).map(n=>n.c);
  (SVC_ADD[id]||[]).forEach(c=>{ if (out.indexOf(c)<0) out.push(c); });
  return out.filter(c=>(SVC_DEL[id]||[]).indexOf(c)<0);
}
/* Equation 11 asks whether a government hospital hosts a Malasakit Center.
   Republic Act No. 11463, Section 3, requires one in every DOH hospital,
   and the Bicol Regional Hospital and Medical Center is DOH-retained, so it
   is cost class 0 by law. Every other government facility stays in class 1
   until the DOH Malasakit directory confirms a center there. */
if (HOSP.brhmc){ HOSP.brhmc.q=0; HOSP.brhmc.qU=0; HOSP.brhmc.qLaw=1; }

/* Definition 16, mobility class. The slow class is for an older person, a
   woman late in pregnancy, or someone with a disability or an injury. Both
   values are declared design parameters, to be replaced by local data. */
const MOBILITY={
  std: {t:"Walks normally", sub:"", kmh:CFG.walkKmh, cap:CFG.maxWalkKm},
  slow:{t:"Walks slowly",   sub:"", kmh:3.0, cap:Math.round(CFG.maxWalkKm*2/3*10)/10}
};
MOBILITY.std.sub=MOBILITY.std.kmh+" km/h, up to "+MOBILITY.std.cap+" km on foot per leg";
MOBILITY.slow.sub="Older person, late pregnancy, disability or injury · "+MOBILITY.slow.kmh+
                  " km/h, up to "+MOBILITY.slow.cap+" km on foot per leg";
let WALK_CAP=CFG.maxWalkKm;
function withMobility(m,fn){
  const M=MOBILITY[m]||MOBILITY.std, k0=CFG.walkKmh, c0=WALK_CAP;
  CFG.walkKmh=M.kmh; WALK_CAP=M.cap;
  try{ return fn(); } finally { CFG.walkKmh=k0; WALK_CAP=c0; }
}
/* The MAP-A transit search, with walking legs limited by the mobility class. */
function transitRoute(o,d,pref,level,whenMin){
  if (o===d) return null;
  const walks=WALKS.filter(w=>w.km<=WALK_CAP);
  [o,d].forEach(function(p){
    if (!STATIONS[p] && !walks.some(w=>w.a===p||w.b===p)){
      const n=nearestStation(p);
      if (n.st) walks.push({a:p,b:n.st,km:n.km,long:true});
    }
  });
  const W = pref==="few"   ? {time:1,xfer:22,fare:0}
          : pref==="cheap" ? {time:1,xfer:6,fare:1.6}
          : pref==="short" ? {time:1,xfer:8,fare:0}
          : {time:1,xfer:6,fare:0};
  const dist={},prev={},seen={};
  const key=(n,t)=>n+"||"+t;
  const h=new Heap();
  dist[key(o,"walk")]=0; h.push(0,key(o,"walk"));
  const real={}; real[key(o,"walk")]=0;
  while (h.size()){
    const top=h.pop(), k=top[1];
    if (seen[k]) continue; seen[k]=true;
    const parts=k.split("||"), node=parts[0], tag=parts[1];
    if (node===d){
      const raw=[]; let cur=k;
      while (prev[cur]){ raw.push(prev[cur].leg); cur=prev[cur].from; }
      raw.reverse();
      return assembleTransit(raw,real[k],o,d);
    }
    const passing = tag!=="walk" && PASSBY(node) && node!==d;
    if (!passing) walks.forEach(function(w){
      let to=null;
      if (w.a===node) to=w.b; else if (w.b===node) to=w.a;
      if (!to) return;
      const m=walkMin(w.km), nk=key(to,"walk");
      const nd=dist[k]+m*W.time*1.15;
      if (nd<(dist[nk]===undefined?Infinity:dist[nk])){
        dist[nk]=nd; real[nk]=real[k]+m;
        prev[nk]={from:k,leg:{kind:"walk",a:node,b:to,km:w.km,min:m,long:!!w.long}};
        h.push(nd,nk);
      }
    });
    SVC_EDGES.forEach(function(e){
      if (e.a!==node) return;
      const changing = (tag!==e.svc.id);
      if (changing && passing) return;
      const wait = changing ? e.svc.h/2 + (tag!=="walk"?CFG.transferPenaltyMin:CFG.boardPenaltyMin) : 0;
      const boardAt = whenMin!=null ? whenMin+real[k]+wait : null;
      if (changing && boardAt!=null && !svcRuns(e.svc,boardAt)) return;
      const rm=rideMin(e,level);
      const km=edgeKm(e);
      const fare=legFare(km,e.svc.mode,"none");
      const nk=key(e.b,e.svc.id);
      const nd=dist[k]+(wait+rm)*W.time+(changing&&tag!=="walk"?W.xfer:0)+fare*W.fare;
      if (nd<(dist[nk]===undefined?Infinity:dist[nk])){
        dist[nk]=nd; real[nk]=real[k]+wait+rm;
        prev[nk]={from:k,leg:{kind:"ride",a:e.a,b:e.b,km:km,min:rm,wait:wait,svc:e.svc,e:e,
          boardAt:changing?boardAt:null}};
        h.push(nd,nk);
      }
    });
  }
  return null;
}

/* Definition 17. Five factors: level, services, emergency room, beds, cost.
   An unreported hospital stays in the set: not answering is not being full.
   For an emergency the cost factor is 1 (Republic Act No. 10932); the
   service factor stays on, because the law removes a deposit, not a
   missing neonatal ICU. ignoreFull is for the surge assignment, where free
   beds are counted directly. */
function suitable(id,kappa,rho,now,needs,ignoreFull){
  const H=HOSP[id]; if (!H) return false;
  const a=ACUITY.find(x=>x.k===kappa)||ACUITY[2];
  if (H.svc < a.lam) return false;
  if (needs&&needs.length){
    const s=servicesOf(id);
    if (needs.some(c=>s.indexOf(c)<0)) return false;
  }
  if (a.ke && H.er!==1) return false;
  if (!ignoreFull && bedStatus(id,now).st==="FULL") return false;
  if (!a.ke && H.q>rho) return false;
  return true;
}
function whyNot(id,kappa,rho,now,needs){
  const H=HOSP[id], a=ACUITY.find(x=>x.k===kappa)||ACUITY[2], why=[];
  if (H.svc<a.lam) why.push(H.svcU?"no licence level on record":"below "+SVC_NAME[a.lam].toLowerCase());
  const s=servicesOf(id), miss=(needs||[]).filter(c=>s.indexOf(c)<0);
  if (miss.length) why.push("does not offer "+miss.map(needName).join(", ").toLowerCase());
  if (a.ke&&H.er!==1) why.push("no emergency room");
  if (bedStatus(id,now).st==="FULL") why.push("reported full");
  if (!a.ke&&H.q>rho) why.push("cost class "+H.q+" is above the chosen payment class");
  return why;
}

/* Travel times to every hospital, kept while the network, the traffic level
   and the walking class stay the same. A patient standing at the hospital
   itself is there in no time; MAP-A's router returns nothing for o===d. */
const careTimeCache={};
function careSig(){ return ROADS.length+":"+ROADS.reduce((a,r)=>a+r.km,0).toFixed(4); }
function careTimes(origin,mode,level,mob){
  const lv=level||trafficLevel, m=mode==="amb"?"std":(mob||"std");
  const key=origin+"|"+mode+"|"+lv+"|"+m+"|"+careSig();
  if (careTimeCache[key]) return careTimeCache[key];
  const out={};
  withMobility(m,function(){
    Object.keys(HOSP).forEach(function(id){
      if (!P[id]) return;
      if (id===origin){ out[id]={min:0,km:0,route:null,kind:mode==="amb"?"road":"transit",lb:false,here:true}; return; }
      let t=hospTime(origin,id,mode,lv);
      if (mode!=="amb"){
        /* within walking distance, walking is a journey too */
        const km=hav(P[origin].ll,P[id].ll)*CFG.walkFactor;
        if (km<=WALK_CAP){
          const wm=walkMin(km);
          if (!t||wm<t.min) t={min:wm,km:km,route:null,kind:"walk",lb:!!(P[id]&&P[id].approx),
                               coords:[P[origin].ll,P[id].ll]};
        }
      }
      out[id]=t;
    });
  });
  careTimeCache[key]=out;
  return out;
}
/* Definition 18. The nearest suitable hospital and the ranked backups. */
function nearestSuitable(origin,kappa,rho,mode,level,needs,mob){
  const now=Date.now(), T=careTimes(origin,mode,level,mob), out=[];
  Object.keys(HOSP).forEach(function(id){
    if (!P[id]) return;
    out.push({id:id,ok:suitable(id,kappa,rho,now,needs),t:T[id]||null,bed:bedStatus(id,now)});
  });
  const fit=out.filter(x=>x.ok&&x.t).sort(function(a,b){
    return a.t.min-b.t.min
        || (a.t.lb?1:0)-(b.t.lb?1:0)
        || (b.bed.free||0)-(a.bed.free||0)
        || (a.id<b.id?-1:1);
  });
  return {best:fit[0]||null,all:out,ranked:fit};
}
/* Definition 19 is unchanged in MAP-A; it reads the travel times above. */
function stabilisation(origin,kappa,best,mode,level,mob){
  if (kappa!==1||!best||!best.t) return null;
  const now=Date.now(), T=careTimes(origin,mode,level,mob);
  let near=null;
  Object.keys(HOSP).forEach(function(id){
    if (!P[id]||HOSP[id].er!==1||!T[id]) return;
    if (bedStatus(id,now).st==="FULL") return;
    if (!near||T[id].min<near.t.min) near={id:id,t:T[id]};
  });
  if (!near||near.id===best.id) return null;
  return (near.t.min+THETA_STAB < best.t.min) ? near : null;
}
/* Definition 20. The three gaps, with infinity minus infinity taken as 0. */
function gapOf(lim,base){
  if (!lim&&!base) return {gap:0};
  if (!lim) return {gap:Infinity,base:base};
  if (!base) return {gap:0};
  return {gap:Math.max(0,lim.t.min-base.t.min),lim:lim,base:base};
}
function paymentGap(origin,kappa,rho,mode,level,needs,mob){
  const a=ACUITY.find(x=>x.k===kappa);
  if (a&&a.ke) return {gap:0};
  const g=gapOf(nearestSuitable(origin,kappa,rho,mode,level,needs,mob).best,
                nearestSuitable(origin,kappa,3,mode,level,needs,mob).best);
  g.any=g.base; return g;
}
function needGap(origin,kappa,rho,mode,level,needs,mob){
  if (!needs||!needs.length) return null;
  return gapOf(nearestSuitable(origin,kappa,rho,mode,level,needs,mob).best,
               nearestSuitable(origin,kappa,rho,mode,level,[],mob).best);
}
function mobilityGap(origin,kappa,rho,level,needs){
  return gapOf(nearestSuitable(origin,kappa,rho,"pt",level,needs,"slow").best,
               nearestSuitable(origin,kappa,rho,"pt",level,needs,"std").best);
}

/* =====================================================================
   PATIENT SCREEN
   ===================================================================== */
let hmNeeds=[], hmMob="std", hmLast=null;
const careIco={
  cross:'<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M12 7.6v8.8M7.6 12h8.8"/><rect x="3.4" y="3.4" width="17.2" height="17.2" rx="4"/></svg>',
  plan:'<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M9 4.5 3.5 6.6v13l5.5-2.1 6 2.1 5.5-2.1v-13L15 6.6z"/><path d="M9 4.5v13M15 6.6v13"/></svg>',
  bed:'<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6v13M3 15h18v4"/><path d="M21 15v-3a3 3 0 0 0-3-3h-7v6"/><circle cx="7" cy="11.5" r="1.8"/></svg>',
  map:'<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0C18.5 15.4 12 21 12 21z"/><circle cx="12" cy="10" r="2.4"/></svg>',
  dir:'<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.8 21.2 12 12 21.2 2.8 12z"/><path d="M9.5 14.5v-2.2a1.6 1.6 0 0 1 1.6-1.6h4.2M13.4 8.6l2 2.1-2 2.1"/></svg>',
  more:'<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><circle cx="5.5" cy="12" r="1.9"/><circle cx="12" cy="12" r="1.9"/><circle cx="18.5" cy="12" r="1.9"/></svg>'
};
function renderHospitalPanel(){
  const a=ACUITY.find(x=>x.k===hmAcuity), emerg=!!a.ke;
  let h='<div class="cr-head"><div class="cr-badge">'+careIco.cross+'</div>'+
    '<div style="flex:1"><div class="cr-title">MAP-A Care</div>'+
    '<div class="cr-sub">Right hospital, right bed, right time</div></div>'+
    '<button id="hmExit" class="mini-btn" style="width:auto;margin:0;padding:7px 13px">Map</button></div>';
  h+='<div class="hm-note"><b>Navigation support, not triage.</b> MAP-A Care does not assess the patient and '+
     'does not replace 911 or the judgment of an ambulance crew. In an emergency, call 911 now.</div>';
  h+='<a class="hm-911" href="tel:911">Call 911</a>';

  h+='<div class="hm-h">1 · Where the patient is</div>';
  const on=hmOriginName();
  h+='<button class="hm-opt" id="hmOrig" aria-pressed="'+(on?"true":"false")+'"><b>'+
     (on?esc(on):"Choose a starting point")+'</b><span>'+
     (on?"Tap to change":"Your position, or any place on the map")+'</span></button>';

  h+='<div class="hm-h">2 · How the patient travels</div><div class="hm-row">'+
     '<button class="hm-opt" data-hmmode="amb" aria-pressed="'+(hmMode==="amb")+'" style="flex:1"><b>Ambulance</b>'+
     '<span>On roads an ambulance can use</span></button>'+
     '<button class="hm-opt" data-hmmode="pt" aria-pressed="'+(hmMode==="pt")+'" style="flex:1"><b>Commute</b>'+
     '<span>Jeepney, van, bus and on foot</span></button></div>';
  if (hmMode==="pt"){
    h+='<div class="hm-row">'+["std","slow"].map(function(m){
      return '<button class="hm-opt" data-mob="'+m+'" aria-pressed="'+(hmMob===m)+'" style="flex:1"><b>'+
             esc(MOBILITY[m].t)+'</b><span>'+esc(MOBILITY[m].sub)+'</span></button>';
    }).join("")+'</div>';
  }

  h+='<div class="hm-h">3 · How the patient is</div>';
  ACUITY.forEach(function(x){
    h+='<button class="hm-opt" data-acuity="'+x.k+'" aria-pressed="'+(hmAcuity===x.k)+'">'+
       '<b>'+x.k+'. '+esc(x.t)+'</b><span>Needs at least '+esc(SVC_NAME[x.lam])+
       (x.ke?' · emergency room required':'')+'</span></button>';
  });

  h+='<div class="hm-h">4 · What the patient needs</div>'+
     '<div class="cr-needs" role="group" aria-label="Services the patient needs">'+
     '<button class="cr-need" data-need="" aria-pressed="'+(!hmNeeds.length)+'"><b>No particular need</b>'+
     '<span>Any hospital at the right level</span></button>';
  NEEDS.forEach(function(n){
    h+='<button class="cr-need" data-need="'+n.c+'" aria-pressed="'+(hmNeeds.indexOf(n.c)>=0)+'"><b>'+
       esc(n.t)+'</b><span>'+esc(n.d)+'</span></button>';
  });
  h+='</div><div class="cr-fine">Choose from what the patient or a referral slip says. MAP-A Care matches it to '+
     'the services each hospital level offers; it does not decide what the patient needs.</div>';

  h+='<div class="hm-h">5 · What the family can pay</div>';
  if (emerg){
    h+='<div class="hm-bad">The cost filter is off for this patient. Republic Act No. 10932 forbids asking for a '+
       'deposit or advance payment before basic emergency care in an emergency or serious case, so every '+
       'hospital stays in the search whatever its cost class.</div>';
  } else {
    PAYCLASS.forEach(function(x){
      h+='<button class="hm-opt" data-pay="'+x.r+'" aria-pressed="'+(hmPay===x.r)+'">'+
         '<b>'+esc(x.t)+'</b><span>'+esc(x.sub)+'</span></button>';
    });
  }

  h+='<button class="hm-go" id="hmGo">Find the right hospital</button>';
  h+='<div id="hmResult"></div>';
  h+='<div class="cr-tools">'+
     '<button class="step" id="hmBeds" style="width:100%;text-align:left"><span class="step-i">'+careIco.bed+'</span>'+
     '<span class="step-b"><span class="step-t">Bed dashboard</span><span class="step-s">Free beds and report age, '+
     'town by town</span></span></button>'+
     '<button class="step" id="hmPlan" style="width:100%;text-align:left"><span class="step-i">'+careIco.plan+'</span>'+
     '<span class="step-b"><span class="step-t">Planning tools</span><span class="step-s">Catchments, beds per person, '+
     'surges, critical roads, new Malasakit Centers</span></span></button></div>';
  $("sheetBody").innerHTML=h;
  wireHospitalPanel();
}
function wireHospitalPanel(){
  const g=id=>document.getElementById(id), root=$("sheetBody");
  if (g("hmExit")) g("hmExit").addEventListener("click",exitHospitalMode);
  if (g("hmBeds")) g("hmBeds").addEventListener("click",function(){ setTab("beds"); showBedDashboard(); });
  if (g("hmPlan")) g("hmPlan").addEventListener("click",function(){ setTab("plan"); showPlanning(); });
  root.querySelectorAll("[data-hmmode]").forEach(function(b){
    b.addEventListener("click",function(){ hmMode=b.dataset.hmmode; renderHospitalPanel(); });
  });
  root.querySelectorAll("[data-mob]").forEach(function(b){
    b.addEventListener("click",function(){ hmMob=b.dataset.mob; renderHospitalPanel(); });
  });
  root.querySelectorAll("[data-acuity]").forEach(function(b){
    b.addEventListener("click",function(){ hmAcuity=+b.dataset.acuity; renderHospitalPanel(); });
  });
  root.querySelectorAll("[data-pay]").forEach(function(b){
    b.addEventListener("click",function(){ hmPay=+b.dataset.pay; renderHospitalPanel(); });
  });
  root.querySelectorAll("[data-need]").forEach(function(b){
    b.addEventListener("click",function(){
      const c=b.dataset.need;
      if (!c) hmNeeds=[];
      else if (hmNeeds.indexOf(c)>=0) hmNeeds=hmNeeds.filter(x=>x!==c);
      else hmNeeds=hmNeeds.concat([c]);
      renderHospitalPanel();
    });
  });
  if (g("hmOrig")) g("hmOrig").addEventListener("click",pickHospitalOrigin);
  if (g("hmGo")) g("hmGo").addEventListener("click",runHospitalSearch);
}
function freeBedsText(b,id){
  if (b.st==="AVAILABLE") return '<b>'+b.free+' free</b> of '+b.cap+' · reported '+ageText(b.ageH);
  if (b.st==="FULL") return '<b>'+(b.div?'Emergency room diverting':'None free')+'</b> · reported '+ageText(b.ageH);
  if (b.st==="STALE") return '<b>Not reported</b> · the last report was '+ageText(b.ageH)+', past the '+AGE_MAX_H+
                             ' hour limit, so it has lapsed';
  return '<b>Not reported</b> · '+authBeds(id)+' licensed beds; how many are free now is not known';
}
function servicesHtml(id){
  const s=servicesOf(id);
  if (!s.length) return HOSP[id].svcU?'Not on record':'None of the eight in Table 8 (infirmary)';
  return s.map(c=>'<span class="cr-svc'+(hmNeeds.indexOf(c)>=0?' on':'')+'">'+esc(needName(c))+'</span>').join(" ");
}
function profileLine(){
  const a=ACUITY.find(x=>x.k===hmAcuity);
  return 'Status '+hmAcuity+(a.ke?' (emergency)':'')+
         (hmNeeds.length?' · needs '+hmNeeds.map(needName).join(", ").toLowerCase():'')+
         ' · '+(a.ke?'cost filter lifted':PAYCLASS[hmPay].t.toLowerCase())+
         ' · '+(hmMode==="amb"?'ambulance':'commute, '+MOBILITY[hmMob].t.toLowerCase());
}
function runHospitalSearch(){
  if (!hmOrigin){ toast("Choose where the patient is first."); return; }
  careClear();
  const o=hmOrigin.id?hmOrigin.id:nearestNode(hmOrigin.ll).id;
  const a=ACUITY.find(x=>x.k===hmAcuity), rho=a.ke?3:hmPay, lv=trafficLevel;
  const res=nearestSuitable(o,hmAcuity,rho,hmMode,lv,hmNeeds,hmMob);
  hmLast={res:res,o:o,rho:rho};
  const box=$("hmResult");
  if (!res.best){
    const now=Date.now();
    const lack=hmNeeds.filter(function(c){
      return !Object.keys(HOSP).some(id=>P[id]&&servicesOf(id).indexOf(c)>=0&&suitable(id,hmAcuity,rho,now,[]));
    });
    let extra="";
    if (lack.length) extra+='<br><br>No hospital that fits the other choices offers '+
      esc(lack.map(needName).join(", ").toLowerCase())+'.';
    if (!a.ke&&rho===0) extra+='<br><br>Only one facility is confirmed as cost class 0, the Bicol Regional '+
      'Hospital and Medical Center, because Republic Act No. 11463 requires a Malasakit Center in every DOH '+
      'hospital. Choosing "Public hospitals" searches every government hospital.';
    box.innerHTML='<div class="warn" style="margin-top:12px"><b>No suitable hospital can be reached.</b><br>'+
      res.all.filter(x=>!x.ok).length+' of '+res.all.length+' hospitals were ruled out by the patient’s needs '+
      'and the other choices, and the rest cannot be reached from here this way. Call 911.'+extra+'</div>'+
      '<button class="btn btn-s" id="hmAlt" style="margin-top:8px">Every hospital, and why</button>';
    const g=document.getElementById("hmAlt");
    if (g) g.addEventListener("click",function(){ showHospitalAlternatives(res,o); });
    return;
  }
  const b=res.best, H=HOSP[b.id], p=P[b.id];
  const stab=stabilisation(o,hmAcuity,b,hmMode,lv,hmMob);
  let h='<div class="cr-prof">'+esc(profileLine())+'</div>';
  if (stab){
    h+='<div class="hm-stab"><h3>Stabilize first</h3>'+
       '<p style="font-size:13px;margin:0 0 6px">'+esc(P[stab.id].name)+' has an open emergency room and is '+
       fmtMin(b.t.min-stab.t.min)+' nearer. For a patient who needs a life-saving intervention now, go '+
       'there first, then transfer.</p><div style="font-size:12.5px;color:var(--gray)">'+esc(fmtHospMin(stab.t))+
       ' away · '+esc(SVC_NAME[HOSP[stab.id].svc])+'</div></div>';
  }
  h+='<div class="hm-card"><div class="cr-rank">First choice</div><h3>'+esc(p.name)+'</h3>'+
     '<div class="hm-eta">'+esc(b.t.here?"You are here":fmtHospMin(b.t))+'</div>'+
     '<div style="font-size:12.5px;color:var(--gray)">'+(b.t.km>0.05?fmtKm(b.t.km)+' · ':'')+
     (hmMode==="amb"?"by ambulance on the road network":b.t.kind==="walk"?"on foot":"by public transport and on foot")+
     '</div>';
  if (b.t.lb) h+='<div class="hm-bad" style="margin:9px 0 0">'+esc(hospApproachNote(b.id))+'</div>';
  h+='<dl class="hm-kv">'+
     '<dt>Level</dt><dd>'+esc(svcLabel(b.id))+'</dd>'+
     '<dt>Services</dt><dd>'+servicesHtml(b.id)+'</dd>'+
     '<dt>Emergency room</dt><dd>'+(H.er?"Yes":"No")+'</dd>'+
     '<dt>Cost class</dt><dd>'+H.q+' · '+esc(PAYCLASS[H.q].t)+
       (H.qLaw?'<br><span class="cr-fine">A DOH hospital, so it hosts a Malasakit Center by Republic Act No. 11463.</span>':
        H.qU?'<br><span class="cr-fine">Ownership is '+esc(H.own)+'; the Malasakit and PhilHealth flags are not in the '+
        'registry export, so this is the class ownership alone implies.</span>':'')+'</dd>'+
     '<dt>Free beds</dt><dd>'+freeBedsText(b.bed,b.id)+'</dd></dl>';
  h+='<div style="margin-top:11px;display:flex;gap:8px;flex-wrap:wrap">'+
     '<button class="btn btn-p" id="hmNav">Start guidance</button>'+
     '<button class="btn btn-s" id="hmAlt">Every hospital, and why</button></div></div>';

  /* Definition 18, backups */
  const backs=res.ranked.slice(1,3);
  h+='<div class="hm-h">If the first hospital turns the patient away</div>';
  if (!backs.length){
    h+='<div class="hm-bad"><b>No backup.</b> No second hospital fits this patient within reach. If '+
       esc(p.name)+' cannot admit, call 911 for a referral.</div>';
  } else {
    backs.forEach(function(x,i){
      const extra=x.t.min-b.t.min;
      h+='<button class="step cr-back" data-back="'+i+'" style="width:100%;text-align:left">'+
         '<span class="step-i cr-num">'+(i+2)+'</span><span class="step-b"><span class="step-t">'+esc(P[x.id].name)+
         '</span><span class="step-s">'+esc(fmtHospMin(x.t))+' · '+(extra>=0.5?'+'+fmtMin(extra)+' more · ':'')+
         esc(svcLabel(x.id))+' · '+esc(bedWord(x.bed))+'</span></span><span class="step-f">Route</span></button>';
    });
  }

  /* Definition 20, the gaps */
  const gp=paymentGap(o,hmAcuity,rho,hmMode,lv,hmNeeds,hmMob);
  if (isFinite(gp.gap)&&gp.gap>0.5){
    h+='<div class="hm-bad"><b>Payment gap '+fmtMin(gp.gap)+'.</b> With no cost limit the nearest suitable '+
       'hospital would be '+esc(P[gp.any.id].name)+', '+fmtMin(gp.any.t.min)+' away. The extra '+fmtMin(gp.gap)+
       ' is what the family’s budget costs in travel time.</div>';
  }
  const gn=needGap(o,hmAcuity,rho,hmMode,lv,hmNeeds,hmMob);
  if (gn&&isFinite(gn.gap)&&gn.gap>0.5){
    h+='<div class="hm-bad"><b>Need gap '+fmtMin(gn.gap)+'.</b> Without the need for '+
       esc(hmNeeds.map(needName).join(", ").toLowerCase())+', '+esc(P[gn.base.id].name)+' would do, '+
       fmtMin(gn.base.t.min)+' away. Only hospitals that offer the service count.</div>';
  }
  if (hmMode==="pt"){
    const gm=mobilityGap(o,hmAcuity,rho,lv,hmNeeds);
    if (isFinite(gm.gap)&&gm.gap>0.5){
      h+='<div class="hm-bad"><b>Mobility gap '+fmtMin(gm.gap)+'.</b> '+(hmMob==="slow"
        ? 'Walking slowly makes this trip '+fmtMin(gm.gap)+' longer than for someone who walks normally.'
        : 'A patient who walks slowly would need '+fmtMin(gm.gap)+' more for the same trip. Choose "Walks slowly" '+
          'for an older person, late pregnancy, or a disability.')+'</div>';
    } else if (!isFinite(gm.gap)){
      h+='<div class="hm-bad"><b>A slow walker cannot make this trip.</b> With the shorter walking limit no '+
         'suitable hospital can be reached by public transport from here. Arrange a vehicle or call 911.</div>';
    }
  }
  h+='<a class="hm-911" href="tel:911">Call 911</a>';
  box.innerHTML=h;
  drawHospitalRoute(b);
  const g=id=>document.getElementById(id);
  if (g("hmNav")) g("hmNav").addEventListener("click",function(){ startHospitalNav(b); });
  if (g("hmAlt")) g("hmAlt").addEventListener("click",function(){ showHospitalAlternatives(res,o); });
  box.querySelectorAll("[data-back]").forEach(function(btn){
    btn.addEventListener("click",function(){ drawHospitalRoute(backs[+btn.dataset.back]); });
  });
}
function hospCoords(b){
  if (!b||!b.t) return null;
  if (b.t.coords) return b.t.coords;
  if (!b.t.route) return null;
  return b.t.kind==="road"?b.t.route.coords:routeCoords(b.t.route);
}
function drawHospitalRoute(b){
  clearRoute();
  const c=hospCoords(b);
  if (!c||c.length<2){ if (P[b.id]) map.setView(P[b.id].ll,15); return; }
  routeLayers.push(L.polyline(c,{renderer:canvasR,color:MS.casing,weight:11,opacity:.85}).addTo(map));
  routeLayers.push(L.polyline(c,{renderer:canvasR,color:"#C5221F",weight:6,opacity:.95}).addTo(map));
  map.fitBounds(L.latLngBounds(c),{padding:[56,56]});
}
function startHospitalNav(b){
  const c=hospCoords(b);
  if (!c||c.length<2){ toast("The patient is already at "+P[b.id].name+"."); return; }
  const steps=b.t.kind==="road"
    ? makeSteps(b.t.route,{classId:"ambulance"},P[b.id].name)
    : b.t.kind==="walk" ? [{ico:"walk",t:"Walk to "+P[b.id].name,km:b.t.km,min:b.t.min}]
    : b.t.route.legs.map(l=>l.kind==="walk"
        ?{ico:"walk",t:"Walk to "+P[l.b].name,km:l.km,min:l.min}
        :{ico:"ride",t:"Ride the "+l.svc.short+", get off at "+boardName(l.svc,l.b),km:l.km,min:l.min});
  startNav(c,steps,b.t.min,{kind:"road",coords:c,min:b.t.min});
}
function showHospitalAlternatives(res,o){
  const now=Date.now(), a=ACUITY.find(x=>x.k===hmAcuity), rho=a.ke?3:hmPay;
  let h='<div style="padding:8px 0 6px"><div style="font-size:18px;font-weight:500">Every hospital, and why</div>'+
    '<div style="font-size:12.5px;color:var(--gray)">'+esc(profileLine())+'</div></div>';
  res.all.slice().sort(function(x,y){
    const ox=x.ok&&x.t, oy=y.ok&&y.t;
    if (ox!==oy) return ox?-1:1;
    return (x.t?x.t.min:1e9)-(y.t?y.t.min:1e9);
  }).forEach(function(x){
    const H=HOSP[x.id], why=whyNot(x.id,hmAcuity,rho,now,hmNeeds);
    if (!x.t) why.push("not reachable this way");
    const ok=x.ok&&x.t;
    h+='<div class="step"><span class="step-i" style="color:'+(ok?"var(--green-text)":"var(--gray-2)")+'">'+
      (ok?"✓":"·")+'</span><span class="step-b"><span class="step-t">'+esc(P[x.id].name)+'</span>'+
      '<span class="step-s">'+esc(svcLabel(x.id))+' · cost class '+H.q+' · '+authBeds(x.id)+' beds'+
      (x.t?' · '+esc(x.t.here?"here":fmtHospMin(x.t)):'')+' · '+esc(bedWord(x.bed))+'</span>'+
      (why.length?'<span class="step-s" style="color:var(--red-text)">Ruled out: '+esc(why.join("; "))+'</span>':'')+
      '</span></div>';
  });
  h+='<div class="foot"><span>Services follow the hospital levels of the DOH (2012) classification; no register '+
     'entry changes any facility’s list yet. Licensed beds are not free beds, so the search never assumes a '+
     'bed is free.</span><button class="link" id="hmBack">Back</button></div>';
  $("sheetBody").innerHTML=h;
  const g=document.getElementById("hmBack");
  if (g) g.addEventListener("click",function(){ renderHospitalPanel(); runHospitalSearch(); });
}

/* =====================================================================
   PLANNING TOOLS · for the Provincial Health Office, the PDRRMO and LGUs
   ===================================================================== */
let careLayer=null;
function careClear(){ if (careLayer&&map){ map.removeLayer(careLayer); } careLayer=null; }
function careLayerNew(){ careClear(); careLayer=L.layerGroup().addTo(map); return careLayer; }
const CARE_COLORS=["#1A73E8","#D93025","#188038","#E37400","#9334E6","#0E8081","#B31412","#5E35B1",
                   "#00796B","#C2185B","#6D4C41","#3949AB","#7CB342","#F4511E","#00897B","#8E24AA"];
/* The anchors of Definition 1 that carry a population: the 18 town centres. */
const careAnchors=()=>LGU_IDS.filter(id=>P[id]&&P[id].pop);
const PLAN={kappa:2,rho:3,need:"",theta:60,kind:"lic",pay:3,mob:"std",k:2,siteTheta:60};
function planNeeds(){ return PLAN.need?[PLAN.need]:[]; }
function planRho(){ const a=ACUITY.find(x=>x.k===PLAN.kappa); return a&&a.ke?3:PLAN.rho; }

/* A small binary heap with a comparator, for lexicographic labels. */
function CHeap(cmp){ this.a=[]; this.cmp=cmp; }
CHeap.prototype.size=function(){ return this.a.length; };
CHeap.prototype.push=function(x){
  const a=this.a; a.push(x); let i=a.length-1;
  while (i>0){ const p=(i-1)>>1; if (this.cmp(a[i],a[p])>=0) break; const t=a[i]; a[i]=a[p]; a[p]=t; i=p; }
};
CHeap.prototype.pop=function(){
  const a=this.a, top=a[0], last=a.pop();
  if (a.length){ a[0]=last; let i=0;
    for(;;){ const l=2*i+1, r=l+1; let s=i;
      if (l<a.length&&this.cmp(a[l],a[s])<0) s=l;
      if (r<a.length&&this.cmp(a[r],a[s])<0) s=r;
      if (s===i) break; const t=a[s]; a[s]=a[i]; a[i]=t; i=s; } }
  return top;
};
/* Proposition 14. One multi-source search from every suitable hospital over
   the ambulance roads labels every place with its nearest suitable hospital,
   ties going to more free beds and then the smaller identifier. The parent
   links form the shortest-path forest that Proposition 17 uses. */
function catchmentMap(prof,exclude){
  const now=Date.now();
  const adj=buildAdj({classId:"ambulance",pref:"fast",level:trafficLevel,exclude:exclude||null});
  const seeds=Object.keys(HOSP).filter(id=>P[id]&&suitable(id,prof.kappa,prof.rho,now,prof.needs));
  const lab={}, par={};
  const hp=new CHeap(function(x,y){ return x.d-y.d || x.b-y.b || (x.h<y.h?-1:x.h>y.h?1:0); });
  seeds.forEach(function(id){
    const b=bedStatus(id,now);
    hp.push({d:0,b:-(b.st==="AVAILABLE"?b.free:0),h:id,n:id,p:null,r:null});
  });
  while (hp.size()){
    const x=hp.pop();
    if (lab[x.n]) continue;
    lab[x.n]={d:x.d,h:x.h}; par[x.n]=x.p?{n:x.p,r:x.r}:null;
    (adj[x.n]||[]).forEach(function(e){
      if (!lab[e.to]) hp.push({d:x.d+e.cost,b:x.b,h:x.h,n:e.to,p:x.n,r:e.r});
    });
  }
  const forest=new Set();
  Object.keys(par).forEach(function(n){ if (par[n]) forest.add(par[n].r); });
  return {lab:lab,par:par,forest:forest,seeds:seeds};
}
/* Single-source ambulance times to every place, for the surge assignment. */
function ambTimesFrom(o){
  const adj=buildAdj({classId:"ambulance",pref:"fast",level:trafficLevel}), dist={}, done={};
  const h=new Heap(); dist[o]=0; h.push(0,o);
  while (h.size()){
    const u=h.pop()[1]; if (done[u]) continue; done[u]=1;
    (adj[u]||[]).forEach(function(e){
      const nd=dist[u]+e.cost;
      if (nd<(dist[e.to]===undefined?Infinity:dist[e.to])){ dist[e.to]=nd; h.push(nd,e.to); }
    });
  }
  return dist;
}
/* Travel time by public transport from every town centre to every hospital. */
const ptMatCache={};
function ptMatrix(mob){
  const key=trafficLevel+"|"+(mob||"std")+"|"+careSig();
  if (ptMatCache[key]) return ptMatCache[key];
  const M={};
  careAnchors().forEach(function(a){
    const T=careTimes(a,"pt",trafficLevel,mob||"std"); M[a]={};
    Object.keys(T).forEach(function(id){ M[a][id]=T[id]?T[id].min:Infinity; });
  });
  ptMatCache[key]=M;
  return M;
}
function sel(id,opts,val,label){
  return '<label class="cr-sel"><span>'+esc(label)+'</span><select id="'+id+'">'+opts.map(function(o){
    return '<option value="'+esc(o[0])+'"'+(String(o[0])===String(val)?' selected':'')+'>'+esc(o[1])+'</option>';
  }).join("")+'</select></label>';
}
const acuityOpts=()=>ACUITY.map(x=>[x.k,x.k+". "+x.t]);
const payOpts=()=>PAYCLASS.map(x=>[x.r,x.t]);
const needOpts=()=>[["","No particular need"]].concat(NEEDS.map(n=>[n.c,n.t]));
function profileControls(){
  const a=ACUITY.find(x=>x.k===PLAN.kappa);
  return '<div class="cr-ctl">'+sel("plK",acuityOpts(),PLAN.kappa,"Patient status")+
    sel("plN",needOpts(),PLAN.need,"Needs")+
    (a.ke?'<div class="cr-fine" style="align-self:end">Cost filter lifted (RA 10932)</div>'
         :sel("plR",payOpts(),PLAN.rho,"Can pay"))+'</div>';
}
function wireProfile(rerun){
  const k=document.getElementById("plK"), n=document.getElementById("plN"), r=document.getElementById("plR");
  if (k) k.addEventListener("change",function(){ PLAN.kappa=+k.value; rerun(); });
  if (n) n.addEventListener("change",function(){ PLAN.need=n.value; rerun(); });
  if (r) r.addEventListener("change",function(){ PLAN.rho=+r.value; rerun(); });
}
function toolHead(title,sub){
  return '<div class="cr-thead"><button class="ico" id="plBack" aria-label="Back to planning tools">'+
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" '+
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M15 5l-7 7 7 7"/></svg>'+
    '</button><div><div class="cr-title" style="font-size:18px">'+esc(title)+'</div><div class="cr-sub">'+esc(sub)+
    '</div></div></div>';
}
function wireBack(){
  const b=document.getElementById("plBack");
  if (b) b.addEventListener("click",showPlanning);
}
function busy(msg,fn){
  $("sheetBody").innerHTML='<div class="cr-busy">'+esc(msg)+'</div>';
  setTimeout(fn,30);
}
function modelNote(extra){
  return '<div class="cr-model"><b>Model output.</b> Computed from the MAP-A road and transit network and the DOH '+
    'registry; it is not a measurement of Albay. '+(extra||'')+'</div>';
}
function showPlanning(){
  if (!hmOn){ hmOn=true; applyHospitalFilter(); $("dir").style.display="none"; $("top").style.display="none"; }
  setTab("plan");
  const items=[
    ["catch","Catchment map","Which hospital each place would be sent to, for one kind of patient"],
    ["beds","Beds per person","Beds within reach per 10,000 people, town by town, and bed deserts"],
    ["surge","Surge assignment","Many patients, few beds: place everyone without overfilling a hospital"],
    ["roads","Critical roads","Roads whose closure would delay patients most, for typhoon and lahar planning"],
    ["sites","New Malasakit Centers","Where free or assisted care would reach the most people"],
    ["dash","Bed dashboard","Free beds and report age by municipality; enter a report"]
  ];
  let h='<div class="cr-head"><div class="cr-badge">'+careIco.plan+'</div><div style="flex:1">'+
    '<div class="cr-title">Planning tools</div><div class="cr-sub">For the Provincial Health Office, the PDRRMO '+
    'and LGUs</div></div></div>';
  items.forEach(function(it){
    h+='<button class="step" data-tool="'+it[0]+'" style="width:100%;text-align:left"><span class="step-b">'+
       '<span class="step-t">'+esc(it[1])+'</span><span class="step-s">'+esc(it[2])+'</span></span>'+
       '<span class="step-f">›</span></button>';
  });
  h+=(careLayer?'<button class="mini-btn" id="plClear">Clear the planning layer from the map</button>':'')+
     modelNote('Where a tool needs free beds and no hospital has reported, it says so rather than assume any.');
  $("sheetBody").innerHTML=h; openSheet("full");
  $("sheetBody").querySelectorAll("[data-tool]").forEach(function(b){
    b.addEventListener("click",function(){
      const t=b.dataset.tool;
      if (t==="catch") showCatchments();
      if (t==="beds") showBedsPerPerson();
      if (t==="surge") showSurge();
      if (t==="roads") showCriticalRoads();
      if (t==="sites") showSites();
      if (t==="dash"){ setTab("beds"); showBedDashboard(); }
    });
  });
  const c=document.getElementById("plClear");
  if (c) c.addEventListener("click",function(){ careClear(); showPlanning(); });
}

/* ---- Definition 22 · catchment map ---- */
function showCatchments(){
  busy("Drawing catchments…",function(){
    const prof={kappa:PLAN.kappa,rho:planRho(),needs:planNeeds()};
    const cm=catchmentMap(prof);
    const col={}; cm.seeds.slice().sort().forEach(function(id,i){ col[id]=CARE_COLORS[i%CARE_COLORS.length]; });
    const lay=careLayerNew();
    clearRoute();
    ROADS.forEach(function(r){
      const A=cm.lab[r.a], B=cm.lab[r.b];
      const g=edgeCoords(r,r.a); if (!g||g.length<2) return;
      const same=A&&B&&A.h===B.h;
      L.polyline(g,{renderer:canvasR,color:same?col[A.h]:"#9AA0A6",weight:same?5:3,opacity:same?.85:.6,
        dashArray:same?null:"4 5"}).addTo(lay);
    });
    Object.keys(P).forEach(function(id){
      const x=cm.lab[id]; if (!P[id].ll) return;
      if (HOSP[id]&&cm.seeds.indexOf(id)>=0){
        L.circleMarker(P[id].ll,{renderer:canvasR,radius:9,color:"#fff",weight:2.5,fillColor:col[id],fillOpacity:1})
          .bindTooltip(P[id].name).addTo(lay);
        return;
      }
      L.circleMarker(P[id].ll,{renderer:canvasR,radius:x?4:3.5,color:x?col[x.h]:"#9AA0A6",weight:1.5,
        fillColor:x?col[x.h]:"#fff",fillOpacity:x?.9:1})
        .bindTooltip(P[id].name+(x?" → "+P[x.h].name+", "+fmtMin(x.d):" → no suitable hospital by road"))
        .addTo(lay);
    });
    const rows=cm.seeds.map(function(id){
      const mine=Object.keys(cm.lab).filter(n=>cm.lab[n].h===id);
      const towns=careAnchors().filter(a=>cm.lab[a]&&cm.lab[a].h===id);
      return {id:id,n:mine.length,towns:towns,pop:towns.reduce((s,a)=>s+P[a].pop,0),
              far:mine.reduce((m,n)=>Math.max(m,cm.lab[n].d),0)};
    }).filter(r=>r.n>0).sort((a,b)=>b.pop-a.pop||b.n-a.n);
    const none=Object.keys(P).filter(n=>!cm.lab[n]);
    let h=toolHead("Catchment map","Definition 22 · by ambulance on the road network")+profileControls();
    if (!cm.seeds.length){
      h+='<div class="warn">No hospital fits this kind of patient, so there are no catchments.</div>';
    } else {
      h+='<div class="note">Every place is coloured by the hospital an ambulance would take this patient to. '+
         rows.length+' hospital'+(rows.length===1?'':'s')+' share the province'+
         (none.length?'; '+none.length+' place'+(none.length===1?' has':'s have')+' no suitable hospital by road':'')+
         '. Grey dashed roads lie on a catchment border.</div>';
      h+='<table class="bd-tbl"><thead><tr><th scope="col">Hospital</th><th scope="col">Town centres</th>'+
         '<th scope="col">People</th><th scope="col">Farthest</th></tr></thead><tbody>';
      rows.forEach(function(r){
        h+='<tr><td><span class="cr-sw" style="background:'+col[r.id]+'"></span>'+esc(P[r.id].name)+'</td>'+
           '<td>'+(r.towns.length?esc(r.towns.map(a=>P[a].name).join(", ")):'<span style="color:var(--gray-2)">none</span>')+
           '</td><td>'+(r.pop?r.pop.toLocaleString("en-PH"):"0")+'</td><td>'+fmtMin(r.far)+'</td></tr>';
      });
      h+='</tbody></table>';
    }
    h+=modelNote('People are the 2020 census counts of the town centres that fall in each catchment; the rest of '+
       'each municipality is not split out. A hospital with an unreported bed status stays in, as in the patient '+
       'search.');
    $("sheetBody").innerHTML=h; openSheet("half");
    wireBack(); wireProfile(showCatchments);
    if (cm.seeds.length) map.fitBounds([[12.99,123.40],[13.50,124.18]],{paddingTopLeft:[22,22],paddingBottomRight:[72,30]});
  });
}

/* ---- Definitions 21 and 23 · beds per person and bed deserts ---- */
function bedsPerPerson(theta,kind,pay,mob){
  const M=ptMatrix(mob), anchors=careAnchors(), now=Date.now();
  const hosp=Object.keys(HOSP).filter(id=>P[id]&&HOSP[id].q<=pay&&HOSP[id].svc>=1&&!HOSP[id].svcU);
  const supply={};
  hosp.forEach(function(id){
    const b=bedStatus(id,now);
    supply[id]=kind==="free"?(b.st==="AVAILABLE"?b.free:0):(authBeds(id)||0);
  });
  const R={};
  hosp.forEach(function(id){
    const pop=anchors.filter(a=>M[a][id]<=theta).reduce((s,a)=>s+P[a].pop,0);
    R[id]=pop>0?supply[id]/pop:0;
  });
  const rows=anchors.map(function(a){
    const reach=hosp.filter(id=>M[a][id]<=theta);
    const cum=reach.reduce((s,id)=>s+supply[id],0);
    const af=reach.reduce((s,id)=>s+R[id],0);
    const nearest=hosp.filter(id=>supply[id]>0).reduce((m,id)=>Math.min(m,M[a][id]),Infinity);
    return {a:a,pop:P[a].pop,cum:cum,af:af*1e4,nearest:nearest,desert:!reach.some(id=>supply[id]>0)};
  });
  const inReach=hosp.filter(id=>anchors.some(a=>M[a][id]<=theta)).reduce((s,id)=>s+supply[id],0);
  const counted=rows.reduce((s,r)=>s+r.pop*r.af/1e4,0);
  return {rows:rows,hosp:hosp,supply:supply,inReach:inReach,counted:counted,
          giniCum:weightedGini(rows.map(r=>({v:r.cum,w:r.pop}))),
          giniAF:weightedGini(rows.map(r=>({v:r.af,w:r.pop}))),
          desertPop:rows.filter(r=>r.desert).reduce((s,r)=>s+r.pop,0),
          pop:rows.reduce((s,r)=>s+r.pop,0),
          reported:Object.keys(HOSP).filter(id=>bedReported(bedStatus(id,now))).length};
}
function showBedsPerPerson(){
  busy("Timing every town to every hospital by public transport…",function(){
    const res=bedsPerPerson(PLAN.theta,PLAN.kind,PLAN.pay,PLAN.mob);
    const lay=careLayerNew(); clearRoute();
    const maxAF=Math.max(1,...res.rows.map(r=>r.af));
    res.rows.forEach(function(r){
      const ll=P[r.a].ll, rad=6+16*Math.sqrt(r.af/maxAF);
      L.circleMarker(ll,{renderer:canvasR,radius:rad,color:r.desert?"#B3261E":"#fff",weight:r.desert?3:2,
        fillColor:r.desert?"#FCE8E6":"#1A73E8",fillOpacity:r.desert?.9:.75})
        .bindTooltip(P[r.a].name+": "+r.af.toFixed(1)+" beds per 10,000"+(r.desert?" · bed desert":""))
        .addTo(lay);
    });
    let h=toolHead("Beds per person","Definitions 21 and 23 · town centres, by public transport")+
      '<div class="cr-ctl">'+
      sel("bpT",[[30,"30 min"],[45,"45 min"],[60,"60 min"],[90,"90 min"]],PLAN.theta,"Within")+
      sel("bpK",[["lic","Licensed beds"],["free","Reported free beds"]],PLAN.kind,"Count")+
      sel("bpP",[[3,"Any hospital"],[1,"Public hospitals"],[0,"Free or assisted care"]],PLAN.pay,"Hospitals")+
      sel("bpM",[["std","Walks normally"],["slow","Walks slowly"]],PLAN.mob,"Walking")+'</div>';
    if (PLAN.kind==="free"&&!res.reported){
      h+='<div class="warn"><b>No hospital has reported free beds.</b> Every town is shown with none, which is a '+
         'statement about the reports, not about the wards. Enter reports in the bed dashboard, or count '+
         'licensed beds.</div>';
    }
    h+='<div class="hm-kv" style="font-size:13.5px">'+
       '<dt>Inequality (Gini)</dt><dd>'+res.giniAF.toFixed(3)+' per person · '+res.giniCum.toFixed(3)+
         ' counting reachable beds</dd>'+
       '<dt>Bed deserts</dt><dd>'+res.rows.filter(r=>r.desert).length+' town'+
         (res.rows.filter(r=>r.desert).length===1?'':'s')+' · '+res.desertPop.toLocaleString("en-PH")+' people ('+
         (res.pop?(res.desertPop/res.pop*100).toFixed(1):'0')+'%)</dd>'+
       '<dt>Beds counted once</dt><dd>'+Math.round(res.counted)+' of the '+res.inReach+
         ' beds in reach (Proposition 15)</dd></div>';
    h+='<table class="bd-tbl"><thead><tr><th scope="col">Town</th><th scope="col">People</th>'+
       '<th scope="col">Beds in reach</th><th scope="col">Per 10,000</th><th scope="col">Nearest</th></tr></thead><tbody>';
    res.rows.slice().sort((a,b)=>a.af-b.af).forEach(function(r){
      h+='<tr'+(r.desert?' class="cr-desert"':'')+'><td>'+esc(P[r.a].name)+(r.desert?' <span class="bd-st is-full">desert</span>':'')+
         '</td><td>'+r.pop.toLocaleString("en-PH")+'</td><td>'+r.cum+'</td><td><b>'+r.af.toFixed(1)+'</b></td><td>'+
         (isFinite(r.nearest)?fmtMin(r.nearest):'none')+'</td></tr>';
    });
    h+='</tbody></table>';
    h+=modelNote('Beds per person follow the two-step floating catchment method (Luo & Wang, 2003): each hospital’s '+
       'beds are shared among the people who can reach it in time, so a crowded hospital counts for less. Only '+
       'hospitals of Level 1 or above count; infirmaries are left out. People are the town populations of the '+
       '2020 census, placed at the town centre.');
    $("sheetBody").innerHTML=h; openSheet("half"); wireBack();
    const w=(id,f)=>{ const e=document.getElementById(id); if (e) e.addEventListener("change",function(){ f(e.value); showBedsPerPerson(); }); };
    w("bpT",v=>{PLAN.theta=+v;}); w("bpK",v=>{PLAN.kind=v;}); w("bpP",v=>{PLAN.pay=+v;}); w("bpM",v=>{PLAN.mob=v;});
  });
}

/* ---- Definition 24 · surge assignment ---- */
const SURGE={groups:[{o:"legazpi",n:6,k:2,r:3,need:""},{o:"daraga",n:5,k:2,r:3,need:""},
                     {o:"tabaco",n:4,k:3,r:1,need:""}],drill:2,last:null};
/* Kuhn's (1955) Hungarian method for an n x m cost matrix, n <= m. */
function hungarian(C){
  const n=C.length, m=C[0].length, INF=1e300;
  const u=new Float64Array(n+1), v=new Float64Array(m+1), p=new Int32Array(m+1), way=new Int32Array(m+1);
  for (let i=1;i<=n;i++){
    p[0]=i; let j0=0;
    const minv=new Float64Array(m+1).fill(INF), used=new Uint8Array(m+1);
    do{
      used[j0]=1; const i0=p[j0]; let delta=INF, j1=0;
      for (let j=1;j<=m;j++) if (!used[j]){
        const cur=C[i0-1][j-1]-u[i0]-v[j];
        if (cur<minv[j]){ minv[j]=cur; way[j]=j0; }
        if (minv[j]<delta){ delta=minv[j]; j1=j; }
      }
      for (let j=0;j<=m;j++){ if (used[j]){ u[p[j]]+=delta; v[j]-=delta; } else minv[j]-=delta; }
      j0=j1;
    } while (p[j0]!==0);
    do{ const j1=way[j0]; p[j0]=p[j1]; j0=j1; } while (j0);
  }
  const ans=new Array(n).fill(-1);
  for (let j=1;j<=m;j++) if (p[j]) ans[p[j]-1]=j-1;
  return ans;
}
function surgeSolve(){
  const now=Date.now(), hosp=Object.keys(HOSP).filter(id=>P[id]);
  const beds={}, drilled=[];
  hosp.forEach(function(id){
    const b=bedStatus(id,now);
    if (b.st==="AVAILABLE") beds[id]=b.free;
    else if (b.st==="FULL") beds[id]=0;
    else { beds[id]=SURGE.drill; if (SURGE.drill>0) drilled.push(id); }
  });
  const pts=[];
  SURGE.groups.forEach(function(g,gi){
    for (let i=0;i<g.n;i++) pts.push({g:gi,o:g.o,k:g.k,r:(ACUITY.find(x=>x.k===g.k).ke?3:g.r),
                                      needs:g.need?[g.need]:[],em:!!ACUITY.find(x=>x.k===g.k).ke});
  });
  const n=pts.length;
  if (!n) return null;
  const tCache={};
  const T=pts.map(function(p){
    const d=tCache[p.o]||(tCache[p.o]=ambTimesFrom(p.o));
    return hosp.map(function(id){
      const ok=suitable(id,p.k,p.r,now,p.needs,true);
      const t=d[id]; return ok&&t!==undefined?t:Infinity;
    });
  });
  let cmax=0; T.forEach(row=>row.forEach(t=>{ if (isFinite(t)) cmax=Math.max(cmax,t); }));
  const U0=(n+1)*(cmax+1), UE=(n+1)*(U0+cmax+1), BIG=(n+1)*(UE+1)*10;
  /* bed slots: a hospital needs no more slots than the patients it can take */
  const slots=[];
  hosp.forEach(function(id,j){
    const usable=T.filter(row=>isFinite(row[j])).length;
    for (let s=0;s<Math.min(beds[id],usable);s++) slots.push(j);
  });
  const C=pts.map(function(p,i){
    const row=slots.map(j=>isFinite(T[i][j])?T[i][j]:BIG);
    for (let q=0;q<n;q++) row.push(q===i?(p.em?UE:U0):BIG);
    return row;
  });
  const ans=hungarian(C);
  const opt=ans.map(c=>c<slots.length?slots[c]:-1);
  /* independent nearest-hospital advice, and a first-come rule */
  const indep=T.map(function(row){
    let b=-1; row.forEach((t,j)=>{ if (isFinite(t)&&beds[hosp[j]]>0&&(b<0||t<row[b])) b=j; }); return b;
  });
  const load={}; indep.forEach(j=>{ if (j>=0) load[j]=(load[j]||0)+1; });
  const turned=Object.keys(load).reduce((s,j)=>s+Math.max(0,load[j]-beds[hosp[j]]),0);
  const left={}; hosp.forEach((id,j)=>{ left[j]=beds[id]; });
  const order=pts.map((p,i)=>i).sort((a,b)=>(pts[b].em?1:0)-(pts[a].em?1:0)||a-b);
  const first=new Array(n).fill(-1);
  order.forEach(function(i){
    let b=-1; T[i].forEach((t,j)=>{ if (isFinite(t)&&left[j]>0&&(b<0||t<T[i][b])) b=j; });
    if (b>=0){ left[b]--; first[i]=b; }
  });
  const sum=a=>a.reduce((s,j,i)=>s+(j>=0?T[i][j]:0),0);
  return {pts:pts,hosp:hosp,beds:beds,T:T,opt:opt,indep:indep,first:first,turned:turned,drilled:drilled,
          placedOpt:opt.filter(j=>j>=0).length,placedFirst:first.filter(j=>j>=0).length,
          emOpt:opt.filter((j,i)=>j<0&&pts[i].em).length,emFirst:first.filter((j,i)=>j<0&&pts[i].em).length,
          minOpt:sum(opt),minFirst:sum(first),reachable:T.filter(r=>r.some(isFinite)).length};
}
function placeOpts(){
  return careAnchors().map(a=>[a,P[a].name]).concat(
    Object.keys(P).filter(id=>!HOSP[id]&&!LGU_IDS.includes(id)&&P[id].type!=="hospital"&&P[id].net)
      .sort((a,b)=>P[a].name.localeCompare(P[b].name)).map(id=>[id,P[id].name]));
}
function showSurge(){
  let h=toolHead("Surge assignment","Definition 24 · by ambulance · many patients, few beds");
  h+='<div class="note">Typhoon, eruption or road crash: list where the patients are. MAP-A Care places each one '+
     'so that no hospital gets more patients than free beds, emergencies first, with the least total travel '+
     'time (Proposition 16). The result is advice for a dispatcher, who confirms every placement.</div>';
  SURGE.groups.forEach(function(g,i){
    const a=ACUITY.find(x=>x.k===g.k);
    h+='<div class="cr-grp"><div class="cr-ctl">'+
       sel("sgO"+i,placeOpts(),g.o,"Where")+
       '<label class="cr-sel"><span>Patients</span><input type="number" id="sgN'+i+'" min="1" max="60" value="'+g.n+'"></label>'+
       sel("sgK"+i,acuityOpts(),g.k,"Status")+
       sel("sgD"+i,needOpts(),g.need,"Needs")+
       (a.ke?'':sel("sgR"+i,payOpts(),g.r,"Can pay"))+
       '</div><button class="link" data-sgdel="'+i+'">Remove this group</button></div>';
  });
  h+='<button class="mini-btn" id="sgAdd">Add a group of patients</button>';
  h+='<div class="cr-ctl" style="margin-top:10px">'+sel("sgDrill",[[0,"None (count reported beds only)"],[1,"1 each"],
     [2,"2 each"],[5,"5 each"],[10,"10 each"]],SURGE.drill,"Free beds at unreported hospitals, for this drill")+'</div>';
  h+='<button class="hm-go" id="sgGo">Assign the patients</button><div id="sgOut"></div>';
  $("sheetBody").innerHTML=h; openSheet("full"); wireBack();
  const g=id=>document.getElementById(id);
  SURGE.groups.forEach(function(gr,i){
    if (g("sgO"+i)) g("sgO"+i).addEventListener("change",e=>{ gr.o=e.target.value; });
    if (g("sgN"+i)) g("sgN"+i).addEventListener("change",e=>{ gr.n=Math.max(1,Math.min(60,Math.round(+e.target.value||1))); });
    if (g("sgK"+i)) g("sgK"+i).addEventListener("change",e=>{ gr.k=+e.target.value; showSurge(); });
    if (g("sgD"+i)) g("sgD"+i).addEventListener("change",e=>{ gr.need=e.target.value; });
    if (g("sgR"+i)) g("sgR"+i).addEventListener("change",e=>{ gr.r=+e.target.value; });
  });
  $("sheetBody").querySelectorAll("[data-sgdel]").forEach(function(b){
    b.addEventListener("click",function(){ SURGE.groups.splice(+b.dataset.sgdel,1); showSurge(); });
  });
  g("sgAdd").addEventListener("click",function(){ SURGE.groups.push({o:"legazpi",n:3,k:3,r:3,need:""}); showSurge(); });
  g("sgDrill").addEventListener("change",e=>{ SURGE.drill=+e.target.value; });
  g("sgGo").addEventListener("click",function(){
    g("sgOut").innerHTML='<div class="cr-busy">Solving…</div>';
    setTimeout(function(){ renderSurge(surgeSolve()); },30);
  });
  if (SURGE.last) renderSurge(SURGE.last,true);
}
function renderSurge(res,quiet){
  SURGE.last=res;
  const out=document.getElementById("sgOut"); if (!out) return;
  if (!res){ out.innerHTML='<div class="warn">Add at least one patient.</div>'; return; }
  const n=res.pts.length, totBeds=res.hosp.reduce((s,id)=>s+res.beds[id],0);
  let h='';
  if (res.drilled.length){
    h+='<div class="warn"><b>Drill assumption in use.</b> '+res.drilled.length+' hospitals have no fresh bed report, '+
       'so this exercise gives each '+SURGE.drill+' free bed'+(SURGE.drill===1?'':'s')+'. Real free beds come only '+
       'from reports.</div>';
  }
  if (!totBeds){
    h+='<div class="warn"><b>No free beds to assign.</b> No hospital has reported free beds and the drill '+
       'assumption is off.</div>';
  }
  h+='<div class="hm-kv" style="font-size:13.5px">'+
     '<dt>Placed</dt><dd><b>'+res.placedOpt+' of '+n+'</b> patients'+(res.emOpt?' · '+res.emOpt+' emergency patients could not be placed':'')+'</dd>'+
     '<dt>First come, first served</dt><dd>'+res.placedFirst+' placed'+(res.emFirst?', '+res.emFirst+' emergencies left out':'')+
       (res.placedFirst===res.placedOpt&&res.minFirst>res.minOpt+0.5?' · '+fmtMin(res.minFirst-res.minOpt)+' more travel in all':'')+'</dd>'+
     '<dt>Everyone to their own nearest</dt><dd>'+res.turned+' patient'+(res.turned===1?'':'s')+
       ' would reach a hospital whose beds are already taken</dd>'+
     '<dt>Free beds in the exercise</dt><dd>'+totBeds+'</dd></div>';
  /* per group */
  SURGE.groups.forEach(function(g,gi){
    const idx=res.pts.map((p,i)=>p.g===gi?i:-1).filter(i=>i>=0);
    if (!idx.length) return;
    const by={}; let un=0;
    idx.forEach(function(i){ const j=res.opt[i]; if (j<0) un++; else by[j]=(by[j]||0)+1; });
    h+='<div class="cr-grpres"><b>'+esc(P[g.o].name)+'</b> · '+idx.length+' patient'+(idx.length===1?'':'s')+
       ' · status '+g.k+(g.need?' · '+esc(needName(g.need).toLowerCase()):'')+'<ul>';
    Object.keys(by).sort((a,b)=>res.T[idx[0]][a]-res.T[idx[0]][b]).forEach(function(j){
      h+='<li>'+by[j]+' to '+esc(P[res.hosp[j]].name)+' · '+fmtMin(res.T[idx[0]][j])+'</li>';
    });
    if (un) h+='<li class="cr-un">'+un+' not placed: no suitable hospital with a free bed can be reached. Call 911 '+
              'for a referral outside the province.</li>';
    h+='</ul></div>';
  });
  out.innerHTML=h;
  /* map: one line per origin-hospital pair */
  const lay=careLayerNew(); clearRoute();
  const pairs={};
  res.pts.forEach(function(p,i){ const j=res.opt[i]; if (j<0) return; const k=p.o+"|"+res.hosp[j]; pairs[k]=(pairs[k]||0)+1; });
  const bounds=[];
  Object.keys(pairs).forEach(function(k,ci){
    const pr=k.split("|"), a=P[pr[0]].ll, b=P[pr[1]].ll;
    L.polyline([a,b],{renderer:canvasR,color:CARE_COLORS[ci%CARE_COLORS.length],weight:2+Math.min(10,pairs[k]*1.5),
      opacity:.8}).bindTooltip(pairs[k]+" from "+P[pr[0]].name+" to "+P[pr[1]].name).addTo(lay);
    bounds.push(a,b);
  });
  if (bounds.length&&!quiet) map.fitBounds(L.latLngBounds(bounds),{padding:[50,50]});
}

/* ---- Definition 25 and Proposition 17 · critical roads ---- */
function criticalRoads(prof){
  const base=catchmentMap(prof), anchors=careAnchors(), rows=[];
  base.forest.forEach(function(r){
    const alt=catchmentMap(prof,[r]);
    let D=0, cutPop=0, cutTowns=[], worst=null, changed=0;
    anchors.forEach(function(a){
      const t1=base.lab[a]?base.lab[a].d:Infinity, t2=alt.lab[a]?alt.lab[a].d:Infinity;
      if (!isFinite(t1)) return;
      if (!isFinite(t2)){ cutPop+=P[a].pop; cutTowns.push(a); return; }
      const dd=t2-t1;
      if (dd>1e-9){ D+=P[a].pop*dd; if (!worst||dd>worst.dd) worst={a:a,dd:dd}; }
    });
    Object.keys(base.lab).forEach(function(nd){
      const y=alt.lab[nd]; if (!y||y.d>base.lab[nd].d+1e-9||y.h!==base.lab[nd].h) changed++;
    });
    rows.push({r:r,D:D,cutPop:cutPop,cutTowns:cutTowns,worst:worst,changed:changed});
  });
  rows.sort((x,y)=>(y.cutPop-x.cutPop)||(y.D-x.D)||(y.changed-x.changed));
  const open=ROADS.filter(r=>roadAllows(r,classById("ambulance"))).length;
  return {rows:rows,tested:base.forest.size,open:open,seeds:base.seeds.length};
}
function showCriticalRoads(){
  busy("Closing each road on the shortest-path forest in turn…",function(){
    const prof={kappa:PLAN.kappa,rho:planRho(),needs:planNeeds()};
    const cr=criticalRoads(prof);
    const top=cr.rows.filter(x=>x.cutPop>0||x.D>0).slice(0,12);
    const lay=careLayerNew(); clearRoute();
    const maxD=Math.max(1,...top.map(x=>x.D));
    top.slice().reverse().forEach(function(x,i){
      const g=edgeCoords(x.r,x.r.a); if (!g||g.length<2) return;
      L.polyline(g,{renderer:canvasR,color:x.cutPop?"#7B1FA2":"#C5221F",
        weight:x.cutPop?11:4+7*Math.sqrt(x.D/maxD),opacity:.9})
        .bindTooltip((top.length-i)+". "+(x.r.name||"road")).addTo(lay);
    });
    let h=toolHead("Critical roads","Definition 25 · ambulance roads · Proposition 17")+profileControls();
    h+='<div class="note">Each road on the shortest-path forest was closed in turn, '+cr.tested+' of the '+cr.open+
       ' roads an ambulance can use; by Proposition 17 closing any other road delays nobody. A road ranks by the '+
       'people it would cut off, then by the extra person-minutes it adds for the town centres.</div>';
    if (!top.length){
      h+='<div class="hm-bad">No single closure delays a town centre for this kind of patient.</div>';
    } else {
      top.forEach(function(x,i){
        h+='<div class="step"><span class="step-i cr-num'+(x.cutPop?' cut':'')+'">'+(i+1)+'</span><span class="step-b">'+
           '<span class="step-t">'+esc(x.r.name||"Road")+'</span><span class="step-s">'+
           esc(P[x.r.a].name)+' – '+esc(P[x.r.b].name)+' · '+fmtKm(x.r.km)+'</span>'+
           (x.cutPop?'<span class="step-s" style="color:var(--red-text)">Cuts off '+esc(x.cutTowns.map(a=>P[a].name).join(", "))+
             ' ('+x.cutPop.toLocaleString("en-PH")+' people) from every suitable hospital</span>':'')+
           (x.D>0?'<span class="step-s">Adds '+Math.round(x.D).toLocaleString("en-PH")+' person-minutes'+
             (x.worst?'; '+esc(P[x.worst.a].name)+' waits '+fmtMin(x.worst.dd)+' longer':'')+'</span>':'')+
           '</span></div>';
      });
    }
    h+=modelNote('Only the town centres carry people here, so a road that delays outlying places but no town '+
       'centre ranks low. Clear the purple and thickest red roads first after a typhoon or lahar flow.');
    $("sheetBody").innerHTML=h; openSheet("half"); wireBack(); wireProfile(showCriticalRoads);
  });
}

/* ---- Definition 26 and Proposition 18 · new Malasakit Center sites ---- */
function siteSelection(theta,k,mob){
  const M=ptMatrix(mob), anchors=careAnchors(), now=Date.now();
  const class0=Object.keys(HOSP).filter(id=>P[id]&&HOSP[id].q===0&&suitable(id,3,0,now,[]));
  const C0=new Set(anchors.filter(a=>class0.some(h=>M[a][h]<=theta)));
  const Q=Object.keys(HOSP).filter(id=>P[id]&&HOSP[id].own==="government"&&HOSP[id].q===1&&HOSP[id].svc>=1&&!HOSP[id].svcU);
  const cover={}; Q.forEach(j=>{ cover[j]=anchors.filter(a=>M[a][j]<=theta); });
  const f=function(S){
    const U=new Set(C0); S.forEach(j=>cover[j].forEach(a=>U.add(a)));
    let s=0; U.forEach(a=>{ if (!C0.has(a)) s+=P[a].pop; }); return s;
  };
  const greedy=[];
  for (let i=0;i<Math.min(k,Q.length);i++){
    let best=null, bv=-1;
    Q.forEach(function(j){ if (greedy.indexOf(j)>=0) return; const v=f(greedy.concat([j])); if (v>bv){ bv=v; best=j; } });
    greedy.push(best);
  }
  let opt=[], ov=-1;
  (function rec(start,S){
    if (S.length===Math.min(k,Q.length)){ const v=f(S); if (v>ov){ ov=v; opt=S.slice(); } return; }
    for (let i=start;i<Q.length;i++){ S.push(Q[i]); rec(i+1,S); S.pop(); }
  })(0,[]);
  const pop=anchors.reduce((s,a)=>s+P[a].pop,0);
  const covPop=[...C0].reduce((s,a)=>s+P[a].pop,0);
  return {class0:class0,C0:C0,Q:Q,cover:cover,greedy:greedy,opt:opt,fG:f(greedy),fO:Math.max(0,ov),pop:pop,
          covPop:covPop,gains:greedy.map((j,i)=>f(greedy.slice(0,i+1))-(i?f(greedy.slice(0,i)):0))};
}
function showSites(){
  busy("Timing every town to every hospital by public transport…",function(){
    const s=siteSelection(PLAN.siteTheta,PLAN.k,PLAN.mob);
    const lay=careLayerNew(); clearRoute();
    careAnchors().forEach(function(a){
      const cov=s.C0.has(a), add=s.greedy.some(j=>s.cover[j].indexOf(a)>=0);
      L.circleMarker(P[a].ll,{renderer:canvasR,radius:7,color:"#fff",weight:2,
        fillColor:cov?"#188038":add?"#1A73E8":"#9AA0A6",fillOpacity:.95})
        .bindTooltip(P[a].name+(cov?" · already covered":add?" · covered by a new site":" · not covered")).addTo(lay);
    });
    s.Q.forEach(function(j){
      const pick=s.greedy.indexOf(j)>=0;
      L.circleMarker(P[j].ll,{renderer:canvasR,radius:pick?12:8,color:pick?"#1A73E8":"#5F6368",weight:3,
        fillColor:"#fff",fillOpacity:1}).bindTooltip(P[j].name+(pick?" · proposed":"")).addTo(lay);
    });
    let h=toolHead("New Malasakit Centers","Definition 26 · greedy choice · Proposition 18")+
      '<div class="cr-ctl">'+sel("stT",[[30,"30 min"],[45,"45 min"],[60,"60 min"],[90,"90 min"]],PLAN.siteTheta,"Within")+
      sel("stK",[[1,"1 site"],[2,"2 sites"],[3,"3 sites"]],PLAN.k,"Choose")+
      sel("stM",[["std","Walks normally"],["slow","Walks slowly"]],PLAN.mob,"Walking")+'</div>';
    h+='<div class="note">A Malasakit Center puts a government hospital in cost class 0, free or assisted care. '+
       'Today '+s.class0.length+' hospital'+(s.class0.length===1?' is':'s are')+' in that class ('+
       esc(s.class0.map(id=>P[id].name).join(", ")||"none")+'), reaching '+s.covPop.toLocaleString("en-PH")+' of '+
       s.pop.toLocaleString("en-PH")+' people at the town centres within '+PLAN.siteTheta+' min by public transport.</div>';
    if (!s.Q.length){
      h+='<div class="hm-bad">No government hospital of Level 1 or above is left without a Malasakit Center.</div>';
    } else {
      h+='<div class="hm-h">Proposed sites, in the order chosen</div>';
      s.greedy.forEach(function(j,i){
        h+='<div class="step"><span class="step-i cr-num">'+(i+1)+'</span><span class="step-b"><span class="step-t">'+
           esc(P[j].name)+'</span><span class="step-s">'+esc(svcLabel(j))+' · brings '+
           s.gains[i].toLocaleString("en-PH")+' more people within reach</span>'+
           (s.cover[j].length?'<span class="step-s">Reaches '+esc(s.cover[j].map(a=>P[a].name).join(", "))+'</span>':'')+
           '</span></div>';
      });
      h+='<div class="hm-kv" style="font-size:13.5px"><dt>Greedy choice</dt><dd>'+s.fG.toLocaleString("en-PH")+
         ' more people</dd><dt>Best possible</dt><dd>'+s.fO.toLocaleString("en-PH")+' (checked against all '+
         'combinations)</dd><dt>Ratio</dt><dd>'+(s.fO?(s.fG/s.fO*100).toFixed(1)+'%':'–')+
         ' · guaranteed at least 63.2%</dd></div>';
      h+='<div class="cr-fine">Candidates: '+esc(s.Q.map(id=>P[id].name).join(", "))+'.</div>';
    }
    h+=modelNote('Coverage counts the census population of each town centre within the time limit. It leaves out '+
       'the cost of a center, the beds at the chosen hospital and the crowding new users bring; check beds per '+
       'person for any site proposed.');
    $("sheetBody").innerHTML=h; openSheet("half"); wireBack();
    const w=(id,f)=>{ const e=document.getElementById(id); if (e) e.addEventListener("change",function(){ f(e.value); showSites(); }); };
    w("stT",v=>{PLAN.siteTheta=+v;}); w("stK",v=>{PLAN.k=+v;}); w("stM",v=>{PLAN.mob=v;});
  });
}

/* =====================================================================
   SHELL · the bottom bar, the More list and the opening screen
   ===================================================================== */
function showMore(){
  setTab("more");
  let h='<div style="padding:8px 0 10px"><div style="font-size:18px;font-weight:500">More</div></div>';
  const items=[
    ["About MAP-A Care","What it does, its sources and its limits","about"],
    ["Directions","Door-to-door trips on jeepneys, vans and buses","dir"],
    ["Routes","Every service in the feed, with fares","routes"],
    ["Saved places","Places and trips kept in this browser","saved"],
    ["Fare matrix","LTFRB rates in force from "+FARE_EFFECTIVE,"fare"],
    ["Network audit",ROADS.filter(r=>r.osm).length+" of "+ROADS.length+" road segments on real roads","audit"],
    ["Map background","Base map, overlays and tools","bg"],
    ["Privacy policy","No cookies, no analytics, nothing sent to the researchers","privacy"],
    ["About the MAP-A atlas","The transit atlas this app is built on","atlas"]
  ];
  items.forEach(function(it){
    h+='<button class="step" data-a="'+it[2]+'" style="width:100%;text-align:left"><span class="step-b">'+
      '<span class="step-t">'+esc(it[0])+'</span><span class="step-s">'+esc(it[1])+'</span></span></button>';
  });
  $("sheetBody").innerHTML=h; openSheet("half");
  $("sheetBody").querySelectorAll("[data-a]").forEach(function(b){
    b.addEventListener("click",function(){
      const a=b.dataset.a;
      if (a==="about") showCareAbout();
      if (a==="dir"){ hmOn=false; applyHospitalFilter(); careClear(); setTab("dir"); openDirections(); }
      if (a==="routes"){ hmOn=false; applyHospitalFilter(); careClear(); showRoutes(); }
      if (a==="saved"){ showSaved(); }
      if (a==="fare") showFareMatrix();
      if (a==="audit") showNetworkAudit();
      if (a==="bg"){ closeSheet(); $("layers").style.display="block"; $("btnLayers").classList.add("on"); }
      if (a==="privacy") showPrivacy();
      if (a==="atlas") showAbout();
    });
  });
}
function showCareAbout(){
  const nH=Object.keys(HOSP).filter(id=>P[id]).length;
  let h='<div class="cr-head"><div class="cr-badge">'+careIco.cross+'</div><div style="flex:1">'+
    '<div class="cr-title">MAP-A Care '+CARE_VERSION+'</div><div class="cr-sub">Right hospital, right bed, right time</div>'+
    '</div></div>';
  h+='<p class="cr-p">MAP-A Care finds the nearest hospital in Albay that can treat a patient, has a bed that is not '+
     'reported full, and accepts what the family can pay, by ambulance or by jeepney, van, bus and on foot. It '+
     'adds backups in case the first hospital turns the patient away, and planning tools for the health office.</p>';
  h+='<div class="hm-h">What it checks for each hospital</div><ul class="cr-ul">'+
     '<li>Level of care and the services that level offers: isolation, normal delivery, operating room, intensive '+
     'care, newborn intensive care, high-risk pregnancy, dialysis and blood bank</li>'+
     '<li>An emergency room, when the patient is in danger</li>'+
     '<li>A bed that is not reported full; an unreported hospital is shown as not reported, never as available</li>'+
     '<li>Cost class: free or assisted care, public, private with PhilHealth, any. The cost filter is lifted for '+
     'emergencies, as Republic Act No. 10932 requires</li></ul>';
  h+='<div class="hm-h">Sources</div><p class="cr-p">'+nH+' hospitals and infirmaries and their licensed beds from '+
     'the DOH National Health Facility Registry; service levels from the DOH (2012) classification; routes, stops, '+
     'fares and roads from the MAP-A atlas, built on OpenStreetMap; town populations from the 2020 census.</p>';
  h+='<div class="hm-h">Limits</div><ul class="cr-ul">'+
     '<li>No hospital has been contacted. Free beds appear only where someone enters a report in the bed '+
     'dashboard, and a report lapses after '+AGE_MAX_H+' hours.</li>'+
     '<li>Service lists follow the hospital level; a hospital may lack a service on a given day.</li>'+
     '<li>Travel times are model outputs from the MAP-A network at free-flow speeds plus the chosen traffic level.</li>'+
     '<li>Navigation and planning support only. It does not diagnose or triage and does not replace 911.</li></ul>';
  h+='<p class="cr-p" style="color:var(--gray)">A student research project of Legazpi City Science High School. '+
     'Not an official service of the DOH, the Provincial Health Office or any LGU.</p>';
  h+='<a class="hm-911" href="tel:911">Call 911</a>';
  $("sheetBody").innerHTML=h; openSheet("full");
}
function careInit(){
  if (!boot._done||typeof map==="undefined"||!map){ setTimeout(careInit,200); return; }
  const nav=$("bottomNav");
  nav.querySelectorAll("button").forEach(function(b){
    const ico=careIco[{hosp:"cross",plan:"plan",beds:"bed",map:"map",dir:"dir",more:"more"}[b.dataset.tab]];
    const bb=b.querySelector("b"); if (bb&&ico){ bb.innerHTML=ico; bb.classList.add("mi"); }
    b.addEventListener("click",function(){
      const t=b.dataset.tab;
      if (t!=="hosp"&&t!=="plan"&&t!=="beds") return;
      if (t==="plan") showPlanning();
      if (t==="beds"){ if (!hmOn){ hmOn=true; applyHospitalFilter(); $("top").style.display="none"; $("dir").style.display="none"; }
                       setTab("beds"); showBedDashboard(); }
      if (t==="hosp") careClear();
    });
    if (b.dataset.tab==="map") b.addEventListener("click",function(){ hmOn=false; applyHospitalFilter(); });
    if (b.dataset.tab==="dir") b.addEventListener("click",function(){ hmOn=false; applyHospitalFilter(); careClear(); });
  });
  hospitalMode();
}
document.addEventListener("DOMContentLoaded",function(){ setTimeout(careInit,0); });
