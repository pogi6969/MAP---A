"""Narration script PDF for a rationale video, built from the video's timeline.json.

Usage: python3 narration_script.py timeline.json BRAND video.mp4 title.png out.pdf "pron1|pron2|..." [version]
"""

import html
import json
import os
import subprocess
import sys
import tempfile


def fmt(t):
    m = int(t // 60)
    return "%d:%04.1f" % (m, t - 60 * m)


def fmt_short(t):
    m = int(round(t) // 60)
    return "%d:%02d" % (m, int(round(t)) - 60 * m)


COLORS = ["#8E1B2C", "#A2462A", "#5B3A7A", "#B58A1A", "#3B4A6B"]

CSS = """
@page { size: Letter; margin: 0.55in 0.55in 0.6in 0.55in; }
body { font-family: 'Inter', 'Liberation Sans', sans-serif; color: #231d1f; font-size: 10.5pt; margin: 0; }
.band { background: #6E0F1E; color: #fff; padding: 20px 24px 14px; border-bottom: 5px solid #E0A92A; margin: 0 0 16px; border-radius: 6px; }
.band h1 { font-family: 'Liberation Serif', serif; font-size: 30pt; margin: 0 0 4px; }
.band .sub { color: #F5D27A; font-size: 12pt; }
.lede { line-height: 1.45; margin: 0 0 14px; }
.box { display: flex; border: 1.5px solid #c9b7a0; border-radius: 8px; overflow: hidden; margin-bottom: 16px; }
.box > div { padding: 10px 14px; }
.box .l { flex: 1.35; border-right: 1px solid #e3d6c3; }
.box .r { flex: 1; background: #fbf6ee; }
.box h3 { margin: 0 0 6px; font-size: 11pt; color: #6E0F1E; }
.box ol { margin: 0; padding-left: 18px; line-height: 1.45; }
.box ul { margin: 0; padding-left: 0; list-style: none; line-height: 1.5; }
.scene { margin: 0 0 16px; page-break-inside: auto; }
.bar { display: flex; justify-content: space-between; color: #fff; padding: 7px 12px; border-radius: 6px 6px 0 0; font-weight: 700; }
.bar span.r { font-weight: 500; font-size: 9.5pt; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-size: 8.5pt; color: #6b5f60; border-bottom: 1.5px solid #c9b7a0; padding: 5px 6px; }
td { vertical-align: top; padding: 7px 6px; border-bottom: 1px solid #eee3d3; }
td.n { width: 34px; font-weight: 700; color: #6E0F1E; }
td.t { width: 54px; font-variant-numeric: tabular-nums; }
td.rt { width: 46px; color: #6b5f60; }
.say { font-weight: 700; font-size: 11pt; margin-bottom: 3px; }
.os { color: #6b5f60; font-size: 8.8pt; line-height: 1.35; }
tr { page-break-inside: avoid; }
.title img { width: 100%; border-radius: 6px; margin-top: 8px; }
.cap { font-size: 8.5pt; color: #6b5f60; }
.clean h2 { font-family: 'Liberation Serif', serif; font-size: 22pt; margin: 0 0 4px; color: #6E0F1E; }
.clean h4 { margin: 12px 0 4px; font-size: 9.5pt; color: #6E0F1E; letter-spacing: .04em; }
.clean p { margin: 0 0 5px; line-height: 1.5; }
.clean .ts { color: #B58A1A; font-size: 8.5pt; font-variant-numeric: tabular-nums; margin-right: 6px; }
.pb { page-break-before: always; }
"""


def build_html(tl, brand, video_name, title_png, prons, version="v1"):
    scenes = tl["scenes"]
    words = sum(c["words"] for sc in scenes for c in sc["cues"])
    total = tl["total"]
    ts = tl["title_start"]
    boom = tl["boom"]
    windows = ", ".join("%s–%s" % (fmt(sc["start"]) if i else "0:00", fmt(sc["end"])) for i, sc in enumerate(scenes))
    conc = [c for c in scenes[-1]["cues"]][-3:]
    h = ["<html><head><meta charset='utf-8'><style>%s</style></head><body>" % CSS]
    h.append("<div class='band'><h1>Narration Script</h1><div class='sub'>%s rationale video %s · how MCS comes into play · version without narration</div></div>" % (brand, version))
    h.append("<p class='lede'>Length %s · 1920 × 1080 · 30 fps · subtitles burned in · %d words in four scenes, then a 10-second title card with no narration. "
             "Read each line over <b>%s</b>. Each line starts when its subtitle appears, and every visual cue is tied to a word, so match your pace to the subtitles.</p>"
             % (fmt_short(total), words, html.escape(video_name)))
    h.append("<div class='box'><div class='l'><h3>How to record</h3><ol>"
             "<li>Play the video and start speaking when each subtitle appears (<b>Start</b>).</li>"
             "<li>Finish the line by <b>Finish by</b>. <b>Read time</b> is the time the line needs at an easy pace.</li>"
             "<li>Record each scene as its own take. Scene windows: %s, then the title card %s–%s (no narration).</li>"
             "<li>The boom lands at %s. Read the conclusion (%s to %s) after it, then stay silent through the title card to %s.</li>"
             "<li>Pace is about 2.3 words per second, with a short breath at each comma.</li></ol></div>"
             % (windows, fmt(ts), fmt_short(total), fmt(boom), conc[0]["id"], conc[-1]["id"], fmt_short(total)))
    h.append("<div class='r'><h3>Say it this way</h3><ul>%s</ul></div></div>" % "".join("<li>%s</li>" % p for p in prons))
    for i, sc in enumerate(scenes):
        w = sum(c["words"] for c in sc["cues"])
        h.append("<div class='scene'><div class='bar' style='background:%s'><span>Scene %d · %s</span><span class='r'>%s–%s · %d words · bar: %s</span></div>"
                 % (COLORS[i % len(COLORS)], i + 1, html.escape(sc["name"]), fmt(sc["start"]), fmt(sc["end"]), w, html.escape(sc["bar"])))
        h.append("<table><tr><th>#</th><th>Start</th><th>Finish by</th><th>Read time</th><th>Narration (read this) · on screen</th></tr>")
        for c in sc["cues"]:
            say = html.escape(c["text"]).replace("[pause]", "<span style='color:#B58A1A'>[pause]</span>")
            h.append("<tr><td class='n'>%s</td><td class='t'>%s</td><td class='t'>%s</td><td class='rt'>%.1f s</td>"
                     "<td><div class='say'>%s</div><div class='os'>On screen: %s</div></td></tr>"
                     % (c["id"], fmt(c["start"]), fmt(c["end"]), c["words"] / 2.3, say, html.escape(c["onscreen"])))
        h.append("</table></div>")
    h.append("<div class='scene title'><div class='bar' style='background:#3B2A2E'><span>Title card · Researchers</span><span class='r'>%s–%s · no narration</span></div>" % (fmt(ts), fmt_short(total)))
    h.append("<table><tr><th>#</th><th>Start</th><th>Finish by</th><th>Read time</th><th>Narration (read this) · on screen</th></tr>")
    h.append("<tr><td class='n'>5.1</td><td class='t'>%s</td><td class='t'>%s</td><td class='rt'>—</td><td><div class='say'>[No narration. Stay silent; let the music and the title card play.]</div>"
             "<div class='os'>On screen: the school building under a deep red overlay, the school seal top-left and a white corner grid; the gold letters %s drop in one by one with a hit, then a gold shine; the full paper title in white; two thin white lines draw outward; "
             "\"De Asis, Dave Justin Ll.\" in large gold with \"LEAD RESEARCHER · FOUNDER OF THE %s RESEARCH &amp; APPLICATION\"; then \"Brimbuela, Peter John A. · Shin, Yeaseong\" in white. Fade to black at %s.</div></td></tr></table>"
             % (fmt(ts), fmt_short(total), brand.replace("-", " - "), brand, fmt_short(total)))
    h.append("<img src='file://%s'><div class='cap'>Title card, final frame (also supplied as %s_Title_Page_1920x1080.png and %s_Title_Page_3840x2160.png).</div></div>"
             % (os.path.abspath(title_png), brand, brand))
    h.append("<div class='clean pb'><h2>Clean read</h2><p class='cap'>The same narration without the production notes. Use it as a teleprompter or to rehearse. A slash marks a short breath.</p>")
    for i, sc in enumerate(scenes):
        h.append("<h4>SCENE %d · %s · %s–%s</h4>" % (i + 1, html.escape(sc["name"].upper()), fmt(sc["start"]), fmt(sc["end"])))
        for c in sc["cues"]:
            txt = html.escape(c["text"]).replace(", ", ", / ")
            h.append("<p><span class='ts'>%s</span>%s</p>" % (fmt(c["start"]), txt))
    h.append("<h4>TITLE CARD · RESEARCHERS · %s–%s</h4><p>[Silent. Title card: %s · De Asis, Dave Justin Ll., Lead Researcher · Founder · Brimbuela, Peter John A. · Shin, Yeaseong. Ends %s.]</p></div>"
             % (fmt(ts), fmt_short(total), brand, fmt_short(total)))
    h.append("</body></html>")
    return "\n".join(h)


PRINT_JS = r"""
const { pathToFileURL } = require('url');
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
(async () => {
  const b = await pw.chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  await p.goto(pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.pdf({ path: process.argv[3], format: 'Letter', printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:7px;color:#888;width:100%;padding:0 0.55in;display:flex;justify-content:space-between;font-family:sans-serif"><span>' + process.argv[4] + ' rationale video ' + process.argv[5] + ' · how MCS comes into play · narration script for the non-narrated version</span><span>Page <span class="pageNumber"></span></span></div>',
    margin: { top: '0.55in', bottom: '0.6in', left: '0.55in', right: '0.55in' } });
  await b.close();
})();
"""


def main():
    tl_path, brand, video, title_png, out_pdf, prons = sys.argv[1:7]
    version = sys.argv[7] if len(sys.argv) > 7 else "v1"
    tl = json.load(open(tl_path))
    page = build_html(tl, brand, os.path.basename(video), title_png, prons.split("|"), version)
    tmp = tempfile.mkdtemp()
    hp = os.path.join(tmp, "script.html")
    open(hp, "w").write(page)
    js = os.path.join(tmp, "print.cjs")
    open(js, "w").write(PRINT_JS)
    subprocess.run(["node", js, hp, os.path.abspath(out_pdf), brand, version], check=True)
    # plain metadata
    print(out_pdf)


if __name__ == "__main__":
    main()
