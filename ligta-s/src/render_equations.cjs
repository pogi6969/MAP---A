// Pre-renders the model's equations to inline SVG with MathJax 3 (run once; output is src/equations.json).
// The website then shows typeset mathematics with no script and no network.
//   npm install mathjax-full@3.2.2   (in any scratch folder), then
//   MATHJAX_DIR=/path/to/node_modules/mathjax-full node src/render_equations.cjs
// Every equation is the paper's own (Sections 2 and 3 of "Safe Shelter, Open Schools").
const path = require('path'), fs = require('fs');
const MJ = process.env.MATHJAX_DIR || 'mathjax-full';
const { mathjax } = require(MJ + '/js/mathjax.js');
const { TeX } = require(MJ + '/js/input/tex.js');
const { AllPackages } = require(MJ + '/js/input/tex/AllPackages.js');
const { SVG } = require(MJ + '/js/output/svg.js');
const { liteAdaptor } = require(MJ + '/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require(MJ + '/js/handlers/html.js');
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const doc = mathjax.document('', { InputJax: new TeX({ packages: AllPackages }), OutputJax: new SVG({ fontCache: 'local' }) });

// [TeX, words a screen reader says]
const EQ = {
  scenario: [String.raw`\sigma = (Z_\sigma,\,X_\sigma),\qquad G_\sigma = (N,\;E \setminus X_\sigma)`,
    'A hazard scenario sigma is a set of active hazard zones and a set of closed roads; the open road graph drops the closed roads.'],
  demand: [String.raw`D_a(\sigma) = P_a\cdot\mathbf{1}\big[\zeta_a \cap Z_\sigma \neq \varnothing\big]`,
    'An origin evacuates its whole population when it lies in an active hazard zone, and nobody otherwise.'],
  capacity: [String.raw`C(F) = \left\lfloor \frac{F}{3.5} \right\rfloor,\qquad q = C(63) = 18`,
    'A floor area of F square meters holds F divided by 3.5, rounded down; a 63 square meter classroom holds 18.'],
  tiers: [String.raw`c^{0}_s = C\big(F^{ec}_s\big),\quad c^{1}_s = C\big(F^{open}_s\big),\quad c^{2}_s = q\,k_s`,
    'Each shelter splits into three tiers: non-school space, school open space, and classrooms at 18 per room.'],
  plan: [String.raw`\sum_{s,\iota} x_{aV,s\iota} \le V_a(\sigma),\qquad \sum_{a,\kappa} x_{a\kappa,s\iota} \le c^{\iota}_s`,
    'A plan places no more vulnerable persons than an origin has, and no more persons in a tier than it holds.'],
  lex: [String.raw`\max F_V \;\succ\; \max F \;\succ\; \min Y \;\succ\; \min O \;\succ\; \min \Theta`,
    'Lexicographic order: most vulnerable placed, then most persons placed, then fewest in classrooms, then fewest in school open spaces, then fewest person-minutes of travel.'],
  penalties: [String.raw`M_O = D\,T_{\max} + 1,\qquad M_Y = D\,(M_O + T_{\max}) + 1`,
    'The penalty weights that turn the lexicographic order into one minimum-cost flow.'],
  vector: [String.raw`\mathbf{c}(a,s,\iota) = \big(\,\mathbf{1}[\iota = 2],\; \mathbf{1}[\iota = 1],\; T_\sigma(a,s)\,\big)`,
    'In the app each trip costs a vector: one if it ends in a classroom, one if it ends in a school open space, and its minutes, compared in that order.'],
  rooms: [String.raw`K_s = \left\lceil \frac{y_s}{q} \right\rceil,\qquad L = \sum_s K_s\,\ell_s,\qquad \text{classroom-days} = K\,d`,
    'Classrooms closed at a school are its classroom evacuees over 18, rounded up; learners displaced add up the learners of those rooms; classroom-days multiply by the stay.'],
  packing: [String.raw`K^{*} \;\le\; K(x) \;\le\; K^{*} + m - 1`,
    'Packing closes at most one classroom more than the true minimum for each school in use beyond the first.'],
  monotone: [String.raw`\sigma \preceq \sigma' \;\Longrightarrow\; Y^{*}(\sigma) \le Y^{*}(\sigma')`,
    'A higher alert level never frees classrooms.'],
  expanded: [String.raw`(v,t)\;\xrightarrow{\;u_e\;}\;(w,\,t+\tau_e),\qquad (v,t)\;\xrightarrow{\;\infty\;}\;(v,\,t+1)`,
    'In the time-expanded network a road moves up to its capacity each minute and takes its travel time; anyone may wait in place.'],
  clearance: [String.raw`T^{*}_\sigma = \min\{\, T \ge 0 : F_\sigma(T) = D' \,\}`,
    'The clearance time is the first minute by which everyone the plan moves can be inside a shelter.'],
  lowerbound: [String.raw`T^{*}_\sigma \;\ge\; \max\Big\{\, \tau_{\min} - 1 + \Big\lceil \frac{D'}{c} \Big\rceil,\;\; \max_{a} \min_{s} T_\sigma(a, s) \,\Big\}`,
    'Lower bound: the shortest trip minus one plus the evacuees over the static flow rate, rounded up, and never below the longest nearest-shelter trip.'],
  closure: [String.raw`\Delta_B = T^{*}_{\sigma + B} - T^{*}_{\sigma} \;\ge\; 0`,
    'Closing a set of roads B never shortens the clearance time.'],
  siting: [String.raw`f(S) = \Phi_\theta(E \cup S) - \Phi_\theta(E)`,
    'The siting gain of new centers S is how many more evacuees can be sheltered outside classrooms within theta minutes.'],
  submod: [String.raw`f(S \cup \{j\}) - f(S) \;\ge\; f(T \cup \{j\}) - f(T),\quad S \subseteq T`,
    'Submodular: a new site adds at least as much to a smaller set of sites as to a larger one.'],
  greedy: [String.raw`f(S_g) \;\ge\; \Big[1 - \Big(1 - \frac{1}{k}\Big)^{k}\Big] f(S^{\mathrm{opt}}) \;\ge\; 0.632\, f(S^{\mathrm{opt}})`,
    'The greedy choice of k sites reaches at least 1 minus (1 minus 1 over k) to the k, and so at least 63.2 percent, of the best possible gain.'],
  sphere: [String.raw`\frac{7\,\mathrm{m} \times 9\,\mathrm{m}}{3.5\,\mathrm{m}^2\ \text{per person}} = 18\ \text{evacuees per classroom}`,
    'Seven meters by nine meters, at 3.5 square meters per person, is 18 evacuees per classroom.']
};
const out = {};
for (const [k, [tex, label]] of Object.entries(EQ)) {
  const node = doc.convert(tex, { display: true });
  let svg = adaptor.innerHTML(node);
  // one role and label per svg; the TeX stays in a data attribute for anyone who wants it
  svg = svg.replace(/ role="img"/g, '').replace(/ focusable="false"/g, '').replace(/ aria-hidden="true"/g, '');
  svg = svg.replace(/<svg /, '<svg role="img" focusable="false" aria-label="' + label.replace(/"/g, '&quot;') + '" ');
  // MathJax ids restart in every conversion: make them unique per equation
  svg = svg.replace(/MJX-(\d+)-/g, 'MJX-' + k + '-$1-');
  out[k] = { tex, label, svg };
}
fs.writeFileSync(path.join(__dirname, 'equations.json'), JSON.stringify(out, null, 1));
console.log('wrote', Object.keys(out).length, 'equations,', JSON.stringify(out).length, 'bytes');
