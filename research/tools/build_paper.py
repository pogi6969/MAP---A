#!/usr/bin/env python3
"""Build a research paper from Markdown into DOCX and PDF.

Markdown conventions understood here (on top of Pandoc's):
  @@TOC@@                 a paragraph replaced by the table of contents
  QQTABQQ                 a tab stop (used inside the table of contents)
  EQNUM:(n)               a paragraph right after a $$ display equation; the two
                          become one borderless row with the number on the right
  ::: {custom-style="X"}  paragraphs in style X (styles defined below)

Pages: US Letter, 1-inch margins, Times New Roman 12 pt, 1.5 line spacing,
page number centered in the footer, no number on the title page. The table of
contents is filled in a second pass from the page numbers of the first PDF.

Usage: python3 build_paper.py paper.md out_basename --toc toc.json
"""

import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mathfmt  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "m": M, "r": R}
# LibreOffice command used to turn the DOCX into a PDF. Set SOFFICE_CMD to override,
# e.g. SOFFICE_CMD="python3 /path/to/soffice_wrapper.py" on machines where soffice needs a wrapper.
SOFFICE = os.environ.get("SOFFICE_CMD", "soffice").split()
TEXT_WIDTH = 9360          # 6.5 in in twips


def w(tag):
    return "{%s}%s" % (W, tag)


# ---------------------------------------------------------------------------
# Reference document (styles)
# ---------------------------------------------------------------------------

STYLE_XML = """
<w:style xmlns:w="{W}" w:type="paragraph" w:styleId="{sid}"{default}>
  <w:name w:val="{name}"/>{based}
  <w:qFormat/>
  <w:pPr>{ppr}</w:pPr>
  <w:rPr>{rpr}</w:rPr>
</w:style>
"""

FONT = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman"/>'
MONO = '<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New" w:eastAsia="Courier New"/>'


def body_ppr(after=160, line=360, jc="both", extra=""):
    return ('<w:spacing w:before="0" w:after="%d" w:line="%d" w:lineRule="auto"/>'
            '<w:jc w:val="%s"/>%s' % (after, line, jc, extra))


