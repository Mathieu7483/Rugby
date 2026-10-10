/* Données et moteur de tournoi partagés par index.html (poules) et knockout.html (phases finales) */
const POOLS = {
  A:["New Zealand","Australia","Chile","Hong Kong China"],
  B:["South Africa","Italy","Georgia","Romania"],
  C:["Argentina","Fiji","Spain","Canada"],
  D:["Ireland","Scotland","Uruguay","Portugal"],
  E:["France","Japan","USA","Samoa"],
  F:["England","Wales","Tonga","Zimbabwe"]
};
const CODE = {"New Zealand":"NZL","Australia":"AUS","Chile":"CHI","Hong Kong China":"HKG","South Africa":"RSA","Italy":"ITA","Georgia":"GEO","Romania":"ROU","Argentina":"ARG","Fiji":"FIJ","Spain":"ESP","Canada":"CAN","Ireland":"IRL","Scotland":"SCO","Uruguay":"URU","Portugal":"POR","France":"FRA","Japan":"JPN","USA":"USA","Samoa":"SAM","England":"ENG","Wales":"WAL","Tonga":"TGA","Zimbabwe":"ZIM"};
const FR = {"New Zealand":"Nouvelle-Zélande","Australia":"Australie","Chile":"Chili","Hong Kong China":"Hong Kong Chine","South Africa":"Afrique du Sud","Italy":"Italie","Georgia":"Géorgie","Romania":"Roumanie","Argentina":"Argentine","Fiji":"Fidji","Spain":"Espagne","Canada":"Canada","Ireland":"Irlande","Scotland":"Écosse","Uruguay":"Uruguay","Portugal":"Portugal","France":"France","Japan":"Japon","USA":"États-Unis","Samoa":"Samoa","England":"Angleterre","Wales":"Pays de Galles","Tonga":"Tonga","Zimbabwe":"Zimbabwe"};
const ALL_TEAMS = Object.values(POOLS).flat();

/* Estimation de secours (points World Rugby approximatifs) si predictions.js est absent */
const FALLBACK = {"South Africa":93,"New Zealand":90,"Ireland":88,"France":88,"England":86,"Argentina":85,"Scotland":82,"Australia":80,"Fiji":80,"Italy":78,"Japan":76,"Georgia":75,"Wales":72,"Samoa":72,"Uruguay":70,"USA":70,"Tonga":69,"Spain":68,"Portugal":66,"Chile":66,"Canada":64,"Romania":62,"Hong Kong China":55,"Zimbabwe":50};
const fallbackP = (a,b)=>{
  const d = FALLBACK[a]-FALLBACK[b] + (a==="Australia"?3:0) - (b==="Australia"?3:0);
  return 1/(1+Math.pow(10,-d/10));
};

const MODEL = (typeof window!=="undefined" && window.PREDICTIONS) || null;
const usingModel = !!(MODEL && Object.keys(MODEL).length);

/* Probabilité que a batte b (cherche la paire dans les deux ordres) */
const _cache = {};
function probA(a,b){
  const k = a+"|"+b;
  if (_cache[k] !== undefined) return _cache[k];
  let p;
  if (MODEL && MODEL[k] != null) p = MODEL[k];
  else if (MODEL && MODEL[b+"|"+a] != null) p = 1 - MODEL[b+"|"+a];
  else p = fallbackP(a,b);
  return (_cache[k] = p);
}

/* ---------- Poules ---------- */
function poolPoints(teams, mode){
  const pts = [0,0,0,0];
  for (let i=0;i<4;i++) for (let j=i+1;j<4;j++){
    const p = probA(teams[i],teams[j]);
    if (mode==="random"){ Math.random()<p ? pts[i]+=4 : pts[j]+=4; }
    else { pts[i]+=4*p; pts[j]+=4*(1-p); }   // mode "fav" : points espérés
  }
  return pts;
}

