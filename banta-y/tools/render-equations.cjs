// Pre-renders the model's equations to inline SVG with MathJax 3, so the website needs no
// math library at run time and the equations show offline. Output: src/equations.json.
//   npm install mathjax-full@3.2.2   (in any folder), then
//   MATHJAX_DIR=/path/to/node_modules/mathjax-full node tools/render-equations.cjs
const path = require("path"), fs = require("fs");
const MJ = process.env.MATHJAX_DIR || "mathjax-full";
const { mathjax } = require(MJ + "/js/mathjax.js");
const { TeX } = require(MJ + "/js/input/tex.js");
const { AllPackages } = require(MJ + "/js/input/tex/AllPackages.js");
const { SVG } = require(MJ + "/js/output/svg.js");
const { liteAdaptor } = require(MJ + "/js/adaptors/liteAdaptor.js");
const { RegisterHTMLHandler } = require(MJ + "/js/handlers/html.js");
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const doc = mathjax.document("", { InputJax: new TeX({ packages: AllPackages }), OutputJax: new SVG({ fontCache: "local" }) });

// Each equation is a list of parts [TeX, spoken text]; parts wrap onto new lines on narrow screens.
const EQ = {
  movement: [
    [String.raw`p_{ii} = 1-\omega_i`, "p i i equals 1 minus omega i, the share of the day spent at home"],
    [String.raw`p_{ij} = \omega_i\,\frac{A_j\,e^{-\beta T_{ij}}}{\sum_{k\neq i} A_k\,e^{-\beta T_{ik}}}`, "p i j equals omega i times A j e to the minus beta T i j, divided by the sum over k not equal to i of A k e to the minus beta T i k"],
    [String.raw`\tilde N_j = \sum_k p_{kj}\,N_k`, "N tilde j, the people present in place j, equals the sum over k of p k j times N k"]
  ],
  ngm: [
    [String.raw`M = \kappa\, D_N P\, W P^{\top}`, "M equals kappa times D N times P times W times P transpose"],
    [String.raw`W = \mathrm{diag}\Big(\frac{V_j}{\tilde N_j^{\,2}}\Big)`, "W is the diagonal matrix of V j over N tilde j squared"],
    [String.raw`\kappa = \frac{a^2 b c\,\nu}{\mu_v(\nu+\mu_v)(\gamma+\mu_h)}`, "kappa equals a squared b c nu over mu v times nu plus mu v times gamma plus mu h"]
  ],
  r0: [
    [String.raw`\mathcal{R}_0^2 = \lambda_{\max}(S)`, "R naught squared equals the largest eigenvalue of S"],
    [String.raw`S = \kappa\,D_N^{1/2} P W P^{\top} D_N^{1/2} = \kappa\sum_j w_j\,q_j q_j^{\top}`, "S equals kappa D N to the one half P W P transpose D N to the one half, equal to kappa times the sum over j of w j q j q j transpose"]
  ],
  sandwich: [
    [String.raw`\min_i \mathcal{R}_i \;\le\; \mathcal{R}_0^2 \;\le\; \max_i \mathcal{R}_i`, "the smallest local exposure number is at most R naught squared, which is at most the largest local exposure number"],
    [String.raw`\mathcal{R}_i = \kappa\sum_j p_{ij}\,m_j`, "R i equals kappa times the sum over j of p i j m j"],
    [String.raw`\mathcal{R}_0^2 \;\ge\; \kappa\,\frac{V}{N}`, "R naught squared is at least kappa times total mosquitoes over total people"]
  ],
  shares: [
    [String.raw`s_j = \frac{\kappa\,w_j\,(q_j^{\top}v)^2}{\mathcal{R}_0^2},\quad \sum_j s_j = 1`, "s j equals kappa w j times q j dot v squared, over R naught squared; the shares add up to one"],
    [String.raw`\frac{\partial\,\mathcal{R}_0^2}{\partial u_j} = -\kappa\,w_j\,(q_j^{\top}v)^2`, "the derivative of R naught squared with respect to u j equals minus kappa w j times q j dot v squared"]
  ],
  program: [
    [String.raw`\min_{u}\ \sum_j c_j u_j`, "minimize the sum of c j u j"],
    [String.raw`\text{subject to}\quad r^2 I - S(u) \succeq 0,\quad 0 \le u_j \le \bar u_j`, "subject to r squared I minus S of u positive semidefinite, and u j between 0 and u bar j"]
  ],
  certificate: [
    [String.raw`\kappa \sum_j p_{ij}\,m_j\,(1-u_j) \;\le\; r^2 \ \text{ for every } i`, "kappa times the sum over j of p i j m j times 1 minus u j is at most r squared for every i"],
    [String.raw`\Longrightarrow\quad \mathcal{R}_0(u) \le r`, "implies R naught of u is at most r"]
  ],
  barrier: [
    [String.raw`\phi_t(u) = t\,c^{\top}u - \log\det\big(r^2 I - S(u)\big)`, "phi t of u equals t c transpose u minus log det of r squared I minus S of u"],
    [String.raw`-\sum_j \log u_j - \sum_j \log(\bar u_j - u_j)`, "minus the sum of log u j minus the sum of log of u bar j minus u j"]
  ],
  dual: [
    [String.raw`g(Z) = \sum_j \bar u_j \min\{0,\ c_j - \kappa w_j\, q_j^{\top} Z q_j\}`, "g of Z equals the sum over j of u bar j times the minimum of 0 and c j minus kappa w j q j transpose Z q j"],
    [String.raw`-\ \mathrm{tr}\big(Z(r^2 I - S(0))\big) \;\le\; \text{least cost}`, "minus the trace of Z times r squared I minus S of 0, which is at most the least cost"]
  ],
  inversion: [
    [String.raw`y = P\,z`, "y equals P z"],
    [String.raw`\|\hat z - z\|_{\infty} \;\le\; \frac{\|\varepsilon\|_{\infty}}{\min_i\,(2p_{ii}-1)}`, "the largest error in z hat is at most the largest error in the rates divided by the smallest value of 2 p i i minus 1"]
  ],
  cusum: [
    [String.raw`S_t = \max\{0,\ S_{t-1} + x_t - k_t\}`, "S t equals the maximum of 0 and S t minus 1 plus x t minus k t"],
    [String.raw`k_t = \frac{(\theta-1)\,\mu_t}{\ln\theta}`, "k t equals theta minus 1 times mu t over the natural log of theta"],
    [String.raw`\text{alarm when } S_t \ge h`, "alarm when S t reaches h"]
  ],
  arl: [
    [String.raw`\text{alarm by week } \tau + \lceil h/\delta \rceil - 1`, "alarm by week tau plus the ceiling of h over delta minus 1"],
    [String.raw`\mathrm{ARL} = \big((I-Q)^{-1}\mathbf{1}\big)_0`, "average run length equals the first entry of I minus Q inverse times the vector of ones"]
  ],
  season: [
    [String.raw`\mathcal{R}_0^2(u;\varsigma) = \varsigma\,\mathcal{R}_0^2(u;1)`, "R naught squared in season sigma equals sigma times R naught squared in the reference season"]
  ],
  threshold: [
    [String.raw`\kappa = 0.584`, "kappa equals 0.584"],
    [String.raw`\mathcal{R}_0 = 1 \text{ at } m = 1/\kappa \approx 1.71`, "R naught equals 1 at m equal to 1 over kappa, about 1.71 mosquitoes per person"]
  ]
};

const out = {};
const esc = (t) => t.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
for (const [k, parts] of Object.entries(EQ)) {
  out[k] = parts.map(([tex, say]) => {
    const node = doc.convert(tex, { display: true });
    let svg = adaptor.innerHTML(node);
    svg = svg.replace(/ role="img"/g, "").replace(/ focusable="false"/g, "").replace(/ aria-hidden="true"/g, "");
    svg = svg.replace(/<svg /, '<svg role="img" aria-label="' + esc(say) + '" focusable="false" ');
    return { tex, say, svg };
  });
}
const dest = path.join(__dirname, "..", "src", "equations.json");
fs.writeFileSync(dest, JSON.stringify(out, null, 1));
console.log("wrote", dest, Object.keys(out).length, "equations");