PARA_STYLES = {
    # styleId: (name, basedOn, pPr, rPr)
    "Normal": ("Normal", None, body_ppr(), FONT + '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="en-PH"/>'),
    "BodyText": ("Body Text", "Normal", body_ppr(), ""),
    "FirstParagraph": ("First Paragraph", "BodyText", body_ppr(), ""),
    "Compact": ("Compact", "BodyText", body_ppr(after=80), ""),
    "Heading1": ("heading 1", "Normal",
                 '<w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="160" w:line="360" w:lineRule="auto"/>'
                 '<w:jc w:val="left"/><w:outlineLvl w:val="0"/>',
                 '<w:b/><w:bCs/><w:color w:val="000000"/><w:sz w:val="24"/><w:szCs w:val="24"/>'),
    "Heading2": ("heading 2", "Normal",
                 '<w:keepNext/><w:keepLines/><w:spacing w:before="200" w:after="120" w:line="360" w:lineRule="auto"/>'
                 '<w:jc w:val="left"/><w:outlineLvl w:val="1"/>',
                 '<w:b/><w:bCs/><w:color w:val="000000"/><w:sz w:val="24"/><w:szCs w:val="24"/>'),
    "Heading3": ("heading 3", "Normal",
                 '<w:keepNext/><w:keepLines/><w:spacing w:before="160" w:after="100" w:line="360" w:lineRule="auto"/>'
                 '<w:jc w:val="left"/><w:outlineLvl w:val="2"/>',
                 '<w:b/><w:bCs/><w:i w:val="0"/><w:color w:val="000000"/><w:sz w:val="24"/><w:szCs w:val="24"/>'),
    "Center": ("Center", "Normal", body_ppr(after=0, jc="center"), ""),
    "CenterBold": ("Center Bold", "Normal", body_ppr(after=0, jc="center"), "<w:b/><w:bCs/>"),
    "TitleMain": ("Title Main", "Normal", body_ppr(after=240, line=360, jc="center"),
                  '<w:b/><w:bCs/><w:sz w:val="30"/><w:szCs w:val="30"/>'),
    "AbstractTitle": ("Abstract Title", "Normal", body_ppr(after=120, jc="center"),
                      "<w:b/><w:bCs/>"),
    "PaperCaption": ("Paper Caption", "Normal",
                     '<w:keepNext/>' + body_ppr(after=100, line=276), ""),
    "FigureCaption": ("Figure Caption", "Normal", body_ppr(after=200, line=276), '<w:sz w:val="22"/><w:szCs w:val="22"/>'),
    "SourceLine": ("Source Line", "Normal", body_ppr(after=160, line=276, jc="center"),
                   '<w:i/><w:iCs/><w:sz w:val="22"/><w:szCs w:val="22"/>'),
    "NoteText": ("Note Text", "Normal", body_ppr(after=160, line=276),
                 '<w:sz w:val="22"/><w:szCs w:val="22"/>'),
    "FigurePara": ("Figure Para", "Normal", '<w:keepNext/>' + body_ppr(after=60, line=240, jc="center"), ""),
    "Reference": ("Reference", "Normal",
                  '<w:spacing w:before="0" w:after="120" w:line="360" w:lineRule="auto"/>'
                  '<w:ind w:left="720" w:hanging="720"/><w:jc w:val="left"/>', ""),
    "TOC1": ("toc 1", "Normal",
             '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="%d"/></w:tabs>'
             '<w:spacing w:before="0" w:after="60" w:line="320" w:lineRule="auto"/><w:jc w:val="left"/>' % TEXT_WIDTH,
             "<w:b/><w:bCs/>"),
    "TOC2": ("toc 2", "Normal",
             '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="%d"/></w:tabs>'
             '<w:spacing w:before="0" w:after="60" w:line="320" w:lineRule="auto"/><w:ind w:left="567"/>'
             '<w:jc w:val="left"/>' % TEXT_WIDTH, ""),
    "TOC3": ("toc 3", "Normal",
             '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="%d"/></w:tabs>'
             '<w:spacing w:before="0" w:after="60" w:line="320" w:lineRule="auto"/><w:ind w:left="1134"/>'
             '<w:jc w:val="left"/>' % TEXT_WIDTH, ""),
    "TableText": ("Table Text", "Normal", body_ppr(after=0, line=240, jc="left"),
                  '<w:sz w:val="21"/><w:szCs w:val="21"/>'),
    "SourceCode": ("Source Code", "Normal",
                   '<w:spacing w:before="60" w:after="200" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/>',
                   MONO + '<w:sz w:val="18"/><w:szCs w:val="18"/>'),
    "EquationPara": ("Equation Para", "Normal",
                     '<w:spacing w:before="120" w:after="120" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/>', ""),
    "EquationNumber": ("Equation Number", "Normal", body_ppr(after=0, line=240, jc="right"), ""),
}


def make_reference(path):
    subprocess.run(["pandoc", "-o", path, "--print-default-data-file", "reference.docx"], check=True)
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(path) as z:
        z.extractall(tmp)
    sp = os.path.join(tmp, "word", "styles.xml")
    tree = etree.parse(sp)
    root = tree.getroot()
    # document defaults
    rpr_default = root.find("w:docDefaults/w:rPrDefault/w:rPr", NS)
    for child in list(rpr_default):
        rpr_default.remove(child)
    holder = etree.fromstring('<w:rPr xmlns:w="%s">%s<w:sz w:val="24"/><w:szCs w:val="24"/>'
                              '<w:lang w:val="en-PH"/></w:rPr>' % (W, FONT))
    for child in list(holder):
        rpr_default.append(child)
    for sid, (name, based, ppr, rpr) in PARA_STYLES.items():
        old = root.find("w:style[@w:styleId='%s']" % sid, NS)
        if old is not None:
            root.remove(old)
        xml = STYLE_XML.format(W=W, sid=sid, name=name,
                               default=' w:default="1"' if sid == "Normal" else "",
                               based='' if based is None else '<w:basedOn w:val="%s"/>' % based,
                               ppr=ppr, rpr=rpr)
        root.append(etree.fromstring(xml))
    # character style for inline code
    for sid in ("VerbatimChar",):
        old = root.find("w:style[@w:styleId='%s']" % sid, NS)
        if old is not None:
            root.remove(old)
        root.append(etree.fromstring(
            '<w:style xmlns:w="%s" w:type="character" w:styleId="VerbatimChar"><w:name w:val="Verbatim Char"/>'
            '<w:rPr>%s<w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr></w:style>' % (W, MONO)))
    # hyperlinks black
    hl = root.find("w:style[@w:styleId='Hyperlink']", NS)
    if hl is not None:
        rpr = hl.find("w:rPr", NS)
        for c in list(rpr):
            rpr.remove(c)
        rpr.append(etree.fromstring('<w:color xmlns:w="%s" w:val="000000"/>' % W))
    tree.write(sp, xml_declaration=True, encoding="UTF-8", standalone=True)
    os.remove(path)
    _zip_dir(tmp, path)
    shutil.rmtree(tmp)