/* ---------- Meilleurs troisièmes -> adversaires des vainqueurs A, B, C, D ----------
   Règles officielles connues : A3->C1, B3->D1, C3->A1, D3->B1.
   Les 3es des poules E et F prennent les places restantes (A1 < B1 < C1 < D1).
   Quand E et F sont tous deux qualifiés, l'ordre exact vient du tableau officiel
   des 15 combinaisons, non reproduit ici : approximation (E3 avant F3). */
function assignThirds(qualPools){
  const fixed = {A:"C", B:"D", C:"A", D:"B"};    // poule du 3e -> poule du vainqueur affronté
  const slots = {A:null,B:null,C:null,D:null};
  qualPools.forEach(p => { if (fixed[p]) slots[fixed[p]] = p; });
  const free = ["A","B","C","D"].filter(s => !slots[s]);
  const ef = qualPools.filter(p => p==="E"||p==="F").sort();
  free.forEach((s,i)=> slots[s] = ef[i]);
  return slots;
}

/* ---------- Tournoi complet ----------
   mode "random" : tirage aléatoire ; mode "fav" : le favori gagne toujours. */
function runTournament(mode){
  const standings = {}, thirds = [];
  for (const [L,teams] of Object.entries(POOLS)){
    const pts = poolPoints(teams, mode);
    const order = teams.map((t,i)=>({team:t,pts:pts[i],r:Math.random()}))
                       .sort((x,y)=>y.pts-x.pts||x.r-y.r);
    standings[L] = order;
    thirds.push({pool:L, ...order[2]});
  }
  thirds.sort((x,y)=>y.pts-x.pts||x.r-y.r);
  const qual = thirds.slice(0,4);
  const slots = assignThirds(qual.map(t=>t.pool));

  const w = L => standings[L][0].team, r = L => standings[L][1].team;
  const th = L => standings[slots[L]][2].team;

  const play = (a,b,la,lb)=>{
    const pa = probA(a,b);
    const aWins = mode==="random" ? Math.random()<pa : pa>=0.5;
    return {a,b,pa,la,lb,winner:aWins?a:b};
  };
  const r16 = [
    play(w("A"),th("A"),"1er A","3e "+slots.A),
    play(w("B"),th("B"),"1er B","3e "+slots.B),
    play(w("E"),r("D"),"1er E","2e D"),
    play(r("C"),r("F"),"2e C","2e F"),
    play(w("C"),th("C"),"1er C","3e "+slots.C),
    play(w("D"),th("D"),"1er D","3e "+slots.D),
    play(w("F"),r("B"),"1er F","2e B"),
    play(r("A"),r("E"),"2e A","2e E")
  ];
  const meet = (m1,m2,l1,l2)=>play(m1.winner,m2.winner,l1,l2);
  const qf = [
    meet(r16[0],r16[1],"V. M1","V. M2"), meet(r16[2],r16[3],"V. M3","V. M4"),
    meet(r16[4],r16[5],"V. M5","V. M6"), meet(r16[6],r16[7],"V. M7","V. M8")
  ];
  const sf = [meet(qf[0],qf[1],"V. QF1","V. QF2"), meet(qf[2],qf[3],"V. QF3","V. QF4")];
  const final = meet(sf[0],sf[1],"V. DF1","V. DF2");
  return {standings, qual, slots, r16, qf, sf, final, champion:final.winner};
}

/* ---------- Monte Carlo : chances d'atteindre chaque tour ---------- */
function monteCarlo(N=5000){
  const c = {};
  ALL_TEAMS.forEach(t=>c[t]={r16:0,qf:0,sf:0,f:0,w:0});
  for (let s=0;s<N;s++){
    const t = runTournament("random");
    t.r16.forEach(m=>{c[m.a].r16++;c[m.b].r16++;});
    t.qf.forEach(m=>{c[m.a].qf++;c[m.b].qf++;});
    t.sf.forEach(m=>{c[m.a].sf++;c[m.b].sf++;});
    c[t.final.a].f++; c[t.final.b].f++; c[t.champion].w++;
  }
  ALL_TEAMS.forEach(t=>{for(const k in c[t]) c[t][k]/=N;});
  return c;
}

if (typeof module!=="undefined") module.exports = {runTournament, monteCarlo, assignThirds, probA, ALL_TEAMS};