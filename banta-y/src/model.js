/* BANTA-Y model, version 1.
   A residence-time (Lagrangian) host-vector model of dengue on a network of barangays:
   the reproduction number R0 and its place-by-place decomposition, least-cost vector
   control (a convex program solved by a barrier interior-point method with a certified
   dual lower bound, plus a linear-program certificate), residence-to-place inversion of
   case counts, and a Poisson CUSUM early-warning rule.

   This is a JavaScript port of denguemodel.py from the research
   "Where People Go, Dengue Goes" (research/where-people-go-dengue/code). The same file is
   inlined into the app and the website by tools/build.mjs, and tests/verify.mjs checks it
   against the Python results in results.json. No external code is used. */
var BantayModel = (function () {
  "use strict";

  /* ------------------------------------------------------------------ small linear algebra */

  function zeros(n, m) {
    var A = new Array(n);
    for (var i = 0; i < n; i++) { A[i] = new Array(m); for (var j = 0; j < m; j++) A[i][j] = 0; }
    return A;
  }
  function eye(n) { var A = zeros(n, n); for (var i = 0; i < n; i++) A[i][i] = 1; return A; }
  function copyM(A) { return A.map(function (r) { return r.slice(); }); }
  function dot(a, b) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }
  function matVec(A, x) { return A.map(function (r) { return dot(r, x); }); }
  function matTVec(A, x) {
    var n = A.length, m = A[0].length, y = new Array(m).fill(0);
    for (var i = 0; i < n; i++) for (var j = 0; j < m; j++) y[j] += A[i][j] * x[i];
    return y;
  }
  function sum(a) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i]; return s; }

  /* Cholesky factor L (lower) of a symmetric matrix; null when it is not positive definite. */
  function cholesky(A) {
    var n = A.length, L = zeros(n, n);
    for (var j = 0; j < n; j++) {
      var d = A[j][j];
      for (var k = 0; k < j; k++) d -= L[j][k] * L[j][k];
      if (!(d > 0) || !isFinite(d)) return null;
      var ljj = Math.sqrt(d);
      L[j][j] = ljj;
      for (var i = j + 1; i < n; i++) {
        var s = A[i][j];
        for (var k2 = 0; k2 < j; k2++) s -= L[i][k2] * L[j][k2];
        L[i][j] = s / ljj;
      }
    }
    return L;
  }
  function forwardSub(L, b) {
    var n = L.length, x = new Array(n);
    for (var i = 0; i < n; i++) {
      var s = b[i];
      for (var k = 0; k < i; k++) s -= L[i][k] * x[k];
      x[i] = s / L[i][i];
    }
    return x;
  }
  function backSubT(L, b) {           /* solves L^T x = b */
    var n = L.length, x = new Array(n);
    for (var i = n - 1; i >= 0; i--) {
      var s = b[i];
      for (var k = i + 1; k < n; k++) s -= L[k][i] * x[k];
      x[i] = s / L[i][i];
    }
    return x;
  }
  function cholSolve(L, b) { return backSubT(L, forwardSub(L, b)); }
  function cholInverse(L) {            /* (L L^T)^-1 */
    var n = L.length, Z = zeros(n, n);
    for (var j = 0; j < n; j++) {
      var e = new Array(n).fill(0); e[j] = 1;
      var col = cholSolve(L, e);
      for (var i = 0; i < n; i++) Z[i][j] = col[i];
    }
    for (var a = 0; a < n; a++) for (var b2 = a + 1; b2 < n; b2++) {
      var v = (Z[a][b2] + Z[b2][a]) / 2; Z[a][b2] = v; Z[b2][a] = v;
    }
    return Z;
  }
  /* Gaussian elimination with partial pivoting (fallback solver). */
  function gaussSolve(A0, b0) {
    var n = A0.length, A = copyM(A0), b = b0.slice();
    for (var c = 0; c < n; c++) {
      var p = c, best = Math.abs(A[c][c]);
      for (var r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > best) { best = Math.abs(A[r][c]); p = r; }
      if (best === 0) return null;
      if (p !== c) { var t = A[p]; A[p] = A[c]; A[c] = t; var tb = b[p]; b[p] = b[c]; b[c] = tb; }
      for (var r2 = c + 1; r2 < n; r2++) {
        var f = A[r2][c] / A[c][c];
        if (f === 0) continue;
        for (var k = c; k < n; k++) A[r2][k] -= f * A[c][k];
        b[r2] -= f * b[c];
      }
    }
    var x = new Array(n);
    for (var i = n - 1; i >= 0; i--) {
      var s = b[i];
      for (var k2 = i + 1; k2 < n; k2++) s -= A[i][k2] * x[k2];
      x[i] = s / A[i][i];
    }
    return x;
  }
  /* Least squares min ||A x - b|| by Householder QR (A is m x n, m >= n, full column rank). */
  function lstsq(A0, b0) {
    var m = A0.length, n = A0[0].length, A = copyM(A0), b = b0.slice();
    for (var k = 0; k < n; k++) {
      var norm = 0;
      for (var i = k; i < m; i++) norm += A[i][k] * A[i][k];
      norm = Math.sqrt(norm);
      if (norm === 0) continue;
      var alpha = A[k][k] > 0 ? -norm : norm;
      var v = new Array(m).fill(0);
      v[k] = A[k][k] - alpha;
      for (var i2 = k + 1; i2 < m; i2++) v[i2] = A[i2][k];
      var vv = 0;
      for (var i3 = k; i3 < m; i3++) vv += v[i3] * v[i3];
      if (vv === 0) continue;
      for (var j = k; j < n; j++) {
        var s = 0;
        for (var i4 = k; i4 < m; i4++) s += v[i4] * A[i4][j];
        s = 2 * s / vv;
        for (var i5 = k; i5 < m; i5++) A[i5][j] -= s * v[i5];
      }
      var sb = 0;
      for (var i6 = k; i6 < m; i6++) sb += v[i6] * b[i6];
      sb = 2 * sb / vv;
      for (var i7 = k; i7 < m; i7++) b[i7] -= sb * v[i7];
    }
    var x = new Array(n);
    for (var r = n - 1; r >= 0; r--) {
      var t = b[r];
      for (var c = r + 1; c < n; c++) t -= A[r][c] * x[c];
      x[r] = A[r][r] === 0 ? 0 : t / A[r][r];
    }
    return x;
  }

  /* Cyclic Jacobi eigen-solver for a symmetric matrix.
     Returns eigenvalues in ascending order and the matching unit eigenvectors as columns. */
  function jacobiEigen(S) {
    var n = S.length, A = copyM(S), V = eye(n), sweep, p, q, k;
    var total = 0;
    for (p = 0; p < n; p++) for (q = 0; q < n; q++) total += A[p][q] * A[p][q];
    for (sweep = 0; sweep < 100; sweep++) {
      var off = 0;
      for (p = 0; p < n; p++) for (q = p + 1; q < n; q++) off += A[p][q] * A[p][q];
      if (off <= 1e-32 * total || off === 0) break;
      for (p = 0; p < n - 1; p++) {
        for (q = p + 1; q < n; q++) {
          var apq = A[p][q];
          if (apq === 0) continue;
          var theta = (A[q][q] - A[p][p]) / (2 * apq);
          var t = (theta >= 0 ? 1 : -1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
          if (!isFinite(theta)) t = 0;
          var c = 1 / Math.sqrt(t * t + 1), s = t * c;
          for (k = 0; k < n; k++) {
            var akp = A[k][p], akq = A[k][q];
            A[k][p] = c * akp - s * akq;
            A[k][q] = s * akp + c * akq;
          }
          for (k = 0; k < n; k++) {
            var apk = A[p][k], aqk = A[q][k];
            A[p][k] = c * apk - s * aqk;
            A[q][k] = s * apk + c * aqk;
          }
          A[p][q] = 0; A[q][p] = 0;
          for (k = 0; k < n; k++) {
            var vkp = V[k][p], vkq = V[k][q];
            V[k][p] = c * vkp - s * vkq;
            V[k][q] = s * vkp + c * vkq;
          }
        }
      }
    }
    var idx = [];
    for (p = 0; p < n; p++) idx.push(p);
    idx.sort(function (x, y) { return A[x][x] - A[y][y]; });
    return {
      values: idx.map(function (i) { return A[i][i]; }),
      vectors: V.map(function (row) { return idx.map(function (i) { return row[i]; }); }),
      sweeps: sweep
    };
  }

  /* ------------------------------------------------------------------ parameters */

  var DEFAULT_PARAMS = {
    a: 0.29,          // bites per mosquito per day
    b: 0.5,           // mosquito-to-human transmission probability per bite
    c: 0.5,           // human-to-mosquito transmission probability per bite
    mosquitoLife: 10, // days (mu_v = 1/10)
    eip: 8,           // extrinsic incubation period, days (nu = 1/8)
    infectious: 5,    // human infectious period, days (gamma = 1/5)
    humanLife: 70     // years (mu_h = 1/(70*365))
  };

  function rates(par) {
    par = par || DEFAULT_PARAMS;
    return {
      a: par.a, b: par.b, c: par.c,
      muV: 1 / par.mosquitoLife, nu: 1 / par.eip,
      gamma: 1 / par.infectious, muH: 1 / (par.humanLife * 365)
    };
  }

  /* Equation (8): kappa = a^2 b c nu / (mu_v (nu + mu_v) (gamma + mu_h)). */
  function kappa(par) {
    var r = rates(par);
    return r.a * r.a * r.b * r.c * r.nu / (r.muV * (r.nu + r.muV) * (r.gamma + r.muH));
  }

  /* ------------------------------------------------------------------ mobility */

  /* Travel minutes from positions in km: t0 + distance / speed (km per minute). */
  function travelFromPositions(pos, t0, speed) {
    var n = pos.length, T = zeros(n, n);
    for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) {
      var dx = pos[i][0] - pos[j][0], dy = pos[i][1] - pos[j][1];
      T[i][j] = t0 + Math.sqrt(dx * dx + dy * dy) / speed;
    }
    return T;
  }

  /* Definition 3: p_ii = 1 - omega_i; p_ij = omega_i * pi_ij for j != i with
     pi_ij proportional to attract_j * exp(-beta * travel_ij). */
  function residenceTimeMatrix(omega, attract, travel, beta) {
    var n = omega.length, P = zeros(n, n);
    for (var i = 0; i < n; i++) {
      var w = new Array(n), tot = 0;
      for (var j = 0; j < n; j++) {
        w[j] = j === i ? 0 : attract[j] * Math.exp(-beta * travel[i][j]);
        tot += w[j];
      }
      P[i][i] = 1 - omega[i];
      if (tot > 0) { for (var j2 = 0; j2 < n; j2++) P[i][j2] += omega[i] * w[j2] / tot; }
      else P[i][i] = 1;
    }
    return P;
  }

  /* N~_j = sum_k p_kj N_k: average number of people present in place j. */
  function presentPopulation(P, N) { return matTVec(P, N); }

  /* ------------------------------------------------------------------ reproduction number */

  function keepFactor(n, u) { var k = new Array(n); for (var i = 0; i < n; i++) k[i] = u ? 1 - u[i] : 1; return k; }

  function weights(P, N, V, u) {
    var Nt = presentPopulation(P, N), keep = keepFactor(V.length, u);
    return V.map(function (v, j) { return keep[j] * v / (Nt[j] * Nt[j]); });
  }

  /* Q = D_N^1/2 P: row i scaled by sqrt(N_i); column j is q_j. */
  function qMatrix(P, N) { return P.map(function (row, i) { var s = Math.sqrt(N[i]); return row.map(function (p) { return s * p; }); }); }

  /* S = kappa Q W Q^T, symmetric and similar to M = kappa D_N P W P^T. */
  function symmetricMatrix(P, N, V, k, u) {
    var n = N.length, W = weights(P, N, V, u), Q = qMatrix(P, N), S = zeros(n, n);
    for (var i = 0; i < n; i++) for (var j = i; j < n; j++) {
      var s = 0;
      for (var l = 0; l < n; l++) s += Q[i][l] * W[l] * Q[j][l];
      S[i][j] = k * s; S[j][i] = k * s;
    }
    return S;
  }

  /* M = kappa D_N P W P^T (not symmetric), for display. */
  function hostHostMatrix(P, N, V, k, u) {
    var n = N.length, W = weights(P, N, V, u), M = zeros(n, n);
    for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) {
      var s = 0;
      for (var l = 0; l < n; l++) s += P[i][l] * W[l] * P[j][l];
      M[i][j] = k * N[i] * s;
    }
    return M;
  }

  function r0Squared(P, N, V, k, u) {
    var e = jacobiEigen(symmetricMatrix(P, N, V, k, u));
    return e.values[e.values.length - 1];
  }
  function r0(P, N, V, k, u) { return Math.sqrt(Math.max(0, r0Squared(P, N, V, k, u))); }

  /* R_i = kappa sum_j p_ij (1 - u_j) m_j with m_j = V_j / N~_j. */
  function localNumbers(P, N, V, k, u) {
    var Nt = presentPopulation(P, N), keep = keepFactor(V.length, u);
    var m = V.map(function (v, j) { return keep[j] * v / Nt[j]; });
    return matVec(P, m).map(function (x) { return k * x; });
  }

  function topEigen(P, N, V, k, u) {
    var e = jacobiEigen(symmetricMatrix(P, N, V, k, u));
    var n = N.length, v = e.vectors.map(function (r) { return r[n - 1]; });
    if (sum(v) < 0) v = v.map(function (x) { return -x; });
    var gap = n > 1 ? e.values[n - 1] - e.values[n - 2] : Infinity;
    return { lambda: e.values[n - 1], v: v, gap: gap, values: e.values };
  }

  /* Proposition 6: share of R0^2 carried by place j, s_j = kappa w_j (q_j . v)^2 / lambda. */
  function placeShares(P, N, V, k, u) {
    var te = topEigen(P, N, V, k, u), W = weights(P, N, V, u), Q = qMatrix(P, N);
    var proj = matTVec(Q, te.v);
    var contrib = W.map(function (w, j) { return k * w * proj[j] * proj[j]; });
    return { shares: contrib.map(function (c) { return c / te.lambda; }), contrib: contrib, lambda: te.lambda, v: te.v, gap: te.gap };
  }

  /* d R0^2 / d u_j = -kappa (V_j / N~_j^2) (q_j . v)^2 at u. */
  function gradient(P, N, V, k, u) {
    var te = topEigen(P, N, V, k, u), Nt = presentPopulation(P, N), Q = qMatrix(P, N);
    var proj = matTVec(Q, te.v);
    return V.map(function (v, j) { return -k * (v / (Nt[j] * Nt[j])) * proj[j] * proj[j]; });
  }

  /* Residence of cases in the growth phase: Perron vector of M = D_N^1/2 v, normalised. */
  function caseShare(P, N, V, k, u) {
    var te = topEigen(P, N, V, k, u);
    var x = te.v.map(function (vi, i) { return Math.abs(Math.sqrt(N[i]) * vi); });
    var s = sum(x);
    return x.map(function (xi) { return xi / s; });
  }

  /* Everything the Transmission screen shows. */
  function analyse(net) {
    var P = net.P, N = net.N, V = net.V, k = net.kappa;
    var n = N.length;
    var Nt = presentPopulation(P, N);
    var m = V.map(function (v, j) { return v / Nt[j]; });
    var R = localNumbers(P, N, V, k);
    var sh = placeShares(P, N, V, k);
    var r2 = sh.lambda;
    var Ntot = sum(N), Vtot = sum(V);
    var hom2 = k * Vtot / Ntot;
    var iso2 = V.map(function (v, i) { return k * v / N[i]; });
    var grad = sh.contrib.map(function (c) { return -c; });
    var cs = caseShare(P, N, V, k);
    var hot = grad.map(function (g, j) { return net.cost ? -g / net.cost[j] : NaN; });
    return {
      n: n, present: Nt, m: m, R_local: R, r0_sq: r2, r0: Math.sqrt(Math.max(0, r2)),
      hom_r0: Math.sqrt(hom2), iso_r0: iso2.map(Math.sqrt),
      r0_no_movement: Math.sqrt(Math.max.apply(null, iso2)),
      shares: sh.shares, case_share: cs, grad: grad, hotspot_per_teamday: hot,
      resident_share: N.map(function (x) { return x / Ntot; }),
      minR: Math.min.apply(null, R), maxR: Math.max.apply(null, R), gap: sh.gap
    };
  }

  /* ------------------------------------------------------------------ strategies */

  function costOf(cost, u) { return dot(cost, u); }

  /* Smallest common u with R0^2 <= r2 (bisection; R0^2 decreases in u). */
  function uniformControl(P, N, V, k, ubarScalar, r2, tol) {
    tol = tol || 1e-10;
    var n = V.length;
    var full = function (x) { return new Array(n).fill(x); };
    if (r0Squared(P, N, V, k) <= r2) return full(0);
    if (r0Squared(P, N, V, k, full(ubarScalar)) > r2) return null;
    var lo = 0, hi = ubarScalar;
    while (hi - lo > tol) {
      var mid = (lo + hi) / 2;
      if (r0Squared(P, N, V, k, full(mid)) <= r2) hi = mid; else lo = mid;
    }
    return full(hi);
  }

  /* Smallest t with u = min(t * direction, ubar) meeting R0^2 <= r2. */
  function scaledControl(P, N, V, k, direction, ubar, r2, tol) {
    tol = tol || 1e-10;
    var n = V.length;
    var at = function (t) { return direction.map(function (d, j) { return Math.min(t * d, ubar[j]); }); };
    if (r0Squared(P, N, V, k) <= r2) return new Array(n).fill(0);
    var tHi = 1;
    while (r0Squared(P, N, V, k, at(tHi)) > r2) {
      tHi *= 2;
      if (tHi > 1e9) return null;
    }
    var lo = 0, hi = tHi;
    while (hi - lo > tol * Math.max(1, hi)) {
      var mid = (lo + hi) / 2;
      if (r0Squared(P, N, V, k, at(mid)) <= r2) hi = mid; else lo = mid;
    }
    return at(hi);
  }

  /* Dense two-phase simplex (Bland's rule):
     minimise c.x subject to A x <= b and 0 <= x <= ub. Returns {x, value} or null. */
  function linprog(c, A, b, ub) {
    var n = c.length, rows = [], rhs = [], i, j;
    for (i = 0; i < A.length; i++) { rows.push(A[i].slice()); rhs.push(b[i]); }
    for (j = 0; j < n; j++) if (isFinite(ub[j])) { var e = new Array(n).fill(0); e[j] = 1; rows.push(e); rhs.push(ub[j]); }
    var m = rows.length, nArt = 0;
    for (i = 0; i < m; i++) if (rhs[i] < 0) nArt++;
    var ncol = n + m + nArt, T = zeros(m, ncol + 1), basis = new Array(m), a = 0;
    for (i = 0; i < m; i++) {
      var sg = rhs[i] < 0 ? -1 : 1;
      for (j = 0; j < n; j++) T[i][j] = sg * rows[i][j];
      T[i][n + i] = sg;
      T[i][ncol] = sg * rhs[i];
      if (sg < 0) { T[i][n + m + a] = 1; basis[i] = n + m + a; a++; } else basis[i] = n + i;
    }
    var EPS = 1e-11;
    function pivot(r, col) {
      var pv = T[r][col];
      for (var jj = 0; jj <= ncol; jj++) T[r][jj] /= pv;
      for (var ii = 0; ii < m; ii++) {
        if (ii === r) continue;
        var f = T[ii][col];
        if (f === 0) continue;
        for (var j2 = 0; j2 <= ncol; j2++) T[ii][j2] -= f * T[r][j2];
      }
      basis[r] = col;
    }
    function run(cost, allowed) {
      for (var it = 0; it < 50000; it++) {
        var enter = -1;
        for (var jj = 0; jj < ncol; jj++) {
          if (!allowed(jj)) continue;
          var rc = cost[jj];
          for (var ii = 0; ii < m; ii++) rc -= cost[basis[ii]] * T[ii][jj];
          if (rc < -1e-10) { enter = jj; break; }
        }
        if (enter < 0) return true;
        var leave = -1, best = Infinity;
        for (var r = 0; r < m; r++) {
          if (T[r][enter] > EPS) {
            var ratio = T[r][ncol] / T[r][enter];
            if (ratio < best - 1e-14 || (Math.abs(ratio - best) <= 1e-14 && basis[r] < basis[leave])) { best = ratio; leave = r; }
          }
        }
        if (leave < 0) return false;   // unbounded
        pivot(leave, enter);
      }
      return false;
    }
    var cost1 = new Array(ncol).fill(0);
    for (j = n + m; j < ncol; j++) cost1[j] = 1;
    if (nArt > 0) {
      run(cost1, function () { return true; });
      var infeas = 0;
      for (i = 0; i < m; i++) if (basis[i] >= n + m) infeas += T[i][ncol];
      if (infeas > 1e-9 * Math.max(1, Math.max.apply(null, rhs.map(Math.abs)))) return null;
      for (i = 0; i < m; i++) if (basis[i] >= n + m) {
        for (j = 0; j < n + m; j++) if (Math.abs(T[i][j]) > 1e-9) { pivot(i, j); break; }
      }
    }
    var cost2 = new Array(ncol).fill(0);
    for (j = 0; j < n; j++) cost2[j] = c[j];
    if (!run(cost2, function (jj) { return jj < n + m; })) return null;
    var x = new Array(n).fill(0);
    for (i = 0; i < m; i++) if (basis[i] < n) x[basis[i]] = T[i][ncol];
    x = x.map(function (v, jj) { return Math.min(ub[jj], Math.max(0, v)); });
    return { x: x, value: dot(c, x) };
  }

  /* LP certificate: min cost.u s.t. R_i(u) <= r2 for all i and 0 <= u <= ubar.
     Since R0^2 <= max_i R_i(u), any feasible u is a safe plan. */
  function certificateControl(P, N, V, k, cost, ubar, r2) {
    var Nt = presentPopulation(P, N), n = V.length;
    var m = V.map(function (v, j) { return v / Nt[j]; });
    var A = P.map(function (row) { return row.map(function (p, j) { return -k * p * m[j]; }); });
    var R0 = localNumbers(P, N, V, k);
    var b = R0.map(function (r) { return r2 - r; });
    var res = linprog(cost, A, b, ubar.slice(0, n));
    return res ? res.x : null;
  }

  /* Proposition 9: for any Z >= 0, g(sZ) <= optimal cost for every s >= 0, where
     g(Z) = sum_j ubar_j min(0, c_j - kappa w_j q_j' Z q_j) - tr(Z (r2 I - S(0))).
     The scale s is optimised exactly over the breakpoints of the concave function g(sZ). */
  function dualLowerBound(P, N, V, k, cost, ubar, r2, Z) {
    var n = V.length, W = weights(P, N, V), Q = qMatrix(P, N), S0 = symmetricMatrix(P, N, V, k);
    var beta = new Array(n);
    for (var j = 0; j < n; j++) {
      var s = 0;
      for (var i = 0; i < n; i++) for (var l = 0; l < n; l++) s += Q[i][j] * Z[i][l] * Q[l][j];
      beta[j] = s;
    }
    var base = 0;
    for (var a = 0; a < n; a++) for (var b2 = 0; b2 < n; b2++) base += Z[a][b2] * ((a === b2 ? r2 : 0) - S0[b2][a]);
    var slope = W.map(function (w, jj) { return k * w * beta[jj]; });
    function g(sv) {
      var t = 0;
      for (var jj = 0; jj < n; jj++) t += ubar[jj] * Math.min(0, cost[jj] - sv * slope[jj]);
      return t - sv * base;
    }
    var best = g(0);
    for (var j2 = 0; j2 < n; j2++) if (slope[j2] > 0) best = Math.max(best, g(cost[j2] / slope[j2]));
    return best;
  }

  /* Least-cost control by a barrier (interior-point) method with a certified gap:
     minimise c.u subject to r2 I - S(u) > 0, 0 < u < ubar.
     Returns {u, upper, lower, iterations, outer} with lower <= optimum <= upper; null if infeasible.
     Places with ubar_j = 0 (no control possible) are held at u_j = 0. */
  function leastCostControl(P, N, V, k, cost, ubar, r2, opts) {
    opts = opts || {};
    var relGap = opts.relGap || 1e-6, maxNewton = opts.maxNewton || 200;
    var n = V.length, W = weights(P, N, V), Q = qMatrix(P, N);
    if (r0Squared(P, N, V, k) <= r2) return { u: new Array(n).fill(0), upper: 0, lower: 0, iterations: 0, outer: 0 };
    if (r0Squared(P, N, V, k, ubar) >= r2) return null;
    var J = [];                                  // free variables
    for (var j0 = 0; j0 < n; j0++) if (ubar[j0] > 1e-12) J.push(j0);
    var nf = J.length;
    var kw = W.map(function (w) { return k * w; });

    function F_of(uf) {
      var u = expand(uf), F = zeros(n, n);
      for (var i = 0; i < n; i++) for (var l = i; l < n; l++) {
        var s = 0;
        for (var j = 0; j < n; j++) s += Q[i][j] * kw[j] * (1 - u[j]) * Q[l][j];
        F[i][l] = (i === l ? r2 : 0) - s; F[l][i] = F[i][l];
      }
      return F;
    }
    function expand(uf) { var u = new Array(n).fill(0); for (var q = 0; q < nf; q++) u[J[q]] = uf[q]; return u; }
    var ubf = J.map(function (j) { return ubar[j]; }), cf = J.map(function (j) { return cost[j]; });
    function inside(uf) { for (var q = 0; q < nf; q++) if (!(uf[q] > 0 && uf[q] < ubf[q])) return false; return true; }
    function phi(t, uf, L) {
      var v = t * dot(cf, uf), q;
      for (q = 0; q < n; q++) v -= 2 * Math.log(L[q][q]);
      for (q = 0; q < nf; q++) v -= Math.log(uf[q]) + Math.log(ubf[q] - uf[q]);
      return v;
    }

    var delta = 1e-3, uf = ubf.map(function (x) { return x * (1 - delta); });
    while (!(inside(uf) && cholesky(F_of(uf)))) {
      delta /= 2;
      uf = ubf.map(function (x) { return x * (1 - delta); });
      if (delta < 1e-12) return null;
    }
    var nu = 3 * nf;
    var mu = opts.mu || Math.min(10, Math.max(1.2, 1 + 4 / Math.sqrt(nu)));
    var t = nu / Math.max(dot(cf, uf), 1e-9);
    var newton = 0, outer = 0, bestLower = 0, upper;
    for (;;) {
      outer++;
      for (var it = 0; it < maxNewton; it++) {
        var F = F_of(uf), L = cholesky(F);
        if (!L) break;
        // X = L^-1 Q restricted to the free columns; B = X^T X = Q' F^-1 Q
        var X = J.map(function (j) { return forwardSub(L, Q.map(function (r) { return r[j]; })); });
        var B = zeros(nf, nf);
        for (var a = 0; a < nf; a++) for (var b = a; b < nf; b++) { B[a][b] = dot(X[a], X[b]); B[b][a] = B[a][b]; }
        var grad = new Array(nf), H = zeros(nf, nf);
        for (var q = 0; q < nf; q++) {
          var jq = J[q];
          grad[q] = t * cf[q] - kw[jq] * B[q][q] - 1 / uf[q] + 1 / (ubf[q] - uf[q]);
          for (var r = 0; r < nf; r++) H[q][r] = kw[jq] * kw[J[r]] * B[q][r] * B[q][r];
          H[q][q] += 1 / (uf[q] * uf[q]) + 1 / ((ubf[q] - uf[q]) * (ubf[q] - uf[q]));
        }
        // Newton direction with symmetric diagonal (Jacobi) scaling and a Cholesky solve
        var ds = H.map(function (row, q2) { return Math.sqrt(row[q2]); });
        var Hs = H.map(function (row, q2) { return row.map(function (h, r2_) { return h / (ds[q2] * ds[r2_]); }); });
        var gs = grad.map(function (g, q2) { return g / ds[q2]; });
        var Lh = cholesky(Hs), y;
        if (Lh) y = cholSolve(Lh, gs).map(function (v) { return -v; });
        else { y = gaussSolve(Hs, gs); if (!y) break; y = y.map(function (v) { return -v; }); }
        var step = y.map(function (v, q2) { return v / ds[q2]; });
        var dec2 = -dot(grad, step);
        if (!(dec2 > 0)) break;
        newton++;
        if (dec2 / 2 <= 1e-9) break;
        // backtracking line search that keeps the point strictly feasible
        var sLen = 1, phi0 = phi(t, uf, L), un = null;
        for (;;) {
          var cand = uf.map(function (v, q2) { return v + sLen * step[q2]; });
          if (inside(cand)) {
            var Ln = cholesky(F_of(cand));
            if (Ln && phi(t, cand, Ln) <= phi0 - 0.25 * sLen * dec2) { un = cand; break; }
          }
          sLen *= 0.5;
          if (sLen < 1e-14) break;
        }
        if (!un) break;                 // no further progress possible in floating point
        uf = un;
      }
      var Lz = cholesky(F_of(uf));
      var Z = cholInverse(Lz);
      bestLower = Math.max(bestLower, dualLowerBound(P, N, V, k, cost, ubar, r2, Z));
      upper = dot(cf, uf);
      if (upper - bestLower <= relGap * Math.max(upper, 1e-12) || nu / t <= 1e-12 * Math.max(upper, 1) || outer > 400) break;
      t *= mu;
    }
    return { u: expand(uf), upper: upper, lower: bestLower, iterations: newton, outer: outer };
  }

  /* All five strategies for one target. ubar is a vector of maximum reductions. */
  function strategies(net, target, opts) {
    var P = net.P, N = net.N, V = net.V, k = net.kappa, cost = net.cost, ubar = net.ubar;
    var r2 = target * target, out = {};
    var allSame = ubar.every(function (x) { return Math.abs(x - ubar[0]) < 1e-15; });
    var ones = ubar.map(function () { return 1; });
    var sh = placeShares(P, N, V, k).shares, cs = caseShare(P, N, V, k);
    var plans = {
      uniform: allSame ? uniformControl(P, N, V, k, ubar[0], r2) : scaledControl(P, N, V, k, ones, ubar, r2),
      case_residence: scaledControl(P, N, V, k, cs, ubar, r2),
      place_share: scaledControl(P, N, V, k, sh, ubar, r2),
      certificate: certificateControl(P, N, V, k, cost, ubar, r2)
    };
    var ex = leastCostControl(P, N, V, k, cost, ubar, r2, opts);
    plans.exact = ex ? ex.u : null;
    Object.keys(plans).forEach(function (name) {
      var u = plans[name];
      out[name] = u ? { u: u, cost: costOf(cost, u), r0: r0(P, N, V, k, u), feasible: true } : { u: null, cost: NaN, r0: NaN, feasible: false };
    });
    out.exact.lower = ex ? ex.lower : NaN;
    out.exact.upper = ex ? ex.upper : NaN;
    out.exact.iterations = ex ? ex.iterations : 0;
    return out;
  }

  /* ------------------------------------------------------------------ inversion */

  /* Lawson-Hanson non-negative least squares: min ||A x - b|| subject to x >= 0. */
  function nnls(A, b, maxIter) {
    var m = A.length, n = A[0].length;
    maxIter = maxIter || 3 * n + 30;
    var x = new Array(n).fill(0), passive = new Array(n).fill(false);
    var tol = 1e-12 * Math.max(1, Math.sqrt(dot(b, b))) * n;
    function resid(xv) { var Ax = matVec(A, xv); return b.map(function (bi, i) { return bi - Ax[i]; }); }
    function solveP() {
      var idx = [];
      for (var j = 0; j < n; j++) if (passive[j]) idx.push(j);
      var sub = A.map(function (row) { return idx.map(function (j) { return row[j]; }); });
      var s = lstsq(sub, b), z = new Array(n).fill(0);
      idx.forEach(function (j, q) { z[j] = s[q]; });
      return z;
    }
    for (var outer = 0; outer < maxIter; outer++) {
      var w = matTVec(A, resid(x)), jBest = -1, wBest = tol;
      for (var j = 0; j < n; j++) if (!passive[j] && w[j] > wBest) { wBest = w[j]; jBest = j; }
      if (jBest < 0) break;
      passive[jBest] = true;
      for (var inner = 0; inner < 3 * n + 10; inner++) {
        var z = solveP(), ok = true;
        for (var j2 = 0; j2 < n; j2++) if (passive[j2] && z[j2] <= 0) { ok = false; break; }
        if (ok) { x = z; break; }
        var alpha = Infinity;
        for (var j3 = 0; j3 < n; j3++) if (passive[j3] && z[j3] <= 0) alpha = Math.min(alpha, x[j3] / (x[j3] - z[j3]));
        x = x.map(function (xi, jj) { return xi + alpha * (z[jj] - xi); });
        for (var j4 = 0; j4 < n; j4++) if (passive[j4] && x[j4] <= 1e-15) { passive[j4] = false; x[j4] = 0; }
      }
    }
    return x;
  }

  /* ||P^-1||_inf <= 1 / min_i (2 p_ii - 1) when every p_ii > 1/2 (Varah, 1975). */
  function varahBound(P) {
    var margin = Infinity;
    for (var i = 0; i < P.length; i++) margin = Math.min(margin, 2 * P[i][i] - 1);
    return margin <= 0 ? Infinity : 1 / margin;
  }

  /* Cases by residence -> infection pressure and infections by place.
     rate_i = cases_i / N_i = sum_j p_ij z_j; z >= 0 by NNLS; infections at place j = z_j N~_j.
     errScale: Varah bound times one Poisson standard deviation of the largest rate. */
  function inferPlaces(P, N, cases) {
    var rate = cases.map(function (c, i) { return c / N[i]; });
    var z = nnls(P, rate);
    var Nt = presentPopulation(P, N);
    var vb = varahBound(P);
    var noise = Math.max.apply(null, cases.map(function (c, i) { return Math.sqrt(Math.max(c, 1)) / N[i]; }));
    return {
      rate: rate, z: z, infections: z.map(function (zj, j) { return zj * Nt[j]; }),
      varah: vb, noiseInf: noise, zErr: vb * noise,
      infErr: Nt.map(function (nt) { return vb * noise * nt; })
    };
  }

  /* ------------------------------------------------------------------ early warning */

  /* Reference value for a Poisson CUSUM tuned to a 1.5-fold rise: k = (mu1 - mu0) / ln(mu1/mu0). */
  function cusumK(mu0, ratio) { ratio = ratio || 1.5; return (ratio - 1) * mu0 / Math.log(ratio); }

  /* S_t = max(0, S_{t-1} + x_t - k_t); alarm at the first t with S_t >= h (0-based index). */
  function cusum(x, k, h) {
    var S = [], s = 0, alarm = null;
    for (var t = 0; t < x.length; t++) {
      var kt = Array.isArray(k) ? k[t] : k;
      s = Math.max(0, s + x[t] - kt);
      S.push(s);
      if (alarm === null && s >= h) alarm = t;
    }
    return { S: S, alarm: alarm };
  }

  /* Single-week threshold rule: alarm when x_t > mu_t + z sqrt(mu_t). */
  function thresholdRule(x, mu, z) {
    var thr = mu.map(function (m) { return m + z * Math.sqrt(m); }), alarm = null;
    for (var t = 0; t < x.length; t++) if (alarm === null && x[t] > thr[t]) alarm = t;
    return { threshold: thr, alarm: alarm };
  }

  /* Proposition 12 (ii): if every count from week tau on exceeds k_t by at least delta,
     the alarm sounds no later than week tau + ceil(h / delta) - 1. Returns ceil(h / delta). */
  function delayBound(h, delta) { return delta > 0 ? Math.ceil(h / delta - 1e-12) : Infinity; }

  /* log Gamma by the Lanczos approximation (g = 7, n = 9), for Poisson probabilities. */
  var LANCZOS = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
    -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  function logGamma(x) {
    if (x < 0.5) return Math.log(Math.PI / Math.abs(Math.sin(Math.PI * x))) - logGamma(1 - x);
    x -= 1;
    var a = LANCZOS[0], t = x + 7.5;
    for (var i = 1; i < 9; i++) a += LANCZOS[i] / (x + i);
    return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
  }
  function poissonPmf(x, mu) {
    if (x < 0 || x !== Math.floor(x)) return 0;
    if (mu === 0) return x === 0 ? 1 : 0;
    return Math.exp(x * Math.log(mu) - mu - logGamma(x + 1));
  }
  function poissonCdf(x, mu) {
    if (x < 0) return 0;
    var s = 0, X = Math.floor(x);
    for (var i = 0; i <= X; i++) s += poissonPmf(i, mu);
    return Math.min(1, s);
  }

  /* Proposition 12 (iii), Brook and Evans (1972): exact average run length of the Poisson CUSUM
     with whole-number k and h and independent Poisson(mu) counts: ((I - Q)^-1 1)_0. */
  function arlMarkov(mu, k, h) {
    var Q = zeros(h, h), i, j;
    for (i = 0; i < h; i++) for (j = 0; j < h; j++) {
      if (j === 0) Q[i][j] = k - i >= 0 ? poissonCdf(k - i, mu) : 0;
      else { var x = j - i + k; Q[i][j] = x >= 0 ? poissonPmf(x, mu) : 0; }
    }
    var A = zeros(h, h);
    for (i = 0; i < h; i++) for (j = 0; j < h; j++) A[i][j] = (i === j ? 1 : 0) - Q[i][j];
    var L = gaussSolve(A, new Array(h).fill(1));
    return L ? L[0] : Infinity;
  }

  /* Single-week rule "alarm when x > c" with Poisson(mu) counts: geometric run length 1 / P(X > c). */
  function thresholdArl(mu, c) {
    var p = 1 - poissonCdf(c, mu);
    return p <= 0 ? Infinity : 1 / p;
  }

  /* Proposition 10: least cost of reaching the target for several season factors. */
  function seasonCurve(net, target, factors, opts) {
    var r2 = target * target;
    return factors.map(function (s) {
      var Vs = net.V.map(function (v) { return v * s; });
      var res = leastCostControl(net.P, net.N, Vs, net.kappa, net.cost, net.ubar, r2, opts);
      return { s: s, r0: r0(net.P, net.N, Vs, net.kappa), cost: res ? res.upper : null, lower: res ? res.lower : null };
    });
  }

  /* ------------------------------------------------------------------ text input */

  /* Numbers from pasted text: separated by spaces, tabs, commas, semicolons or new lines. */
  function parseNumbers(text) {
    return String(text == null ? "" : text).split(/[\s,;]+/).filter(function (s) { return s !== ""; })
      .map(function (s) { return Number(s); }).filter(function (x) { return isFinite(x); });
  }

  /* Rows of cells from CSV or tab-separated text; double quotes may wrap a cell. */
  function parseDelimited(text) {
    var src = String(text == null ? "" : text).replace(/\r\n?/g, "\n");
    var firstLine = src.split("\n")[0] || "";
    var sep = firstLine.indexOf("\t") >= 0 ? "\t" : (firstLine.indexOf(";") >= 0 && firstLine.indexOf(",") < 0 ? ";" : ",");
    var rows = [], row = [], cell = "", q = false;
    for (var i = 0; i < src.length; i++) {
      var ch = src[i];
      if (q) {
        if (ch === '"') { if (src[i + 1] === '"') { cell += '"'; i++; } else q = false; }
        else cell += ch;
      } else if (ch === '"') q = true;
      else if (ch === sep) { row.push(cell.trim()); cell = ""; }
      else if (ch === "\n") { row.push(cell.trim()); rows.push(row); row = []; cell = ""; }
      else cell += ch;
    }
    if (cell !== "" || row.length) { row.push(cell.trim()); rows.push(row); }
    return rows.filter(function (r) { return r.some(function (c) { return c !== ""; }); });
  }

  function toCSV(rows) {
    return rows.map(function (r) {
      return r.map(function (c) {
        var s = c == null ? "" : String(c);
        return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
      }).join(",");
    }).join("\n") + "\n";
  }

  /* Weekly counts and baselines from pasted text: "count, expected" or "week, count, expected"
     per line; lines without numbers (headers) are skipped. */
  function parseWeekly(text) {
    var counts = [], expected = [];
    parseDelimited(text).forEach(function (r) {
      var nums = r.map(function (c) { return c === "" ? NaN : Number(c); });
      if (nums.some(function (x) { return !isFinite(x); })) {
        if (r.length === 1) { var sp = parseNumbers(r[0]); if (sp.length >= 2) nums = sp; else return; } else return;
      }
      if (nums.length >= 3) { counts.push(nums[1]); expected.push(nums[2]); }
      else if (nums.length === 2) { counts.push(nums[0]); expected.push(nums[1]); }
    });
    return { counts: counts, expected: expected };
  }

  /* ------------------------------------------------------------------ the synthetic test network D1 */

  /* Six synthetic barangays. Not real Albay data: a declared test network used to check the
     method (verify_dengue.py, build_d1). Travel minutes = 4 + distance / 0.3 km per minute. */
  var D1 = {
    label: "Test network D1 (synthetic)",
    beta: 0.06, travelMode: "positions", t0: 4, speed: 0.3,
    householdsPerTeamDay: 50, ubar: 0.8, target: 0.95,
    rows: [
      { id: "B1", name: "B1 Poblacion", desc: "Central school and public market", residents: 4000, mhat: 5.3, attract: 10, away: 0.2, x: 0, y: 0, households: 976 },
      { id: "B2", name: "B2 Urban residential", desc: "Urban residential", residents: 6000, mhat: 1.6, attract: 2, away: 0.4, x: 1.5, y: 0.5, households: 1463 },
      { id: "B3", name: "B3 Peri-urban", desc: "Peri-urban", residents: 3500, mhat: 2.0, attract: 1.5, away: 0.35, x: 3, y: -1, households: 854 },
      { id: "B4", name: "B4 Rural upland", desc: "Rural upland", residents: 2000, mhat: 2.3, attract: 0.5, away: 0.25, x: 6, y: 4, households: 488 },
      { id: "B5", name: "B5 Rural lowland", desc: "Rural lowland (rice fields)", residents: 1800, mhat: 1.8, attract: 0.5, away: 0.3, x: -4, y: -3, households: 439 },
      { id: "B6", name: "B6 Coastal", desc: "Coastal", residents: 2500, mhat: 1.4, attract: 1, away: 0.3, x: 2, y: -5, households: 610 }
    ],
    /* four weeks of synthetic cases by residence (results.json d1.inversion.cases_by_residence) */
    cases: [76, 91, 53, 39, 24, 25],
    /* the model's own infections by place that produced those cases (known only because D1 is synthetic) */
    truth: [138.77018138817115, 59.125032902610165, 43.924912005555036, 42.70069198837346, 19.294571669844373, 16.18461004544578],
    /* one simulated year of weekly cases and the expected count of a normal year (results.json d1.cusum) */
    alarm: {
      theta: 1.5, h: 12.75, z: 3.64,
      counts: [5, 8, 10, 4, 9, 9, 7, 7, 2, 6, 6, 9, 8, 7, 5, 4, 5, 5, 11, 4, 6, 7, 7, 6, 9, 10, 13, 15, 11, 13, 11, 24, 10, 25, 17, 17, 27, 19, 21, 27, 24, 26, 13, 15, 15, 13, 15, 15, 28, 23, 17, 18],
      expected: (function () {
        var e = [];
        for (var w = 1; w <= 52; w++) e.push(Math.round((6 + 5 * Math.exp(-Math.pow((w - 32) / 8, 2))) * 100) / 100);
        return e;
      })()
    }
  };

  /* Build P, N, V, cost, ubar for a network description like D1. */
  function buildNetwork(spec, par, season) {
    var rows = spec.rows, n = rows.length;
    var N = rows.map(function (r) { return +r.residents; });
    var omega = rows.map(function (r) { return +r.away; });
    var attract = rows.map(function (r) { return +r.attract; });
    var travel = spec.travelMode === "matrix" && spec.travel ? spec.travel
      : travelFromPositions(rows.map(function (r) { return [+r.x, +r.y]; }), spec.t0, spec.speed);
    var P = residenceTimeMatrix(omega, attract, travel, spec.beta);
    var s = season == null ? 1 : season;
    var V = rows.map(function (r, i) { return +r.mhat * N[i] * s; });
    var cost = rows.map(function (r) { return r.cost != null ? +r.cost : +r.households / spec.householdsPerTeamDay; });
    var ubar = rows.map(function (r) { return r.ubar != null ? +r.ubar : spec.ubar; });
    return { n: n, P: P, N: N, V: V, travel: travel, omega: omega, attract: attract, cost: cost, ubar: ubar, kappa: kappa(par) };
  }

  return {
    version: 1,
    DEFAULT_PARAMS: DEFAULT_PARAMS, D1: D1,
    zeros: zeros, eye: eye, cholesky: cholesky, cholInverse: cholInverse, gaussSolve: gaussSolve, lstsq: lstsq,
    jacobiEigen: jacobiEigen, kappa: kappa, rates: rates,
    travelFromPositions: travelFromPositions, residenceTimeMatrix: residenceTimeMatrix,
    presentPopulation: presentPopulation, weights: weights, symmetricMatrix: symmetricMatrix,
    hostHostMatrix: hostHostMatrix, r0Squared: r0Squared, r0: r0, localNumbers: localNumbers,
    topEigen: topEigen, placeShares: placeShares, gradient: gradient, caseShare: caseShare, analyse: analyse,
    uniformControl: uniformControl, scaledControl: scaledControl, linprog: linprog,
    certificateControl: certificateControl, dualLowerBound: dualLowerBound,
    leastCostControl: leastCostControl, strategies: strategies,
    nnls: nnls, varahBound: varahBound, inferPlaces: inferPlaces,
    cusumK: cusumK, cusum: cusum, thresholdRule: thresholdRule, delayBound: delayBound,
    poissonPmf: poissonPmf, poissonCdf: poissonCdf, arlMarkov: arlMarkov, thresholdArl: thresholdArl,
    seasonCurve: seasonCurve, parseNumbers: parseNumbers, parseDelimited: parseDelimited, toCSV: toCSV,
    parseWeekly: parseWeekly, buildNetwork: buildNetwork
  };
})();
if (typeof module === "object" && module && module.exports) module.exports = BantayModel;