def _zip_dir(src, dest):
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml first
        names = []
        for base, dirs, files in os.walk(src):
            for f in files:
                full = os.path.join(base, f)
                names.append(os.path.relpath(full, src))
        names.sort(key=lambda n: (n != "[Content_Types].xml", n))
        for n in names:
            z.write(os.path.join(src, n), n)


# ---------------------------------------------------------------------------
# Post-processing of the Pandoc output
# ---------------------------------------------------------------------------

def _para_text(p):
    return "".join(t.text or "" for t in p.iter(w("t")))


def replace_tabs(body):
    for t in list(body.iter(w("t"))):
        if t.text and "QQTABQQ" in t.text:
            r = t.getparent()
            parts = t.text.split("QQTABQQ")
            idx = list(r).index(t)
            r.remove(t)
            for i, part in enumerate(parts):
                if i > 0:
                    r.insert(idx, etree.Element(w("tab")))
                    idx += 1
                if part:
                    nt = etree.Element(w("t"))
                    nt.text = part
                    nt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                    r.insert(idx, nt)
                    idx += 1


def style_tables(body):
    for tbl in body.iter(w("tbl")):
        tblPr = tbl.find(w("tblPr"))
        if tblPr is None:
            tblPr = etree.SubElement(tbl, w("tblPr"))
            tbl.insert(0, tblPr)
        if tblPr.find(w("tblCaption")) is not None and tblPr.find(w("tblCaption")).get(w("val")) == "EQ":
            continue
        for tag in ("tblBorders", "tblW", "tblLayout", "tblCellMar", "tblLook"):
            old = tblPr.find(w(tag))
            if old is not None:
                tblPr.remove(old)
        tblW = etree.SubElement(tblPr, w("tblW"))
        tblW.set(w("w"), "5000")
        tblW.set(w("type"), "pct")
        borders = etree.SubElement(tblPr, w("tblBorders"))
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = etree.SubElement(borders, w(side))
            e.set(w("val"), "single")
            e.set(w("sz"), "6")
            e.set(w("space"), "0")
            e.set(w("color"), "000000")
        mar = etree.SubElement(tblPr, w("tblCellMar"))
        for side, val in (("top", "40"), ("left", "80"), ("bottom", "40"), ("right", "80")):
            e = etree.SubElement(mar, w(side))
            e.set(w("w"), val)
            e.set(w("type"), "dxa")
        # reorder tblPr children into schema order
        order = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
                 "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders",
                 "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription"]
        kids = sorted(list(tblPr), key=lambda e: order.index(etree.QName(e).localname)
                      if etree.QName(e).localname in order else 99)
        for k in list(tblPr):
            tblPr.remove(k)
        for k in kids:
            tblPr.append(k)
        rows = tbl.findall(w("tr"))
        for ri, tr in enumerate(rows):
            trPr = tr.find(w("trPr"))
            if trPr is None:
                trPr = etree.Element(w("trPr"))
                tr.insert(0, trPr)
            if trPr.find(w("cantSplit")) is None:
                trPr.insert(0, etree.Element(w("cantSplit")))
            if ri == 0 and trPr.find(w("tblHeader")) is None:
                trPr.append(etree.Element(w("tblHeader")))
            for p in tr.iter(w("p")):
                pPr = p.find(w("pPr"))
                if pPr is None:
                    pPr = etree.Element(w("pPr"))
                    p.insert(0, pPr)
                ps = pPr.find(w("pStyle"))
                if ps is None:
                    ps = etree.Element(w("pStyle"))
                    pPr.insert(0, ps)
                ps.set(w("val"), "TableText")
                jc = pPr.find(w("jc"))
                if jc is not None and jc.get(w("val")) in ("both",):
                    pPr.remove(jc)
                if ri == 0:
                    for r in p.iter(w("r")):
                        rPr = r.find(w("rPr"))
                        if rPr is None:
                            rPr = etree.Element(w("rPr"))
                            r.insert(0, rPr)
                        if rPr.find(w("b")) is None:
                            rPr.insert(0, etree.Element(w("b")))


