/* LIGTA-S map: draws a road network, hazard zones, origins, shelters and a plan's flows as SVG.
 * Coordinates are kilometers east (x) and north (y) of the summit. Plain ES5, no dependencies.
 *   LigtasMap.draw(svgElement, data, options)
 * options: scenario {zones, closed}, extraClosed [tags], flows [{path:[nodeIds], persons}],
 *          siteNotes {nodeId: {text, tone}}, candidates [{node, label, chosen}], route [nodeIds],
 *          selectOrigin id, bridgesClickable bool, compact bool, label string
 */
(function (root) {
  "use strict";

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function f(n) { return (Math.round(n * 1000) / 1000).toString(); }
  function fmt(n) { return Math.round(n).toLocaleString("en-US"); }
  function setOf(list) { var s = {}; (list || []).forEach(function (k) { s[k] = true; }); return s; }

  /* where the road segment p-q crosses the ray from the summit at bearing deg (math angle), or null */
  function crossing(p, q, deg) {
    var dx = Math.cos(deg * Math.PI / 180), dy = Math.sin(deg * Math.PI / 180);
    var ex = q[0] - p[0], ey = q[1] - p[1];
    var det = ex * (-dy) - ey * (-dx);
    if (Math.abs(det) < 1e-12) return null;
    var t = ((0 - p[0]) * (-dy) - (0 - p[1]) * (-dx)) / det;
    if (!(t > 0 && t < 1)) return null;
    return [p[0] + t * ex, p[1] + t * ey];
  }

  function draw(svg, data, o) {
    o = o || {};
    var geo = data.geo || {};
    var sc = o.scenario || { zones: [], closed: [] };
    var active = setOf(sc.zones);
    var closed = setOf((sc.closed || []).concat(o.extraClosed || []));
    var pos = {}, kind = {}, names = {};
    (data.nodes || []).forEach(function (n) { pos[n.id] = [+n.x, -(+n.y)]; kind[n.id] = n.kind; names[n.id] = n.name || n.id; });
    var xs = [], ys = [];
    Object.keys(pos).forEach(function (k) { xs.push(pos[k][0]); ys.push(pos[k][1]); });
    if (!xs.length) { xs = [-10, 10]; ys = [-10, 10]; }
    var pad = o.compact ? 2.2 : 2.6;
    var minX = Math.min.apply(null, xs) - pad - 0.6, maxX = Math.max.apply(null, xs) + pad + 1.4;
    var minY = Math.min.apply(null, ys) - pad, maxY = Math.max.apply(null, ys) + pad;
    if (geo.pdzRadius) {
      minX = Math.min(minX, -geo.pdzRadius - 1); maxX = Math.max(maxX, geo.pdzRadius + 1);
      minY = Math.min(minY, -geo.pdzRadius - 1); maxY = Math.max(maxY, geo.pdzRadius + 1);
    }
    /* label size in km: larger when the map is drawn narrow (phones), so labels stay readable */
    var px = svg.getBoundingClientRect ? svg.getBoundingClientRect().width : 0;
    var fs = o.compact ? 0.78 : (px > 0 && px < 460 ? 1.08 : px > 0 && px < 640 ? 0.86 : 0.66);
    /* make room for the shelter labels and notes, which can be long (e.g. "EC3 · LPC-TSW") */
    var groups = {};
    (data.shelters || []).forEach(function (s) { if (pos[s.node]) (groups[s.node] = groups[s.node] || []).push(s.id); });
    Object.keys(groups).forEach(function (node) {
      var L = labelAt(pos[node]), p0 = pos[node];
      var note = o.siteNotes && o.siteNotes[node];
      var w = Math.max(groups[node].join(" · ").length * fs * 0.62, note ? note.text.length * fs * 0.57 : 0);
      if (L.anchor === "end") minX = Math.min(minX, L.x - w - 0.3); else maxX = Math.max(maxX, L.x + w + 0.3);
      minY = Math.min(minY, L.y - fs - 0.2); maxY = Math.max(maxY, L.y + fs * 1.3 + 0.2);
      void p0;
    });
    var W = maxX - minX, H = maxY - minY;
    var out = [];
    svg.setAttribute("viewBox", [f(minX), f(minY), f(W), f(H)].join(" "));
    svg.setAttribute("role", "img");
    if (o.label) svg.setAttribute("aria-label", o.label);

    /* hazard layers */
    var chans = data.channels || [];
    var r0 = (geo.channelRange || [1.5, 14.5])[0], r1 = (geo.channelRange || [1.5, 14.5])[1];
    var laharOn = !!active.LAHAR;
    chans.forEach(function (c) {
      var a = c.bearing * Math.PI / 180;
      var x0 = r0 * Math.cos(a), y0 = -r0 * Math.sin(a), x1 = r1 * Math.cos(a), y1 = -r1 * Math.sin(a);
      out.push('<line class="lm-channel' + (laharOn ? " on" : "") + '" x1="' + f(x0) + '" y1="' + f(y0) + '" x2="' + f(x1) + '" y2="' + f(y1) + '"/>');
      /* label at the outer end of the channel; on the east side it goes just past the end, below it
         (above it for a channel to the north-east), clear of the shelter labels beside the line */
      var east = Math.cos(a) > 0.2;
      var lx = east ? x1 + 0.7 : (r1 - 0.6) * Math.cos(a) + 0.5;
      var ly = east ? (y1 > 0 ? y1 + fs * 0.9 + 0.3 : y1 - 0.3) : -(r1 - 0.6) * Math.sin(a);
      out.push('<text class="lm-chlabel" x="' + f(lx) + '" y="' + f(ly) + '" font-size="' + f(fs * 0.9) + '">Channel ' + esc(c.id) + '</text>');
    });
    if (geo.pdzRadius) {
      out.push('<circle class="lm-pdz' + (active.PDZ ? " on" : "") + '" cx="0" cy="0" r="' + f(geo.pdzRadius) + '"><title>' + esc(zoneName(data, "PDZ")) + '</title></circle>');
    }
    if (geo.edz) {
      var e = geo.edz;
      var p = function (r, deg) { var t = deg * Math.PI / 180; return f(r * Math.cos(t)) + " " + f(-r * Math.sin(t)); };
      var large = (e.to - e.from) > 180 ? 1 : 0;
      out.push('<path class="lm-edz' + (active.EDZ ? " on" : "") + '" d="M' + p(e.r1, e.from) + " A" + f(e.r1) + " " + f(e.r1) + " 0 " + large + " 0 " + p(e.r1, e.to) +
        " L" + p(e.r0, e.to) + " A" + f(e.r0) + " " + f(e.r0) + " 0 " + large + " 1 " + p(e.r0, e.from) + 'Z"><title>' + esc(zoneName(data, "EDZ")) + '</title></path>');
    }

    /* roads */
    var bridgeTag = {};
    chans.forEach(function (c) { (c.bridges || []).forEach(function (b) { bridgeTag[b] = c; }); });
    var bridges = [];
    (data.roads || []).forEach(function (r) {
      var a = pos[r.u], b = pos[r.v];
      if (!a || !b) return;
      var isClosed = !!closed[r.tag];
      var cls = "lm-road" + (kind[r.u] === "origin" || kind[r.v] === "origin" ? " local" : "") + (isClosed ? " closed" : "");
      out.push('<line class="' + cls + '" x1="' + f(a[0]) + '" y1="' + f(a[1]) + '" x2="' + f(b[0]) + '" y2="' + f(b[1]) + '"><title>' +
        esc(names[r.u] + " to " + names[r.v] + ": " + r.tau + " min, " + r.cap + " evacuees per min" + (isClosed ? ", closed" : "")) + '</title></line>');
      if (bridgeTag[r.tag]) {
        var c = bridgeTag[r.tag];
        var X = crossing([+a[0], -a[1]], [+b[0], -b[1]], c.bearing);
        var bx = X ? X[0] : (a[0] + b[0]) / 2, by = X ? -X[1] : (a[1] + b[1]) / 2;
        bridges.push({ tag: r.tag, x: bx, y: by, closed: isClosed, locked: !!setOf(sc.closed)[r.tag] });
      }
    });

    /* flows of the current plan */
    var maxP = 1;
    (o.flows || []).forEach(function (fl) { if (fl.persons > maxP) maxP = fl.persons; });
    (o.flows || []).forEach(function (fl) {
      if (!fl.path || fl.path.length < 2) return;
      var pts = fl.path.map(function (id) { return pos[id] ? f(pos[id][0]) + "," + f(pos[id][1]) : null; }).filter(Boolean);
      var w = 0.12 + 0.5 * Math.sqrt(fl.persons / maxP);
      out.push('<polyline class="lm-flow' + (fl.tone ? " " + fl.tone : "") + '" points="' + pts.join(" ") + '" stroke-width="' + f(w) + '"><title>' + esc(fl.title || (fmt(fl.persons) + " evacuees")) + '</title></polyline>');
    });
    if (o.route && o.route.length > 1) {
      var rp = o.route.map(function (id) { return pos[id] ? f(pos[id][0]) + "," + f(pos[id][1]) : null; }).filter(Boolean);
      out.push('<polyline class="lm-route-under" points="' + rp.join(" ") + '"/>');
      out.push('<polyline class="lm-route" points="' + rp.join(" ") + '"/>');
    }

    /* bridges */
    bridges.forEach(function (b) {
      var s = 0.62;
      var attrs = o.bridgesClickable && !b.locked ? ' data-bridge="' + esc(b.tag) + '" tabindex="0" role="button" aria-pressed="' + (b.closed ? "true" : "false") + '" aria-label="Bridge ' + esc(b.tag) + (b.closed ? ", closed. Activate to reopen." : ", open. Activate to close.") + '"' : "";
      out.push('<g class="lm-bridge' + (b.closed ? " closed" : "") + (attrs ? " click" : "") + '"' + attrs + '>' +
        (attrs ? '<circle class="hit" cx="' + f(b.x + 0.25) + '" cy="' + f(b.y + 0.3) + '" r="0.95"/>' : "") +
        '<rect x="' + f(b.x - s / 2) + '" y="' + f(b.y - s / 2) + '" width="' + f(s) + '" height="' + f(s) + '" rx="0.08"/>' +
        (b.closed ? '<path d="M' + f(b.x - 0.2) + " " + f(b.y - 0.2) + "L" + f(b.x + 0.2) + " " + f(b.y + 0.2) + "M" + f(b.x + 0.2) + " " + f(b.y - 0.2) + "L" + f(b.x - 0.2) + " " + f(b.y + 0.2) + '"/>' : "") +
        '<text x="' + f(b.x + 0.45) + '" y="' + f(b.y + 0.95) + '" font-size="' + f(fs * 0.82) + '">' + esc(b.tag) + '</text>' +
        '<title>Bridge ' + esc(b.tag) + (b.closed ? " (closed)" : " (open)") + '</title></g>');
    });

    /* ring junctions and towns */
    Object.keys(pos).forEach(function (id) {
      if (kind[id] === "ring") out.push('<circle class="lm-junction" cx="' + f(pos[id][0]) + '" cy="' + f(pos[id][1]) + '" r="0.14"/>');
    });
    out.push('<path class="lm-summit" d="M0 -0.75 L0.7 0.5 L-0.7 0.5Z"><title>Summit</title></path>');

    /* candidate sites (siting) */
    (o.candidates || []).forEach(function (c) {
      var p = pos[c.node];
      if (!p) return;
      out.push('<circle class="lm-cand' + (c.chosen ? " chosen" : "") + '" cx="' + f(p[0]) + '" cy="' + f(p[1]) + '" r="1.05"><title>' + esc(c.title || c.label || c.node) + '</title></circle>');
      if (c.label) out.push('<text class="lm-candlabel' + (c.chosen ? " chosen" : "") + '" x="' + f(p[0] - 1.25) + '" y="' + f(p[1] - 0.75) + '" font-size="' + f(fs * 0.95) + '" text-anchor="end">' + esc(c.label) + '</text>');
    });

    /* shelter sites: shelters that share a node are drawn as one site */
    var sites = {}, order = [];
    (data.shelters || []).forEach(function (s) {
      if (!pos[s.node]) return;
      if (!sites[s.node]) { sites[s.node] = []; order.push(s.node); }
      sites[s.node].push(s);
    });
    order.forEach(function (node) {
      var list = sites[node], p = pos[node];
      var school = list.some(function (s) { return s.kind === "school"; });
      var ec = list.some(function (s) { return s.kind !== "school"; });
      var unsafe = list.every(function (s) { return (s.zones || []).some(function (z) { return active[z]; }); });
      var sz = 0.95, x = p[0] - sz / 2, y = p[1] - sz / 2;
      var t = list.map(function (s) { return s.id + " " + (s.name || ""); }).join("; ") + " (" + names[node] + ")";
      out.push('<g class="lm-site' + (unsafe ? " unsafe" : "") + '"><title>' + esc(t) + '</title>');
      if (school && ec) {
        out.push('<rect class="lm-ec" x="' + f(x) + '" y="' + f(y) + '" width="' + f(sz) + '" height="' + f(sz) + '"/>');
        out.push('<path class="lm-school" d="M' + f(x + sz) + " " + f(y) + "L" + f(x + sz) + " " + f(y + sz) + "L" + f(x) + " " + f(y + sz) + 'Z"/>');
        out.push('<rect class="lm-site-edge" x="' + f(x) + '" y="' + f(y) + '" width="' + f(sz) + '" height="' + f(sz) + '"/>');
      } else {
        out.push('<rect class="' + (school ? "lm-school" : "lm-ec") + ' lm-site-edge" x="' + f(x) + '" y="' + f(y) + '" width="' + f(sz) + '" height="' + f(sz) + '"/>');
      }
      var LP = labelAt(p), lx = LP.x, ly = LP.y, anchor = LP.anchor;
      out.push('<text class="lm-sitelabel" x="' + f(lx) + '" y="' + f(ly) + '" font-size="' + f(fs) + '" text-anchor="' + anchor + '">' + esc(list.map(function (s) { return s.id; }).join(" · ")) + '</text>');
      var note = o.siteNotes && o.siteNotes[node];
      if (note) out.push('<text class="lm-sitenote ' + (note.tone || "") + '" x="' + f(lx) + '" y="' + f(ly + fs * 1.15) + '" font-size="' + f(fs * 0.92) + '" text-anchor="' + anchor + '">' + esc(note.text) + '</text>');
      out.push('</g>');
    });

    /* origins */
    (data.origins || []).forEach(function (og) {
      var p = pos[og.node];
      if (!p) return;
      var on = (og.zones || []).some(function (z) { return active[z]; });
      var r = 0.32 + 0.022 * Math.sqrt(Math.max(0, +og.pop || 0));
      var sel = o.selectOrigin === og.id;
      var attrs = o.originsClickable ? ' data-origin="' + esc(og.id) + '" tabindex="0" role="button" aria-label="' + esc(og.name || og.id) + '"' : "";
      out.push('<g class="lm-origin' + (on ? " on" : "") + (sel ? " sel" : "") + (attrs ? " click" : "") + '"' + attrs + '>' +
        '<circle cx="' + f(p[0]) + '" cy="' + f(p[1]) + '" r="' + f(r) + '"/>' +
        '<text x="' + f(p[0] + r + 0.25) + '" y="' + f(p[1] - r - 0.05) + '" font-size="' + f(fs * 1.02) + '">' + esc(og.id) + '</text>' +
        '<title>' + esc((og.name || og.id) + ": " + fmt(og.pop) + " residents, " + fmt(og.vul) + " vulnerable" + (on ? ", must evacuate" : "")) + '</title></g>');
    });
    svg.innerHTML = out.join("");
  }

  /* where a shelter site's label goes, relative to its marker */
  function labelAt(p) {
    var lx = p[0] + (p[0] >= 0 ? 0.8 : -0.8), anchor = p[0] >= 0 ? "start" : "end";
    if (Math.abs(p[0]) < 3) { lx = p[0] + 0.8; anchor = "start"; }
    var ly = p[1] + (p[1] > 0 ? 1.35 : -0.75);
    if (Math.abs(p[1]) < 2) ly = p[1] - 0.8;
    return { x: lx, y: ly, anchor: anchor };
  }

  function zoneName(data, id) {
    var z = (data.zones || []).filter(function (x) { return x.id === id; })[0];
    return z ? z.name : id;
  }

  root.LigtasMap = { draw: draw };
})(typeof window !== "undefined" ? window : this);
