/* TANTIYA engine: plan-based quantity take-off, DUPA unit costs, DPWH-style indirect costs,
   and the hybrid over-budget screen (OLS baseline, regularized gradient-boosted trees, Isolation Forest, Shapley values).
   Runs unchanged in the browser (window.TANTIYA) and in Node (require). No dependencies. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.TANTIYA = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var VERSION = '1.0.0';
  var BASE_YEAR = 2025;

  /* ---------- Basic prices: Region V, indicative 2025 base. Replace with the current DPWH CMPD,
     ACEL rental rates and the regional wage order before quoting. ---------- */
  var BASE_PRICES = {
    cement:    { g: 'Materials', label: 'Portland cement, 40 kg bag', unit: 'bag', v: 270 },
    sand:      { g: 'Materials', label: 'Washed sand', unit: 'm³', v: 1200 },
    gravel:    { g: 'Materials', label: 'Crushed gravel, 19 mm', unit: 'm³', v: 1500 },
    rebar:     { g: 'Materials', label: 'Deformed bar, Grade 40/60', unit: 'kg', v: 48 },
    tiewire:   { g: 'Materials', label: 'Tie wire, G.I. #16', unit: 'kg', v: 90 },
    plywood:   { g: 'Materials', label: 'Plywood 12 mm, 1.22 × 2.44 m', unit: 'sheet', v: 750 },
    lumber:    { g: 'Materials', label: 'Form lumber', unit: 'bd-ft', v: 45 },
    nails:     { g: 'Materials', label: 'Common wire nails', unit: 'kg', v: 95 },
    chb100:    { g: 'Materials', label: 'Concrete hollow block 100 mm', unit: 'pc', v: 16 },
    chb150:    { g: 'Materials', label: 'Concrete hollow block 150 mm', unit: 'pc', v: 24 },
    roofsheet: { g: 'Materials', label: 'Pre-painted long-span sheet 0.40 mm', unit: 'm²', v: 450 },
    steel:     { g: 'Materials', label: 'Cold-formed steel (purlins, trusses)', unit: 'kg', v: 75 },
    paint:     { g: 'Materials', label: 'Paint system, primer + 2 coats', unit: 'm²', v: 95 },
    fcboard:   { g: 'Materials', label: 'Fiber-cement board 4.5 mm', unit: 'sheet', v: 450 },
    furring:   { g: 'Materials', label: 'Metal furring and hangers', unit: 'm²', v: 180 },
    tile:      { g: 'Materials', label: 'Ceramic floor tile 600 × 600', unit: 'm²', v: 550 },
    skilled:   { g: 'Labor', label: 'Skilled worker, 8-hour day', unit: 'day', v: 650 },
    unskilled: { g: 'Labor', label: 'Laborer, 8-hour day', unit: 'day', v: 480 },
    equipMix:  { g: 'Equipment', label: 'Mixer and vibrator', unit: 'm³', v: 300 },
    equipExc:  { g: 'Equipment', label: 'Backhoe excavation', unit: 'm³', v: 90 },
    equipComp: { g: 'Equipment', label: 'Plate compactor', unit: 'm³', v: 40 },
    equipLift: { g: 'Equipment', label: 'Pump or crane for bridge concrete', unit: 'm³', v: 450 },
    window:    { g: 'Supply and install', label: 'Aluminum-framed glass window', unit: 'm²', v: 4200 },
    door:      { g: 'Supply and install', label: 'Door set with jamb and hardware', unit: 'set', v: 9500 },
    fixture:   { g: 'Supply and install', label: 'Plumbing fixture with piping', unit: 'set', v: 20000 },
    elec:      { g: 'Supply and install', label: 'Electrical works', unit: 'm² GFA', v: 950 },
    gutter:    { g: 'Supply and install', label: 'Gutter and downspout, pre-painted', unit: 'lm', v: 650 },
    handrail:  { g: 'Supply and install', label: 'Steel pipe railing, stairs and corridors', unit: 'lm', v: 3800 },
    septic:    { g: 'Supply and install', label: 'Septic tank, two chambers', unit: 'set', v: 150000 },
    water:     { g: 'Supply and install', label: 'Water service line and elevated tank', unit: 'lot', v: 85000 },
    ramp:      { g: 'Supply and install', label: 'Accessibility ramp with railings (BP 344)', unit: 'lot', v: 45000 },
    fire:      { g: 'Supply and install', label: 'Fire extinguishers, emergency lights, exit signs', unit: 'per floor', v: 25000 },
    termite:   { g: 'Supply and install', label: 'Soil poisoning', unit: 'm²', v: 55 },
    clearing:  { g: 'Supply and install', label: 'Clearing and grubbing', unit: 'm²', v: 30 },
    boring:    { g: 'Supply and install', label: 'Bored-pile drilling with casing', unit: 'm³ of bore', v: 15000 },
    psc:       { g: 'Supply and install', label: 'Precast PSC I-girder, base rate', unit: 'lm', v: 16000 },
    pscSpan:   { g: 'Supply and install', label: 'PSC girder rate added per metre of span', unit: 'lm per m', v: 480 },
    bearing:   { g: 'Supply and install', label: 'Elastomeric bearing pad', unit: 'pc', v: 18000 },
    expjoint:  { g: 'Supply and install', label: 'Expansion joint', unit: 'lm', v: 22000 },
    railing:   { g: 'Supply and install', label: 'Steel bridge railing', unit: 'lm', v: 6500 },
    riprap:    { g: 'Supply and install', label: 'Grouted riprap', unit: 'm³', v: 3200 },
    embank:    { g: 'Supply and install', label: 'Embankment for approaches', unit: 'm³', v: 420 },
    cofferdam: { g: 'Supply and install', label: 'Cofferdam and dewatering', unit: 'per pier', v: 250000 },
    billboard: { g: 'Supply and install', label: 'Project billboard', unit: 'lot', v: 8000 }
  };

  function prices(over) {
    var P = {};
    for (var k in BASE_PRICES) P[k] = over && over[k] != null ? +over[k] : BASE_PRICES[k].v;
    return P;
  }

  /* Concrete: bags of cement, m³ of sand and m³ of gravel per m³ (Class A = 360 kg cement, 20.7 MPa). */
  var MIX = {
    A:   { bags: 9.0,  sand: 0.50, gravel: 1.00, label: 'Class A, 20.7 MPa' },
    S28: { bags: 10.5, sand: 0.45, gravel: 0.90, label: 'f′c 27.6 MPa' }
  };

  /* Steel intensity, kg of bar per m³ of concrete, before 7% laps and hooks. Lean = near code minimum. */
  var RHO = {
    footing: 90, pedestal: 200, tiebeam: 130, column: 200, beam: 180, slab: 100, sog: 30, stair: 110,
    deck: 160, girder: 220, diaphragm: 140, curb: 120, abutment: 110, piercol: 160, piercap: 150, pilecap: 100, pile: 110, approach: 100
  };
  var LAP = 1.07;

  /* ---------- DUPA: labor, equipment (incl. minor tools at 10% of labor) and materials per unit ---------- */
  function catalog(P, opt) {
    opt = opt || {};
    var esc = opt.escalation == null ? 0.04 : opt.escalation;
    var year = opt.year || BASE_YEAR;
    var f = Math.pow(1 + esc, year - BASE_YEAR);
    function L(sk, un) { return sk * P.skilled + un * P.unskilled; }
    function conc(mix) { var m = MIX[mix]; return 1.05 * (m.bags * P.cement + m.sand * P.sand + m.gravel * P.gravel); }
    var C = {};
    function add(id, ref, desc, unit, lab, eqp, mat, si) {
      var e = eqp + (si ? 0 : 0.10 * lab);
      C[id] = { id: id, ref: ref, desc: desc, unit: unit, lab: lab * f, eqp: e * f, mat: mat * f, si: !!si, unitCost: (lab + e + mat) * f };
    }
    var formMat = 0.336 / 3 * P.plywood + 7 / 3 * P.lumber + 0.15 * P.nails;
    /* general requirements */
    add('billboard', 'B.5', 'Project billboard / signboard', 'lot', 0, 0, P.billboard, true);
    /* buildings */
    add('clearing', '800(1)', 'Clearing and grubbing', 'm²', 0, 0, P.clearing, true);
    add('excav', '803(1)a', 'Structure excavation, common soil', 'm³', L(0, 0.35), P.equipExc, 0);
    add('backfill', '804(1)a', 'Backfill and compaction from excavated material', 'm³', L(0, 0.30), P.equipComp, 0);
    add('gravel', '—', 'Gravel bedding and fill', 'm³', L(0, 0.50), 0, 1.15 * P.gravel);
    add('termite', '1000(1)', 'Soil poisoning', 'm²', 0, 0, P.termite, true);
    add('concA', '900(1)c', 'Structural concrete, ' + MIX.A.label, 'm³', L(0.6, 1.2), P.equipMix, conc('A'));
    add('rebar', '902(1)a', 'Reinforcing steel, deformed, Grade 40/60', 'kg', L(0.012, 0.006), 0.6, 1.03 * P.rebar + 0.015 * P.tiewire);
    add('form', '903(2)', 'Formworks and falseworks (3 uses)', 'm²', L(0.25, 0.15), 40, formMat);
    add('chb100', '1046(2)a1', 'CHB wall 100 mm, reinforced, with mortar', 'm²', L(0.20, 0.15), 0,
      12.5 * 1.05 * P.chb100 + 0.522 * P.cement + 0.0435 * P.sand + 1.9 * P.rebar);
    add('chb150', '1046(2)a2', 'CHB wall 150 mm, reinforced, with mortar', 'm²', L(0.22, 0.16), 0,
      12.5 * 1.05 * P.chb150 + 0.80 * P.cement + 0.066 * P.sand + 2.2 * P.rebar);
    add('plaster', '1027(1)', 'Cement plaster finish, 16 mm', 'm²', L(0.18, 0.10), 0, 0.17 * P.cement + 0.019 * P.sand);
    add('paint', '1032(1)a', 'Painting, masonry and concrete', 'm²', L(0.08, 0), 0, P.paint);
    add('roofframe', '1047', 'Roof framing, cold-formed steel', 'kg', L(0.010, 0.006), 3, 1.05 * P.steel + 5);
    add('roofing', '1013', 'Pre-painted long-span metal roofing with accessories', 'm²', L(0.15, 0.10), 0, 1.10 * P.roofsheet + 55);
    add('ceiling', '1003', 'Ceiling, fiber-cement board on metal furring', 'm²', L(0.20, 0.10), 0, 0.336 * 1.05 * P.fcboard + P.furring);
    add('floorplain', '—', 'Floor finish, plain cement (steel trowel)', 'm²', L(0.08, 0.04), 0, 0.06 * P.cement + 0.004 * P.sand);
    add('floortile', '1018', 'Floor tiles, 600 × 600 ceramic', 'm²', L(0.25, 0.10), 0, 1.05 * P.tile + 120);
    add('window', '—', 'Windows, aluminum frame and glass', 'm²', 0, 0, P.window, true);
    add('door', '—', 'Doors with jambs and hardware', 'set', 0, 0, P.door, true);
    add('fixture', '1002', 'Plumbing fixtures with water and sanitary lines', 'set', 0, 0, P.fixture, true);
    add('elec', '1100–1102', 'Electrical works: conduits, wiring, panel, lighting', 'm²', 0, 0, P.elec, true);
    add('apron', '—', 'Concrete apron and walkway, 100 mm on gravel bed', 'm²', 0.1 * L(0.6, 1.2), 0.1 * P.equipMix, 0.1 * conc('A') + 0.05 * 1.15 * P.gravel);
    add('gutter', '—', 'Gutters and downspouts', 'lm', 0, 0, P.gutter, true);
    add('handrail', '—', 'Steel pipe railings, stairs and corridors', 'lm', 0, 0, P.handrail, true);
    add('septic', '—', 'Septic tank, two chambers', 'set', 0, 0, P.septic, true);
    add('water', '—', 'Water service line and elevated tank', 'lot', 0, 0, P.water, true);
    add('ramp', '—', 'Accessibility ramp with railings (BP 344)', 'lot', 0, 0, P.ramp, true);
    add('fire', '—', 'Fire extinguishers, emergency lights, exit signs', 'per floor', 0, 0, P.fire, true);
    /* bridges */
    add('bexcav', '103(2)', 'Structure excavation', 'm³', L(0, 0.35), P.equipExc, 0);
    add('embank', '104(1)', 'Embankment for approaches', 'm³', 0, 0, P.embank, true);
    add('bore', '400', 'Bored piles, drilling with casing', 'lm', 0, 0, 0, true); /* unit cost set by pile diameter */
    add('pileconc', '400', 'Bored-pile concrete, tremie, ' + MIX.A.label, 'm³', L(0.5, 1.0), P.equipMix + 200, conc('A'));
    add('brebar', '404', 'Reinforcing steel, Grade 60', 'kg', L(0.012, 0.006), 0.6, 1.03 * P.rebar + 0.015 * P.tiewire);
    add('concSub', '405', 'Structural concrete, ' + MIX.A.label + ' (substructure)', 'm³', L(0.6, 1.2), P.equipMix, conc('A'));
    add('concSup', '405', 'Structural concrete, ' + MIX.S28.label + ' (superstructure)', 'm³', L(0.7, 1.4), P.equipMix + P.equipLift, conc('S28') + 250);
    add('bform', '405', 'Formworks and falseworks (subsidiary to Item 405)', 'm²', L(0.30, 0.20), 80, formMat + 120);
    add('psc', '406', 'Precast PSC I-girders, supply and launch', 'lm', 0, 0, 0, true); /* unit cost set by span */
    add('bearing', '412', 'Elastomeric bearing pads', 'pc', 0, 0, P.bearing, true);
    add('expjoint', '—', 'Expansion joints', 'lm', 0, 0, P.expjoint, true);
    add('railing', '401', 'Railings, steel', 'lm', 0, 0, P.railing, true);
    add('riprap', '505', 'Grouted riprap', 'm³', 0, 0, P.riprap, true);
    add('cofferdam', '—', 'Cofferdam and dewatering', 'per pier', 0, 0, P.cofferdam, true);
    C._f = f;
    return C;
  }

  /* ---------- Building take-off ---------- */
  var BUILDING_DEFAULTS = {
    kind: 'building', name: 'New building', province: 'Albay', year: BASE_YEAR, use: 'school',
    L: 18, W: 9, N: 2, h: 3.2, sx: 4.5, sy: 4.5,
    col: 0.40, bw: 0.30, hb: 0.50, ts: 0.125, sog: 0.10,
    B: 1.6, tf: 0.40, Df: 1.5,
    wallDensity: 0.15, openExt: 0.25, openInt: 0.08,
    pitch: 18, eave: 0.9, finish: 'lean', fixtures: 0,
    area: 0, perim: 0, nCols: 0, wallLen: 0
  };

  var BRIDGE_DEFAULTS = {
    kind: 'bridge', name: 'New bridge', province: 'Albay', year: BASE_YEAR,
    ns: 2, Ls: 20, Wc: 6.70, sw: 0.75, sup: 'RCDG', ts: 0.20, gs: 2.1,
    Ha: 6.0, Hp: 7.0, pilesA: 6, pilesP: 6, D: 1.0, Lp: 18, appr: 5.0, riprap: 120, water: true
  };

  function fill(defs, p) {
    var o = {};
    for (var k in defs) o[k] = p && p[k] != null && p[k] !== '' ? p[k] : defs[k];
    for (var k2 in o) if (typeof defs[k2] === 'number') o[k2] = +o[k2];
    if (typeof o.water === 'string') o.water = o.water === 'true' || o.water === '1' || o.water === 'yes';
    return o;
  }

  function takeoffBuilding(p0) {
    var p = fill(BUILDING_DEFAULTS, p0);
    var L = p.L, W = p.W, N = Math.max(1, Math.round(p.N)), h = p.h, b = p.col;
    var foot = p.area > 0 ? p.area : L * W;
    var P = p.perim > 0 ? p.perim : 2 * (L + W);
    var nx = Math.max(1, Math.round(L / p.sx)), ny = Math.max(1, Math.round(W / p.sy));
    var Nc = p.nCols > 0 ? Math.round(p.nCols) : (nx + 1) * (ny + 1);
    var gfa = foot * N;
    var lenGrid = (ny + 1) * L + (nx + 1) * W;
    var spans = (ny + 1) * nx + (nx + 1) * ny;
    var net = Math.max(0, lenGrid - spans * b);
    var Q = [];
    function q(id, qty, group, note) { if (qty > 0) Q.push({ id: id, qty: qty, group: group, note: note || '' }); }

    /* earthworks */
    var Vexc = Nc * Math.pow(p.B + 0.6, 2) * p.Df + net * (0.25 + 0.4) * 0.5;
    var Vftg = Nc * p.B * p.B * p.tf;
    var Vped = Nc * b * b * Math.max(0, p.Df - p.tf);
    var Vtb = net * 0.25 * 0.40;
    var Vbed = Nc * p.B * p.B * 0.10 + foot * 0.10;
    var Vback = Math.max(0, Vexc - Vftg - Vped - Nc * p.B * p.B * 0.10 - Vtb);

    /* concrete */
    var Vcol = N * Nc * b * b * h;
    var VbF = (N - 1) * net * p.bw * (p.hb - p.ts);
    var VbR = net * 0.25 * 0.40;
    var Vslab = (N - 1) * foot * p.ts;
    var Vsog = foot * p.sog;
    var nr = Math.ceil(h / 0.175), run = nr / 2 * 0.275, incl = Math.sqrt(run * run + h * h / 4);
    var Vst = N > 1 ? (N - 1) * (2 * (1.5 * incl * 0.15 + nr / 2 * 0.5 * 0.175 * 0.275 * 1.5) + 1.5 * 3.0 * 0.15) : 0;
    var conc = { footing: Vftg, pedestal: Vped, tiebeam: Vtb, column: Vcol, beam: VbF + VbR, slab: Vslab, sog: Vsog, stair: Vst };
    var Vc = 0, kg = 0;
    for (var e in conc) { Vc += conc[e]; kg += conc[e] * RHO[e] * LAP; }

    /* formwork */
    var Fm = Nc * 4 * p.B * p.tf + Nc * 4 * b * Math.max(0, p.Df - p.tf) + net * 2 * 0.40
      + N * Nc * 4 * b * Math.max(0, h - p.hb)
      + (N - 1) * net * (2 * (p.hb - p.ts) + p.bw) + net * (2 * 0.40 + 0.25)
      + Math.max(0, (N - 1) * (foot - net * p.bw))
      + (N > 1 ? (N - 1) * (2 * 1.5 * incl + 1.5 * 3.0 + nr * 1.5 * 0.175) : 0);

    /* masonry and finishes */
    var wallH = Math.max(0, h - p.hb);
    var perimCols = Math.min(Nc, 2 * (nx + ny));
    var Aext = Math.max(0, P - perimCols * b) * wallH * N * (1 - p.openExt);
    var Lint = p.wallLen > 0 ? p.wallLen * N : p.wallDensity * gfa;
    var Aint = Lint * wallH * (1 - p.openInt);
    var exposed = N * Nc * 4 * b * Math.max(0, h - p.hb) + (N - 1) * net * (2 * (p.hb - p.ts) + p.bw);
    var Aplaster = 2 * (Aext + Aint) + 0.6 * exposed;
    var Aceil = foot;
    var Apaint = Aplaster + Aceil + (N - 1) * foot;
    var Awin = Math.max(0, P - perimCols * b) * wallH * N * p.openExt * 0.75;
    var nDoor = Math.max(2, Math.ceil(gfa / 35));
    var nFix = p.fixtures > 0 ? Math.round(p.fixtures) : Math.max(2, Math.ceil(gfa / 80));
    var lean = p.finish !== 'standard';
    var Atile = lean ? 0.06 * gfa : gfa;
    var Aplain = Math.max(0, gfa - Atile);

    /* roof */
    var Lr = L + 2 * p.eave, Wr = (foot / L) + 2 * p.eave;
    var Aplan = Lr * Wr, Aroof = Aplan / Math.cos(p.pitch * Math.PI / 180);
    var kgRoof = (lean ? 14 : 18) * Aplan;

    q('billboard', 1, 'General requirements');
    q('clearing', (L + 6) * (foot / L + 6), 'Earthworks');
    q('excav', Vexc, 'Earthworks');
    q('backfill', Vback, 'Earthworks');
    q('gravel', Vbed, 'Earthworks');
    q('termite', foot, 'Earthworks');
    q('concA', Vc, 'Concrete works', fmt1(Vc) + ' m³ in ' + Nc + ' footings and columns, beams, ' + (N - 1) + ' suspended slab(s), slab on grade' + (Vst ? ', stairs' : ''));
    q('rebar', kg, 'Concrete works', 'Steel intensity by element, 7% laps and hooks');
    q('form', Fm, 'Concrete works', 'Contact area');
    q('chb150', Aext, 'Masonry and finishes', 'Exterior walls less ' + Math.round(p.openExt * 100) + '% openings');
    q('chb100', Aint, 'Masonry and finishes', 'Partitions less ' + Math.round(p.openInt * 100) + '% openings');
    q('plaster', Aplaster, 'Masonry and finishes', 'Both wall faces and exposed concrete');
    q('paint', Apaint, 'Masonry and finishes');
    q('floorplain', Aplain, 'Masonry and finishes');
    q('floortile', Atile, 'Masonry and finishes', lean ? 'Toilets and wet areas (6% of GFA)' : 'All floors');
    q('roofframe', kgRoof, 'Roofing and ceiling', (lean ? 14 : 18) + ' kg per m² of roof plan');
    q('roofing', Aroof, 'Roofing and ceiling', 'Slope ' + p.pitch + '°, eaves ' + p.eave + ' m');
    q('ceiling', Aceil, 'Roofing and ceiling', 'Top floor; lower soffits painted');
    q('window', Awin, 'Doors and windows');
    q('door', nDoor, 'Doors and windows', '1 per 35 m² of GFA');
    q('fixture', nFix, 'Plumbing', p.fixtures > 0 ? 'From plan' : '1 per 80 m² of GFA');
    q('elec', gfa, 'Electrical');
    q('apron', P * 1.0, 'Auxiliary works', '1.0 m wide around the building');
    q('gutter', 2 * Lr, 'Auxiliary works', 'Both eaves');
    q('handrail', N > 1 ? (N - 1) * (L + 2 * 2 * incl) : 0, 'Auxiliary works', 'Upper corridors and stairs');
    q('septic', Math.max(1, Math.ceil(nFix / 12)), 'Auxiliary works');
    q('water', 1, 'Auxiliary works');
    q('ramp', 1, 'Auxiliary works');
    q('fire', N, 'Auxiliary works');

    return {
      kind: 'building', params: p, lines: Q,
      geo: { gfa: gfa, foot: foot, perim: P, N: N, nCols: Nc, nx: nx, ny: ny, concrete: Vc, steel: kg, form: Fm, wallExt: Aext, wallInt: Aint, roof: Aroof, beamLen: net },
      basis: { label: 'GFA', area: gfa }
    };
  }

  /* ---------- Bridge take-off ---------- */
  function takeoffBridge(p0) {
    var p = fill(BRIDGE_DEFAULTS, p0);
    var ns = Math.max(1, Math.round(p.ns)), Ls = p.Ls;
    var Wt = p.Wc + 2 * p.sw + 2 * 0.25;
    var Ltot = ns * Ls;
    var ng = Math.max(3, Math.round((Wt - 1.0) / p.gs) + 1);
    var s = (Wt - 1.0) / (ng - 1);
    var Adeck = Wt * Ltot;
    var Q = [];
    function q(id, qty, group, note, unitCost) { if (qty > 0) Q.push({ id: id, qty: qty, group: group, note: note || '', unitCost: unitCost }); }
    var conc = { sup: {}, sub: {} }, forms = 0, hg;

    conc.sup.deck = Adeck * p.ts;
    forms += Adeck + 2 * Ltot * p.ts;
    if (p.sup === 'PSCG') {
      hg = Math.max(1.14, 0.045 * Ls) + p.ts;
      var nd = ns * 3;
      conc.sup.diaphragm = nd * (ng - 1) * Math.max(0, s - 0.5) * 0.25 * Math.max(0.3, hg - p.ts - 0.2);
      forms += nd * (ng - 1) * Math.max(0, s - 0.5) * 2 * Math.max(0.3, hg - p.ts - 0.2) - ng * Ltot * 0.5;
    } else {
      hg = Math.max(0.9, 0.07 * Ls);
      var bw = 0.40;
      conc.sup.girder = ng * Ltot * bw * (hg - p.ts);
      var nd2 = ns * (Ls > 20 ? 4 : 3);
      conc.sup.diaphragm = nd2 * (ng - 1) * Math.max(0, s - bw) * 0.25 * Math.max(0.3, hg - p.ts - 0.15);
      forms += ng * Ltot * (2 * (hg - p.ts) + bw) - ng * Ltot * bw + nd2 * (ng - 1) * Math.max(0, s - bw) * 2 * Math.max(0.3, hg - p.ts - 0.15);
    }
    conc.sup.curb = 2 * Ltot * 0.25 * 0.35;
    forms += 2 * Ltot * 0.35 * 2;

    var Wa = Wt + 0.5;
    var abStem = Wa * p.Ha * 0.8 + 0.3 * (hg + 0.2) * Wa + 2 * (4.0 * p.Ha * 0.4);
    conc.sub.abutment = 2 * abStem;
    conc.sub.pilecap = 2 * Wa * 3.0 * 1.2 + (ns - 1) * Wt * 3.0 * 1.2 * 0.85;
    conc.sub.piercol = (ns - 1) * 2 * Math.PI / 4 * 1.44 * p.Hp;
    conc.sub.piercap = (ns - 1) * Wt * 1.5 * 1.2;
    conc.sub.approach = 2 * Wt * p.appr * 0.25;
    forms += 2 * (2 * Wa * p.Ha + 2 * 2 * 4.0 * p.Ha) + 2 * 2 * (Wa + 3.0) * 1.2 + (ns - 1) * 2 * (Wt * 0.85 + 3.0) * 1.2
      + (ns - 1) * 2 * Math.PI * 1.2 * p.Hp + (ns - 1) * (2 * 1.2 * Wt + 2 * 1.5 * 1.2 + 1.5 * Wt) + 2 * 2 * (Wt + p.appr) * 0.25;

    var nP = 2 * p.pilesA + (ns - 1) * p.pilesP;
    var lenPile = nP * p.Lp;
    var Apile = Math.PI / 4 * p.D * p.D;
    var Vpile = lenPile * Apile * 1.10;
    var Vexc = 2 * (Wa + 1) * 4.0 * 2.2 + (ns - 1) * (Wt + 1) * 4.0 * 2.2;
    var Vemb = 2 * (Wt + 2) * p.Ha * 0.5 * 15;

    var Vsup = 0, Vsub = 0, kg = 0;
    var rmap = { deck: 'deck', girder: 'girder', diaphragm: 'diaphragm', curb: 'curb', abutment: 'abutment', pilecap: 'pilecap', piercol: 'piercol', piercap: 'piercap', approach: 'approach' };
    for (var a in conc.sup) { Vsup += conc.sup[a]; kg += conc.sup[a] * RHO[rmap[a]] * LAP; }
    for (var c in conc.sub) { Vsub += conc.sub[c]; kg += conc.sub[c] * RHO[rmap[c]] * LAP; }
    kg += Vpile / 1.10 * RHO.pile * LAP;

    q('billboard', 1, 'General requirements');
    q('bexcav', Vexc, 'Earthworks');
    q('embank', Vemb, 'Earthworks', 'Two 15 m approach fills');
    q('bore', lenPile, 'Foundation', nP + ' piles × ' + p.Lp + ' m, ' + p.D + ' m dia.', null);
    q('pileconc', Vpile, 'Foundation', '10% overbreak');
    q('concSub', Vsub, 'Substructure', '2 abutments' + (ns > 1 ? ', ' + (ns - 1) + ' pier(s)' : '') + ', pile caps, approach slabs');
    q('concSup', Vsup, 'Superstructure', p.sup === 'PSCG' ? 'Deck, diaphragms, curbs' : 'Deck, ' + ng + ' girders (depth ' + fmt2(hg) + ' m = 0.070 L), diaphragms, curbs');
    if (p.sup === 'PSCG') q('psc', ng * Ltot, 'Superstructure', ng + ' girders × ' + ns + ' span(s), depth ' + fmt2(hg - p.ts) + ' m ≥ 0.045 L', null);
    q('brebar', kg, 'Concrete works', 'Steel intensity by element, 7% laps and hooks');
    q('bform', forms, 'Concrete works', 'Contact area');
    q('bearing', 2 * ng * ns, 'Superstructure');
    q('expjoint', (ns + 1) * Wt, 'Superstructure');
    q('railing', 2 * Ltot, 'Superstructure');
    q('riprap', p.riprap, 'Slope protection');
    if (p.water && ns > 1) q('cofferdam', ns - 1, 'Foundation');

    return {
      kind: 'bridge', params: p, lines: Q,
      geo: { length: Ltot, width: Wt, deck: Adeck, girders: ng, girderDepth: hg, spacing: s, piles: nP, pileLen: lenPile, concrete: Vsup + Vsub + Vpile, steel: kg, form: forms },
      basis: { label: 'deck area', area: Adeck }
    };
  }

  function takeoff(p) { return (p && p.kind === 'bridge') ? takeoffBridge(p) : takeoffBuilding(p); }

  /* ---------- Indirect costs: graduated OCM and profit on the estimated direct cost, then VAT ---------- */
  function indirect(edc) {
    if (edc <= 5e6) return { ocm: 0.15, profit: 0.10 };
    if (edc <= 50e6) return { ocm: 0.12, profit: 0.08 };
    if (edc <= 150e6) return { ocm: 0.10, profit: 0.08 };
    return { ocm: 0.08, profit: 0.08 };
  }

  /* AACE 18R-97 Class 3 (budget authorization) accuracy band, widest case. */
  var AACE3 = { low: -0.20, high: 0.30, bestLow: -0.10, bestHigh: 0.10 };

  function quote(t, opt) {
    opt = opt || {};
    var P = prices(opt.prices);
    var C = catalog(P, { year: t.params.year, escalation: opt.escalation });
    var f = C._f;
    var lines = [], direct = 0;
    t.lines.forEach(function (ln) {
      var c = C[ln.id];
      var u = c.unitCost;
      var parts = { lab: c.lab, eqp: c.eqp, mat: c.mat };
      if (ln.id === 'bore') { u = P.boring * Math.PI / 4 * t.params.D * t.params.D * f; parts = { lab: 0, eqp: 0, mat: u }; }
      if (ln.id === 'psc') { u = (P.psc + P.pscSpan * t.params.Ls) * f; parts = { lab: 0, eqp: 0, mat: u }; }
      var amt = u * ln.qty;
      direct += amt;
      lines.push({ id: ln.id, ref: c.ref, desc: c.desc, unit: c.unit, qty: ln.qty, unitCost: u, amount: amt, group: ln.group, note: ln.note, si: c.si, parts: parts });
    });
    var osh = (opt.oshRate == null ? 0.01 : opt.oshRate) * direct;
    var mob = (opt.mobRate == null ? 0.01 : opt.mobRate) * direct;
    lines.unshift({ id: 'osh', ref: 'B.7', desc: 'Occupational safety and health program', unit: 'lot', qty: 1, unitCost: osh, amount: osh, group: 'General requirements', note: '1% of direct cost', si: true, parts: { lab: 0, eqp: 0, mat: osh } });
    lines.unshift({ id: 'mob', ref: 'B.9', desc: 'Mobilization and demobilization', unit: 'lot', qty: 1, unitCost: mob, amount: mob, group: 'General requirements', note: '1% of direct cost', si: true, parts: { lab: 0, eqp: 0, mat: mob } });
    var edc = direct + osh + mob;
    var r = indirect(edc);
    if (opt.ocm != null) r.ocm = +opt.ocm;
    if (opt.profit != null) r.profit = +opt.profit;
    var vatRate = opt.vat == null ? 0.12 : +opt.vat;
    var ocm = edc * r.ocm, profit = edc * r.profit;
    var vat = (edc + ocm + profit) * vatRate;
    var total = edc + ocm + profit + vat;
    var groups = {};
    lines.forEach(function (l) { groups[l.group] = (groups[l.group] || 0) + l.amount; });
    var lab = 0, eqp = 0, mat = 0;
    lines.forEach(function (l) { lab += l.parts.lab * l.qty; eqp += l.parts.eqp * l.qty; mat += l.parts.mat * l.qty; });
    return {
      kind: t.kind, params: t.params, geo: t.geo, lines: lines, groups: groups,
      edc: edc, ocmRate: r.ocm, profitRate: r.profit, vatRate: vatRate, ocm: ocm, profit: profit, vat: vat, total: total,
      perArea: total / t.basis.area, basis: t.basis, split: { lab: lab, eqp: eqp, mat: mat },
      band: { low: total * (1 + AACE3.low), high: total * (1 + AACE3.high) }, escalationFactor: f
    };
  }

  function estimate(p, opt) { return quote(takeoff(p), opt); }

  /* Engineering screen: where the approved budget or contract amount sits against the lean quotation. */
  function screen(total, amount) {
    var cdr = (amount - total) / total;
    var level, text;
    if (cdr > AACE3.high) { level = 'red'; text = 'Above the widest Class 3 accuracy range (+30%). Review the quantities and unit costs.'; }
    else if (cdr > AACE3.bestHigh) { level = 'amber'; text = 'Inside the Class 3 range but above +10%. Ask for the basis of the extra cost.'; }
    else if (cdr < AACE3.low) { level = 'blue'; text = 'More than 20% below the lean quotation. Check for missing scope or an unrealistic price.'; }
    else { level = 'green'; text = 'Within ±10–20% of the lean quotation.'; }
    return { cdr: cdr, level: level, text: text };
  }

  /* ---------- Statistics and machine learning ---------- */
  function mean(a) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i]; return s / a.length; }
  function sd(a) { var m = mean(a), s = 0; for (var i = 0; i < a.length; i++) s += (a[i] - m) * (a[i] - m); return Math.sqrt(s / Math.max(1, a.length - 1)); }
  function quantile(a, q) { var b = a.slice().sort(function (x, y) { return x - y; }); var i = (b.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i); return b[lo] + (b[hi] - b[lo]) * (i - lo); }

  function solve(A, b) {
    var n = b.length, M = A.map(function (r, i) { return r.concat([b[i]]); });
    for (var c = 0; c < n; c++) {
      var piv = c;
      for (var r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[piv][c])) piv = r;
      var tmp = M[c]; M[c] = M[piv]; M[piv] = tmp;
      var d = M[c][c] || 1e-12;
      for (var r2 = 0; r2 < n; r2++) if (r2 !== c) {
        var k = M[r2][c] / d;
        if (k) for (var j = c; j <= n; j++) M[r2][j] -= k * M[c][j];
      }
    }
    return M.map(function (r, i) { return r[n] / (r[i] || 1e-12); });
  }

  /* Ordinary least squares with intercept. */
  function olsFit(X, y) {
    var p = X[0].length + 1, A = [], b = [];
    for (var i = 0; i < p; i++) { A.push(new Array(p).fill(0)); b.push(0); }
    for (var r = 0; r < X.length; r++) {
      var x = [1].concat(X[r]);
      for (var i2 = 0; i2 < p; i2++) { b[i2] += x[i2] * y[r]; for (var j = 0; j < p; j++) A[i2][j] += x[i2] * x[j]; }
    }
    for (var d = 1; d < p; d++) A[d][d] += 1e-9;
    return { beta: solve(A, b) };
  }
  function olsPredict(m, x) { var s = m.beta[0]; for (var i = 0; i < x.length; i++) s += m.beta[i + 1] * x[i]; return s; }
  function olsSummary(X, y) {
    var m = olsFit(X, y), n = X.length, p = X[0].length + 1;
    var res = y.map(function (v, i) { return v - olsPredict(m, X[i]); });
    var sse = res.reduce(function (s, e) { return s + e * e; }, 0), s2 = sse / Math.max(1, n - p);
    var A = [];
    for (var i = 0; i < p; i++) A.push(new Array(p).fill(0));
    X.forEach(function (row) { var x = [1].concat(row); for (var i2 = 0; i2 < p; i2++) for (var j = 0; j < p; j++) A[i2][j] += x[i2] * x[j]; });
    var se = [];
    for (var k = 0; k < p; k++) { var e = new Array(p).fill(0); e[k] = 1; se.push(Math.sqrt(Math.max(0, s2 * solve(A, e)[k]))); }
    var ym = mean(y), sst = y.reduce(function (s, v) { return s + (v - ym) * (v - ym); }, 0);
    return { beta: m.beta, se: se, t: m.beta.map(function (b, i) { return b / (se[i] || 1e-12); }), r2: 1 - sse / sst, n: n, p: p };
  }
  function vif(X) {
    var k = X[0].length, out = [];
    for (var j = 0; j < k; j++) {
      var Xo = X.map(function (r) { return r.filter(function (_, i) { return i !== j; }); });
      var yj = X.map(function (r) { return r[j]; });
      if (!Xo[0].length) { out.push(1); continue; }
      var m = olsFit(Xo, yj), ym = mean(yj), sse = 0, sst = 0;
      yj.forEach(function (v, i) { var e = v - olsPredict(m, Xo[i]); sse += e * e; sst += (v - ym) * (v - ym); });
      out.push(1 / Math.max(1e-9, sse / sst));
    }
    return out;
  }

  /* Regularized gradient-boosted regression trees, XGBoost formulation (squared loss: g = ŷ − y, h = 1;
     gain = ½[G_L²/(H_L+λ) + G_R²/(H_R+λ) − G²/(H+λ)] − γ; leaf weight w = −G/(H+λ)). */
  function gbtFit(X, y, o) {
    o = o || {};
    var T = o.rounds || 150, eta = o.eta || 0.08, depth = o.depth || 3, lam = o.lambda == null ? 1 : o.lambda, gam = o.gamma || 0, mcw = o.minChild || 3;
    var n = X.length, k = X[0].length, base = mean(y), pred = new Array(n).fill(base), trees = [];
    var order = [];
    for (var j = 0; j < k; j++) order.push(Array.from({ length: n }, function (_, i) { return i; }).sort(function (a, b) { return X[a][j] - X[b][j]; }));
    var g = new Array(n);
    function build(idx, d) {
      var G = 0; idx.forEach(function (i) { G += g[i]; });
      var H = idx.length;
      if (d >= depth || H < 2 * mcw) return { w: -G / (H + lam) };
      var inSet = new Uint8Array(n); idx.forEach(function (i) { inSet[i] = 1; });
      var best = { gain: 0 };
      for (var j = 0; j < k; j++) {
        var GL = 0, HL = 0, ord = order[j];
        var prev = null;
        for (var t = 0; t < n; t++) {
          var i = ord[t]; if (!inSet[i]) continue;
          if (prev !== null && HL >= mcw && H - HL >= mcw && X[i][j] > X[prev][j]) {
            var GR = G - GL, HR = H - HL;
            var gain = 0.5 * (GL * GL / (HL + lam) + GR * GR / (HR + lam) - G * G / (H + lam)) - gam;
            if (gain > best.gain) best = { gain: gain, j: j, thr: (X[i][j] + X[prev][j]) / 2 };
          }
          GL += g[i]; HL += 1; prev = i;
        }
      }
      if (!(best.gain > 0)) return { w: -G / (H + lam) };
      var L = [], R = [];
      idx.forEach(function (i) { (X[i][best.j] < best.thr ? L : R).push(i); });
      return { j: best.j, thr: best.thr, gain: best.gain, l: build(L, d + 1), r: build(R, d + 1), n: H };
    }
    var all = Array.from({ length: n }, function (_, i) { return i; });
    for (var r = 0; r < T; r++) {
      for (var i = 0; i < n; i++) g[i] = pred[i] - y[i];
      var tree = build(all, 0);
      trees.push(tree);
      for (var i2 = 0; i2 < n; i2++) pred[i2] += eta * leaf(tree, X[i2]);
    }
    return { base: base, eta: eta, trees: trees, k: k };
  }
  function leaf(t, x) { while (t.w === undefined) t = x[t.j] < t.thr ? t.l : t.r; return t.w; }
  function gbtPredict(m, x) { var s = m.base; for (var i = 0; i < m.trees.length; i++) s += m.eta * leaf(m.trees[i], x); return s; }
  function gbtImportance(m) {
    var imp = new Array(m.k).fill(0);
    (function walk(ts) { ts.forEach(function f(t) { if (t.w === undefined) { imp[t.j] += t.gain; f(t.l); f(t.r); } }); })(m.trees);
    var s = imp.reduce(function (a, b) { return a + b; }, 0) || 1;
    return imp.map(function (v) { return v / s; });
  }

  /* Isolation Forest (Liu, Ting and Zhou, 2008): s(x, ψ) = 2^(−E[h(x)] / c(ψ)). */
  function cN(n) { return n <= 1 ? 0 : 2 * (Math.log(n - 1) + 0.5772156649) - 2 * (n - 1) / n; }
  function iforestFit(X, o) {
    o = o || {};
    var t = o.trees || 200, psi = Math.min(o.psi || 256, X.length), rnd = rng(o.seed || 7), lim = Math.ceil(Math.log2(Math.max(2, psi)));
    var trees = [];
    function grow(rows, d) {
      if (d >= lim || rows.length <= 1) return { size: rows.length };
      var k = X[0].length, j = Math.floor(rnd() * k), lo = Infinity, hi = -Infinity;
      rows.forEach(function (r) { lo = Math.min(lo, X[r][j]); hi = Math.max(hi, X[r][j]); });
      if (hi - lo < 1e-12) return { size: rows.length };
      var thr = lo + rnd() * (hi - lo), L = [], R = [];
      rows.forEach(function (r) { (X[r][j] < thr ? L : R).push(r); });
      return { j: j, thr: thr, l: grow(L, d + 1), r: grow(R, d + 1) };
    }
    for (var i = 0; i < t; i++) {
      var idx = Array.from({ length: X.length }, function (_, q) { return q; });
      for (var a = idx.length - 1; a > 0; a--) { var b = Math.floor(rnd() * (a + 1)); var tmp = idx[a]; idx[a] = idx[b]; idx[b] = tmp; }
      trees.push(grow(idx.slice(0, psi), 0));
    }
    return { trees: trees, c: cN(psi) };
  }
  function iforestScore(m, x) {
    var h = 0;
    m.trees.forEach(function (t) {
      var d = 0;
      while (t.size === undefined) { t = x[t.j] < t.thr ? t.l : t.r; d++; }
      h += d + cN(t.size);
    });
    return Math.pow(2, -(h / m.trees.length) / m.c);
  }

  /* Exact Shapley values with an interventional background (Lundberg and Lee, 2017). */
  function shapley(f, x, background) {
    var M = x.length, phi = new Array(M).fill(0), fact = [1];
    for (var i = 1; i <= M; i++) fact[i] = fact[i - 1] * i;
    var cache = {};
    function v(mask) {
      if (cache[mask] !== undefined) return cache[mask];
      var s = 0;
      background.forEach(function (b) {
        var z = b.slice();
        for (var j = 0; j < M; j++) if (mask & (1 << j)) z[j] = x[j];
        s += f(z);
      });
      return (cache[mask] = s / background.length);
    }
    for (var mask = 0; mask < (1 << M); mask++) {
      var size = 0; for (var j = 0; j < M; j++) if (mask & (1 << j)) size++;
      for (var j2 = 0; j2 < M; j2++) if (!(mask & (1 << j2))) {
        var w = fact[size] * fact[M - size - 1] / fact[M];
        phi[j2] += w * (v(mask | (1 << j2)) - v(mask));
      }
    }
    return { base: v(0), phi: phi };
  }

  function metrics(y, yhat) {
    var n = y.length, ym = mean(y), sse = 0, sst = 0, ape = 0;
    for (var i = 0; i < n; i++) { sse += (y[i] - yhat[i]) * (y[i] - yhat[i]); sst += (y[i] - ym) * (y[i] - ym); ape += Math.abs((y[i] - yhat[i]) / y[i]); }
    return { r2: 1 - sse / sst, rmse: Math.sqrt(sse / n), mape: 100 * ape / n };
  }

  function rng(seed) {
    var a = seed >>> 0;
    return function () { a = (a + 0x6D2B79F5) >>> 0; var t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  function gauss(r) { var u = 0, v = 0; while (u === 0) u = r(); while (v === 0) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

  /* ---------- Contract records: a few plan figures per contract, as published ---------- */
  var CSV_COLUMNS = ['id', 'kind', 'province', 'year', 'length_m', 'width_m', 'storeys', 'spans', 'span_m', 'superstructure', 'contract_cost'];

  function rowPlan(r) {
    if (r.kind === 'bridge') {
      var width = +r.width_m || 8.7;
      return { kind: 'bridge', year: +r.year || BASE_YEAR, ns: +r.spans || 1, Ls: +r.span_m || 20, Wc: Math.max(3.5, width - 2 * 0.75 - 0.5), sup: (r.superstructure || 'RCDG').toUpperCase() === 'PSCG' ? 'PSCG' : 'RCDG' };
    }
    return { kind: 'building', year: +r.year || BASE_YEAR, L: +r.length_m || 18, W: +r.width_m || 9, N: +r.storeys || 1 };
  }

  var FEATURES = {
    building: ['ln Engineering estimate', 'ln Gross floor area', 'Storeys', 'Award year'],
    bridge: ['ln Engineering estimate', 'ln Bridge length', 'Deck width', 'Spans', 'PSC girders', 'Award year']
  };
  function featuresOf(r, opt) {
    var p = rowPlan(r), e = estimate(p, opt);
    if (p.kind === 'bridge') return { est: e.total, area: e.basis.area, x: [Math.log(e.total), Math.log(e.geo.length), e.geo.width, p.ns, p.sup === 'PSCG' ? 1 : 0, p.year - 2022] };
    return { est: e.total, area: e.basis.area, x: [Math.log(e.total), Math.log(e.geo.gfa), p.N, p.year - 2022] };
  }

  /* Hybrid screen over a set of contracts of one kind: engineering ratio, LOOCV model ratio, Isolation Forest. */
  function analyze(rows, o) {
    o = o || {};
    var thr = o.threshold == null ? AACE3.high : o.threshold, cont = o.contamination == null ? 0.05 : o.contamination;
    var F = rows.map(function (r) { return featuresOf(r, o.quote); });
    var X = F.map(function (f) { return f.x; });
    var y = rows.map(function (r) { return Math.log(+r.contract_cost); });
    var n = rows.length, mlr = [], gbt = [];
    for (var i = 0; i < n; i++) {
      var Xt = X.filter(function (_, q) { return q !== i; }), yt = y.filter(function (_, q) { return q !== i; });
      mlr.push(olsPredict(olsFit(Xt, yt), X[i]));
      /* boosting starts from the engineering estimate (base margin = ln estimate) and learns the correction */
      gbt.push(X[i][0] + gbtPredict(gbtFit(Xt, yt.map(function (v, q) { return v - Xt[q][0]; }), o.gbt), X[i]));
    }
    var cost = rows.map(function (r) { return +r.contract_cost; });
    var pm = mlr.map(Math.exp), pg = gbt.map(Math.exp), pe = F.map(function (f) { return f.est; });
    /* calibration factor: median contract-to-estimate ratio of the other contracts (robust to padded ones) */
    var ratio = cost.map(function (c, q) { return c / pe[q]; });
    var kap = ratio.map(function (_, i) { return quantile(ratio.filter(function (_, q) { return q !== i; }), 0.5); });
    var pc = pe.map(function (v, q) { return v * kap[q]; });
    var resid = y.map(function (v, q) { return v - gbt[q]; });
    var Z = X.map(function (x, q) { return [Math.log(cost[q] / F[q].area), x[1], Math.log(cost[q] / pc[q]), resid[q]]; });
    var zs = Z[0].map(function (_, j) { var col = Z.map(function (z) { return z[j]; }); return { m: mean(col), s: sd(col) || 1 }; });
    Z = Z.map(function (z) { return z.map(function (v, j) { return (v - zs[j].m) / zs[j].s; }); });
    var forest = iforestFit(Z, { seed: o.seed || 11 });
    var score = Z.map(function (z) { return iforestScore(forest, z); });
    var cut = quantile(score, 1 - cont);
    var out = rows.map(function (r, q) {
      var s1 = (cost[q] - pc[q]) / pc[q] > thr;
      var s2 = (cost[q] - pg[q]) / pg[q] > thr;
      var s3 = score[q] >= cut && resid[q] > 0;
      var k = (s1 ? 1 : 0) + (s2 ? 1 : 0) + (s3 ? 1 : 0);
      return { id: r.id, cost: cost[q], est: pe[q], cal: pc[q], kappa: kap[q], mlr: pm[q], gbt: pg[q], cdrLean: (cost[q] - pe[q]) / pe[q], cdrEng: (cost[q] - pc[q]) / pc[q], cdrMl: (cost[q] - pg[q]) / pg[q], score: score[q], s1: s1, s2: s2, s3: s3, level: k >= 2 ? 'red' : k === 1 ? 'amber' : 'green' };
    });
    var full = gbtFit(X, y.map(function (v, q) { return v - X[q][0]; }), o.gbt);
    return {
      n: n, features: FEATURES[rows[0].kind === 'bridge' ? 'bridge' : 'building'], rows: out, X: X, y: y,
      kappa: quantile(ratio, 0.5),
      metrics: { engine: metrics(cost, pe), calibrated: metrics(cost, pc), mlr: metrics(cost, pm), gbt: metrics(cost, pg) },
      ols: olsSummary(X, y), vif: vif(X), importance: gbtImportance(full), model: full, olsModel: olsFit(X, y), forest: forest, zscale: zs, cut: cut
    };
  }

  /* ---------- Synthetic contracts for simulation and the demo dataset (never presented as DPWH data) ---------- */
  var PROVINCES = ['Albay', 'Camarines Norte', 'Camarines Sur', 'Catanduanes', 'Masbate', 'Sorsogon'];
  function synth(o) {
    o = o || {};
    var r = rng(o.seed || 2025), rows = [], nb = o.buildings == null ? 90 : o.buildings, nr = o.bridges == null ? 60 : o.bridges;
    var scope = o.scope || { building: 1.35, bridge: 1.20 };
    var priceSd = o.priceSd == null ? 0.06 : o.priceSd, noise = o.noise == null ? 0.10 : o.noise, pad = o.padRate == null ? 0.08 : o.padRate;
    function pick(a) { return a[Math.floor(r() * a.length)]; }
    function padding() {
      if (r() >= pad) return 0;
      if (o.delta != null) return o.delta;
      var lo = o.deltaLo == null ? 0.15 : o.deltaLo, hi = o.deltaHi == null ? 0.80 : o.deltaHi;
      return lo + r() * (hi - lo);
    }
    for (var i = 0; i < nb; i++) {
      var row = { id: 'B' + String(i + 1).padStart(3, '0'), kind: 'building', province: pick(PROVINCES), year: 2022 + Math.floor(r() * 4),
        length_m: Math.round((12 + r() * 33) * 2) / 2, width_m: pick([7, 8, 9, 9, 10, 12, 15]), storeys: pick([1, 1, 2, 2, 2, 3, 4]) };
      var e = scope.building * estimate(rowPlan(row)).total * Math.exp(priceSd * gauss(r) + noise * gauss(r));
      var d = padding();
      row.contract_cost = Math.round(e * (1 + d) / 100) * 100; row._pad = d;
      rows.push(row);
    }
    for (var k = 0; k < nr; k++) {
      var psc = r() < 0.35, span = psc ? pick([25, 30, 35, 40]) : pick([10, 12, 15, 18, 20, 20, 25]);
      var brow = { id: 'R' + String(k + 1).padStart(3, '0'), kind: 'bridge', province: pick(PROVINCES), year: 2022 + Math.floor(r() * 4),
        width_m: pick([7.7, 8.7, 8.7, 9.7, 10.7]), spans: pick([1, 1, 2, 2, 3, 4]), span_m: span, superstructure: psc ? 'PSCG' : 'RCDG' };
      var be = scope.bridge * estimate(rowPlan(brow)).total * Math.exp(priceSd * gauss(r) + noise * gauss(r));
      var bd = padding();
      brow.contract_cost = Math.round(be * (1 + bd) / 100) * 100; brow._pad = bd;
      rows.push(brow);
    }
    return rows;
  }

  /* ---------- Plans from CAD: ASCII DXF closed polylines, lines and circles ---------- */
  function parseDXF(text) {
    var L = text.split(/\r?\n/), pairs = [];
    for (var i = 0; i + 1 < L.length; i += 2) pairs.push([parseInt(L[i].trim(), 10), L[i + 1].trim()]);
    var units = 6, ents = [], inEnt = false, cur = null, sec = null;
    for (var a = 0; a < pairs.length; a++) {
      var c = pairs[a][0], v = pairs[a][1];
      if (c === 9 && v === '$INSUNITS') { for (var b = a + 1; b < Math.min(a + 4, pairs.length); b++) if (pairs[b][0] === 70) { units = +pairs[b][1]; break; } }
      if (c === 0 && v === 'SECTION') { sec = pairs[a + 1] && pairs[a + 1][1]; continue; }
      if (c === 0 && v === 'ENDSEC') { if (cur && sec === 'ENTITIES') ents.push(cur); cur = null; inEnt = false; sec = null; continue; }
      if (sec !== 'ENTITIES') continue;
      if (c === 0) {
        if (cur && cur.type === 'POLYLINE' && v === 'VERTEX') { if (!cur._v) { cur.pts = []; cur._v = true; } cur._inV = true; continue; }
        if (cur && cur.type === 'POLYLINE' && v === 'SEQEND') { ents.push(cur); cur = null; inEnt = false; continue; }
        if (cur) ents.push(cur);
        cur = { type: v, layer: '', pts: [], closed: false };
        inEnt = true;
        continue;
      }
      if (!inEnt || !cur) continue;
      if (c === 8) { if (!cur._inV) cur.layer = v; }
      else if (c === 70) { if (!cur._inV) cur.closed = cur.closed || ((+v) & 1) === 1; }
      else if (c === 10) cur.pts.push([+v, 0]);
      else if (c === 20 && cur.pts.length) cur.pts[cur.pts.length - 1][1] = +v;
      else if (c === 11) cur.p2 = [+v, 0];
      else if (c === 21 && cur.p2) cur.p2[1] = +v;
      else if (c === 40) cur.r = +v;
    }
    if (cur) ents.push(cur);
    var s = { 1: 0.0254, 2: 0.3048, 4: 0.001, 5: 0.01, 6: 1 }[units] || 1;
    function area(pts) { var A = 0; for (var i = 0; i < pts.length; i++) { var p = pts[i], q = pts[(i + 1) % pts.length]; A += p[0] * q[1] - q[0] * p[1]; } return Math.abs(A) / 2 * s * s; }
    function perim(pts, closed) { var P = 0; for (var i = 0; i < pts.length - (closed ? 0 : 1); i++) { var p = pts[i], q = pts[(i + 1) % pts.length]; P += Math.hypot(q[0] - p[0], q[1] - p[1]); } return P * s; }
    var polys = ents.filter(function (e) { return (e.type === 'LWPOLYLINE' || e.type === 'POLYLINE') && e.pts.length >= 3; });
    polys.forEach(function (e) {
      var first = e.pts[0], last = e.pts[e.pts.length - 1];
      if (!e.closed && Math.hypot(first[0] - last[0], first[1] - last[1]) < 1e-6) { e.closed = true; e.pts.pop(); }
    });
    var closed = polys.filter(function (e) { return e.closed; });
    var outlineRe = /OUTLINE|SLAB|FLOOR|BLDG|BUILDING|FOOTPRINT|DECK/i;
    var cand = closed.filter(function (e) { return outlineRe.test(e.layer); });
    if (!cand.length) cand = closed;
    cand.sort(function (a, b) { return area(b.pts) - area(a.pts); });
    var out = cand[0];
    var res = { units: units, scale: s, entities: ents.length, area: 0, perim: 0, L: 0, W: 0, nCols: 0, wallLen: 0 };
    if (out) {
      res.area = area(out.pts); res.perim = perim(out.pts, true);
      var xs = out.pts.map(function (p) { return p[0]; }), ys = out.pts.map(function (p) { return p[1]; });
      var bx = (Math.max.apply(null, xs) - Math.min.apply(null, xs)) * s, by = (Math.max.apply(null, ys) - Math.min.apply(null, ys)) * s;
      res.L = Math.max(bx, by); res.W = res.area / res.L;
    }
    var colRe = /COL/i, wallRe = /WALL|CHB|PARTITION|MASONRY/i;
    ents.forEach(function (e) {
      if (e.type === 'CIRCLE' && colRe.test(e.layer)) res.nCols++;
      else if ((e.type === 'LWPOLYLINE' || e.type === 'POLYLINE') && e.closed && e !== out) {
        var A = area(e.pts);
        if (colRe.test(e.layer) || (A >= 0.04 && A <= 1.0 && !wallRe.test(e.layer))) res.nCols++;
        else if (wallRe.test(e.layer)) res.wallLen += perim(e.pts, true) / 2;
      } else if (wallRe.test(e.layer)) {
        if (e.type === 'LINE' && e.pts.length && e.p2) res.wallLen += Math.hypot(e.p2[0] - e.pts[0][0], e.p2[1] - e.pts[0][1]) * s;
        else if (e.pts.length >= 2) res.wallLen += perim(e.pts, false);
      }
    });
    if (res.wallLen && res.perim) res.wallLen = Math.max(0, res.wallLen - res.perim);
    return res;
  }

  /* Reference plans: typical public-building and bridge configurations used as starting points. */
  var TEMPLATES = [
    { id: 'sb1', label: '1-storey, 2-classroom school building (9 × 18 m)', plan: { kind: 'building', name: '1-storey 2-classroom school building', use: 'school', L: 18, W: 9, N: 1, sx: 4.5, sy: 4.5 } },
    { id: 'sb2', label: '2-storey, 4-classroom school building (9 × 18 m)', plan: { kind: 'building', name: '2-storey 4-classroom school building', use: 'school', L: 18, W: 9, N: 2, sx: 4.5, sy: 4.5 } },
    { id: 'sb3', label: '3-storey, 9-classroom school building (9 × 27 m)', plan: { kind: 'building', name: '3-storey 9-classroom school building', use: 'school', L: 27, W: 9, N: 3, sx: 4.5, sy: 4.5, col: 0.45, B: 1.9, tf: 0.45 } },
    { id: 'mpb', label: 'Multi-purpose hall / evacuation center (15 × 30 m)', plan: { kind: 'building', name: 'Multi-purpose evacuation center', use: 'mpb', L: 30, W: 15, N: 1, h: 4.5, sx: 6, sy: 7.5, col: 0.40, wallDensity: 0.05, pitch: 15 } },
    { id: 'hc2', label: '2-storey health center / office (10 × 20 m)', plan: { kind: 'building', name: '2-storey health center', use: 'health', L: 20, W: 10, N: 2, sx: 5, sy: 5, wallDensity: 0.30, fixtures: 10 } },
    { id: 'br1', label: 'Single-span 15 m RCDG bridge, two lanes', plan: { kind: 'bridge', name: 'Single-span RCDG bridge', ns: 1, Ls: 15, sup: 'RCDG', Ha: 5, water: false, riprap: 80 } },
    { id: 'br2', label: 'Two-span 2 × 20 m RCDG bridge, two lanes', plan: { kind: 'bridge', name: 'Two-span RCDG bridge', ns: 2, Ls: 20, sup: 'RCDG' } },
    { id: 'br3', label: 'Three-span 3 × 30 m PSCG bridge, two lanes', plan: { kind: 'bridge', name: 'Three-span PSCG bridge', ns: 3, Ls: 30, sup: 'PSCG', Ha: 7, Hp: 9, pilesA: 8, pilesP: 8, Lp: 22, riprap: 200 } }
  ];

  function fmt1(v) { return (Math.round(v * 10) / 10).toLocaleString('en-PH'); }
  function fmt2(v) { return (Math.round(v * 100) / 100).toFixed(2); }

  return {
    VERSION: VERSION, BASE_YEAR: BASE_YEAR, BASE_PRICES: BASE_PRICES, MIX: MIX, RHO: RHO, LAP: LAP, AACE3: AACE3,
    BUILDING_DEFAULTS: BUILDING_DEFAULTS, BRIDGE_DEFAULTS: BRIDGE_DEFAULTS, TEMPLATES: TEMPLATES, PROVINCES: PROVINCES,
    CSV_COLUMNS: CSV_COLUMNS, FEATURES: FEATURES,
    prices: prices, catalog: catalog, takeoff: takeoff, takeoffBuilding: takeoffBuilding, takeoffBridge: takeoffBridge,
    indirect: indirect, quote: quote, estimate: estimate, screen: screen,
    olsFit: olsFit, olsPredict: olsPredict, olsSummary: olsSummary, vif: vif,
    gbtFit: gbtFit, gbtPredict: gbtPredict, gbtImportance: gbtImportance,
    iforestFit: iforestFit, iforestScore: iforestScore, shapley: shapley, metrics: metrics,
    rowPlan: rowPlan, featuresOf: featuresOf, analyze: analyze, synth: synth, parseDXF: parseDXF,
    rng: rng, mean: mean, sd: sd, quantile: quantile
  };
});