def number_equations(body):
    children = list(body)
    i = 0
    while i < len(children) - 1:
        p, q = children[i], children[i + 1]
        is_eq = p.tag == w("p") and (p.find(".//m:oMathPara", NS) is not None or
                                     p.find("w:pPr/w:pStyle[@w:val='EquationPara']", NS) is not None)
        if is_eq and q.tag == w("p"):
            txt = _para_text(q).strip()
            mt = re.fullmatch(r"EQNUM:\((.+)\)", txt)
            if mt:
                tbl = etree.Element(w("tbl"))
                tblPr = etree.SubElement(tbl, w("tblPr"))
                tw = etree.SubElement(tblPr, w("tblW"))
                tw.set(w("w"), str(TEXT_WIDTH))
                tw.set(w("type"), "dxa")
                lay = etree.SubElement(tblPr, w("tblLayout"))
                lay.set(w("type"), "fixed")
                cap = etree.SubElement(tblPr, w("tblCaption"))
                cap.set(w("val"), "EQ")
                grid = etree.SubElement(tbl, w("tblGrid"))
                widths = (TEXT_WIDTH - 900, 900)
                for wd in widths:
                    gc = etree.SubElement(grid, w("gridCol"))
                    gc.set(w("w"), str(wd))
                tr = etree.SubElement(tbl, w("tr"))
                trPr = etree.SubElement(tr, w("trPr"))
                etree.SubElement(trPr, w("cantSplit"))
                for ci, wd in enumerate(widths):
                    tc = etree.SubElement(tr, w("tc"))
                    tcPr = etree.SubElement(tc, w("tcPr"))
                    tcw = etree.SubElement(tcPr, w("tcW"))
                    tcw.set(w("w"), str(wd))
                    tcw.set(w("type"), "dxa")
                    va = etree.SubElement(tcPr, w("vAlign"))
                    va.set(w("val"), "center")
                    if ci == 0:
                        pp = copy.deepcopy(p)
                        pPr = pp.find(w("pPr"))
                        if pPr is None:
                            pPr = etree.Element(w("pPr"))
                            pp.insert(0, pPr)
                        for c in list(pPr):
                            pPr.remove(c)
                        ps = etree.SubElement(pPr, w("pStyle"))
                        ps.set(w("val"), "EquationPara")
                        tc.append(pp)
                    else:
                        np_ = etree.SubElement(tc, w("p"))
                        pPr = etree.SubElement(np_, w("pPr"))
                        ps = etree.SubElement(pPr, w("pStyle"))
                        ps.set(w("val"), "EquationNumber")
                        r = etree.SubElement(np_, w("r"))
                        t = etree.SubElement(r, w("t"))
                        t.text = "(%s)" % mt.group(1)
                body.replace(p, tbl)
                body.remove(q)
                children = list(body)
        i += 1


FOOTER_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<w:ftr xmlns:w="%s" xmlns:r="%s"><w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
              '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
              '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r>'
              '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>') % (W, R)


def page_setup(tmp, body):
    sect = body.find(w("sectPr"))
    if sect is None:
        sect = etree.SubElement(body, w("sectPr"))
    for c in list(sect):
        sect.remove(c)
    # footer part
    with open(os.path.join(tmp, "word", "footer_pg.xml"), "w") as f:
        f.write(FOOTER_XML)
    rels_p = os.path.join(tmp, "word", "_rels", "document.xml.rels")
    rels = etree.parse(rels_p)
    rr = rels.getroot()
    rid = "rIdFooterPg"
    if rr.find("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship[@Id='%s']" % rid) is None:
        el = etree.SubElement(rr, "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
        el.set("Id", rid)
        el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer")
        el.set("Target", "footer_pg.xml")
    rels.write(rels_p, xml_declaration=True, encoding="UTF-8", standalone=True)
    ct_p = os.path.join(tmp, "[Content_Types].xml")
    ct = etree.parse(ct_p)
    cr = ct.getroot()
    CT = "http://schemas.openxmlformats.org/package/2006/content-types"
    if cr.find("{%s}Override[@PartName='/word/footer_pg.xml']" % CT) is None:
        el = etree.SubElement(cr, "{%s}Override" % CT)
        el.set("PartName", "/word/footer_pg.xml")
        el.set("ContentType", "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml")
    ct.write(ct_p, xml_declaration=True, encoding="UTF-8", standalone=True)
    fr = etree.SubElement(sect, w("footerReference"))
    fr.set(w("type"), "default")
    fr.set("{%s}id" % R, rid)
    pg = etree.SubElement(sect, w("pgSz"))
    pg.set(w("w"), "12240")
    pg.set(w("h"), "15840")
    mar = etree.SubElement(sect, w("pgMar"))
    for k, v in (("top", "1440"), ("right", "1440"), ("bottom", "1440"), ("left", "1440"),
                 ("header", "720"), ("footer", "720"), ("gutter", "0")):
        mar.set(w(k), v)
    etree.SubElement(sect, w("titlePg"))


def postprocess(docx_in, docx_out):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(docx_in) as z:
        z.extractall(tmp)
    dp = os.path.join(tmp, "word", "document.xml")
    tree = etree.parse(dp)
    body = tree.getroot().find(w("body"))
    replace_tabs(body)
    style_tables(body)
    number_equations(body)
    page_setup(tmp, body)
    tree.write(dp, xml_declaration=True, encoding="UTF-8", standalone=True)
    if os.path.exists(docx_out):
        os.remove(docx_out)
    _zip_dir(tmp, docx_out)
    shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# Table of contents (two passes)
# ---------------------------------------------------------------------------

def toc_markdown(entries, pages):
    out = []
    for (level, text), page in zip(entries, pages):
        style = {1: "toc 1", 2: "toc 2", 3: "toc 3"}[level]
        safe = re.sub(r"^(\d+)\.", r"\1\\.", text)
        out.append('::: {custom-style="%s"}\n%sQQTABQQ%s\n:::\n' % (style, safe, page))
    return "\n".join(out)


def find_pages(pdf, entries):
    n_pages = int(re.search(r"Pages:\s+(\d+)",
                            subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    texts = []
    for i in range(1, n_pages + 1):
        t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", pdf, "-"],
                           capture_output=True, text=True).stdout
        texts.append([re.sub(r"\s+", " ", ln).strip() for ln in t.splitlines()])
    # skip the table of contents: start after the last page that holds dot leaders
    start = 0
    for i, lines in enumerate(texts):
        if any(re.search(r"\.{8,}", ln) for ln in lines):
            start = i + 1
    pages = []
    cur = start
    for level, text in entries:
        key = re.sub(r"\s+", " ", text).strip()[:45]
        found = None
        for i in range(cur, n_pages):
            if any(ln.startswith(key) for ln in texts[i]):
                found = i
                break
        if found is None:
            print("TOC: heading not found:", text, file=sys.stderr)
            pages.append("?")
            continue
        pages.append(str(found + 1))
        cur = found
    return pages, n_pages


def to_pdf(docx, outdir):
    subprocess.run(SOFFICE + ["--headless", "--convert-to", "pdf", "--outdir", outdir, docx],
                   check=True, capture_output=True)
    return os.path.join(outdir, os.path.splitext(os.path.basename(docx))[0] + ".pdf")


def build(md_path, out_base, toc_path, resource_path):
    here = os.path.dirname(os.path.abspath(__file__))
    ref = os.path.join(here, "reference.docx")
    if not os.path.exists(ref):
        make_reference(ref)
    entries = [tuple(e) for e in json.load(open(toc_path))] if toc_path else []
    md = open(md_path, encoding="utf-8").read()
    md = mathfmt.preprocess(md, os.path.join(os.path.dirname(os.path.abspath(out_base)), "eq"))
    outdir = os.path.dirname(os.path.abspath(out_base))
    pages = ["00"] * len(entries)
    for rnd in range(3):
        text = md.replace("@@TOC@@", toc_markdown(entries, pages))
        tmp_md = out_base + ".build.md"
        with open(tmp_md, "w", encoding="utf-8") as f:
            f.write(text)
        raw = out_base + ".raw.docx"
        subprocess.run(["pandoc", tmp_md, "-f", "markdown+pipe_tables+tex_math_dollars+raw_attribute+fenced_divs",
                        "-o", raw, "--reference-doc", ref, "--resource-path", resource_path],
                       check=True)
        docx = out_base + ".docx"
        postprocess(raw, docx)
        os.remove(raw)
        os.remove(tmp_md)
        pdf = to_pdf(docx, outdir)
        if not entries:
            break
        new_pages, n = find_pages(pdf, entries)
        print("round", rnd, "pages", n, flush=True)
        if new_pages == pages:
            break
        pages = new_pages
    return docx, pdf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("out_base")
    ap.add_argument("--toc")
    ap.add_argument("--resource-path", default=".")
    a = ap.parse_args()
    docx, pdf = build(a.markdown, a.out_base, a.toc, a.resource_path)
    print(docx)
    print(pdf)


if __name__ == "__main__":
    main()
