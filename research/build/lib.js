// Shared formatting helpers for the research paper documents.
// Helpers record headings, tables, and figures so the builder can produce the
// Table of Contents, List of Tables, and List of Figures.
const {
  Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, VerticalAlign, TabStopType,
} = require('docx');

const W = 8640; // text width in DXA (Letter, 1.5" left and 1" right margins)
const LINE = 360; // 1.5 line spacing
const L = AlignmentType.LEFT; const C = AlignmentType.CENTER; const J = AlignmentType.JUSTIFIED; const R = AlignmentType.RIGHT;
const B = { bold: true }; const I = { italics: true }; const BI = { bold: true, italics: true };

const state = { toc: [], tables: [], figures: [], tableNo: 0, figureNo: 0 };

// content: 'text' or [['text', {bold:true}], ['more']]
const runs = (content, size) => (Array.isArray(content) ? content : [[content]])
  .map(([t, o = {}]) => new TextRun({ text: t, ...(size ? { size } : {}), ...o }));

const para = (content, o = {}) => new Paragraph({
  alignment: o.align || J,
  indent: o.indent,
  keepNext: o.keepNext,
  keepLines: o.keepLines,
  pageBreakBefore: o.pageBreakBefore,
  spacing: { before: o.before || 0, after: o.after === undefined ? 80 : o.after, line: o.line || LINE },
  children: runs(content, o.size),
});
const p = (content, o = {}) => para(content, { indent: { firstLine: 720 }, ...o });
const np = (content, o = {}) => para(content, o); // no first-line indent
const blank = (n = 1) => Array.from({ length: n }, () => new Paragraph({ spacing: { after: 0 }, children: [] }));
const center = (content, o = {}) => para(content, { align: C, after: 0, line: 276, ...o });
const runIn = (label, text, o = {}) => p([[label, B], [` ${text}`]], o);

// Hanging-indent list item: "1." or "a." label, then text
const item = (label, content, level = 0, o = {}) => {
  const left = 720 + level * 480;
  const body = Array.isArray(content) ? content : [[content]];
  return new Paragraph({
    alignment: J,
    indent: { left, hanging: 400 },
    tabStops: [{ type: TabStopType.LEFT, position: left }],
    keepNext: o.keepNext,
    spacing: { after: o.after === undefined ? 60 : o.after, line: o.line || LINE },
    children: runs([[`${label}\t`], ...body]),
  });
};
const list = (items, { style = 'num', level = 0, line, after } = {}) => items.map((t, i) => {
  const label = style === 'num' ? `${i + 1}.` : `${String.fromCharCode(97 + i)}.`;
  return item(label, t, level, { line, after });
});

// ---------- headings ----------
const chapter = (num, title) => {
  state.toc.push({ level: 0, text: `CHAPTER ${num}`, label: `CHAPTER ${num} ${title}`, kind: 'body' });
  return [
    para([[`CHAPTER ${num}`, B]], { align: C, pageBreakBefore: true, after: 120, keepNext: true }),
    para([[title, B]], { align: C, after: 360, keepNext: true }),
  ];
};
const front = (title) => para([[title, B]], { align: C, pageBreakBefore: true, after: 360, keepNext: true });
const major = (title) => {
  state.toc.push({ level: 0, text: title, label: title, kind: 'body' });
  return para([[title, B]], { align: C, pageBreakBefore: true, after: 360, keepNext: true });
};
const h2 = (title, o = {}) => {
  if (o.toc !== false) state.toc.push({ level: 1, text: title, label: title, kind: 'body' });
  return para([[title, B]], { align: L, keepNext: true, before: 240, after: 120 });
};
const h3 = (title) => para([[title, BI]], { align: L, keepNext: true, before: 160, after: 80 });
const appendix = (letter, title) => {
  state.toc.push({ level: 1, text: `APPENDIX ${letter}`, label: `Appendix ${letter}. ${title}`, kind: 'body' });
  return [
    para([[`APPENDIX ${letter}`, B]], { align: C, pageBreakBefore: true, after: 60, keepNext: true }),
    para([[title, B]], { align: C, after: 240, keepNext: true }),
  ];
};

// ---------- tables ----------
const border = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
const borders = { top: border, bottom: border, left: border, right: border };

const scale = (rel) => {
  const total = rel.reduce((a, b) => a + b, 0);
  const w = rel.map((x) => Math.floor((x / total) * W));
  w[w.length - 1] += W - w.reduce((a, b) => a + b, 0);
  return w;
};

// cell content: string (\n for line breaks) or {text, bold, italic, align, span, shade, size}
const mkCell = (c, width, o, ci, isHeader, isLast) => {
  const spec = typeof c === 'object' && c !== null ? c : { text: c };
  const size = spec.size || o.size || 21;
  const align = isHeader ? C : (spec.align || (o.aligns && o.aligns[ci]) || L);
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    columnSpan: spec.span,
    shading: isHeader || spec.shade ? { fill: spec.shade || 'E7E6E6', type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: { top: o.pad || 40, bottom: o.pad || 40, left: 80, right: 80 },
    verticalAlign: o.vTop ? VerticalAlign.TOP : VerticalAlign.CENTER,
    children: String(spec.text).split('\n').map((line) => new Paragraph({
      alignment: align,
      keepNext: o.keep !== 'none' && !isLast,
      spacing: { after: 0, line: 240, lineRule: 'auto' },
      children: [new TextRun({ text: line, bold: isHeader || spec.bold, italics: spec.italic, size })],
    })),
  });
};

const table = (rel, header, rows, o = {}) => {
  const widths = scale(rel);
  const trs = [];
  const span = (c) => (typeof c === 'object' && c !== null && c.span) || 1;
  const row = (cells, isHeader, isLast) => {
    let col = 0;
    return cells.map((c) => {
      const w = widths.slice(col, col + span(c)).reduce((a, b) => a + b, 0);
      const cell = mkCell(c, w, o, col, isHeader, isLast);
      col += span(c);
      return cell;
    });
  };
  if (header) trs.push(new TableRow({ tableHeader: true, cantSplit: true, children: row(header, true, false) }));
  rows.forEach((r, ri) => trs.push(new TableRow({
    cantSplit: true,
    height: o.rowHeight ? { value: o.rowHeight, rule: 'atLeast' } : undefined,
    children: row(r, false, ri === rows.length - 1),
  })));
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: widths, rows: trs });
};

const gap = () => new Paragraph({ spacing: { after: 120 }, children: [] });
const tnote = (text) => para([['Note. ', I], [text]], { align: J, line: 240, before: 60, after: 160, size: 20 });
const tcaption = (title) => {
  state.tableNo += 1;
  state.tables.push({ num: state.tableNo, title });
  return para([[`Table ${state.tableNo}. `, B], [title, I]], { align: L, keepNext: true, line: 240, before: 160, after: 80 });
};
// numbered table: caption + table + note or spacer
const ntable = (title, rel, header, rows, o = {}) => [tcaption(title), table(rel, header, rows, o), ...(o.note ? [tnote(o.note)] : [gap()])];
const fcaption = (title) => {
  state.figureNo += 1;
  state.figures.push({ num: state.figureNo, title });
  return para([[`Figure ${state.figureNo}. `, B], [title, I]], { align: C, line: 240, before: 120, after: 200 });
};

// ---------- TOC lines (right tab with dot leader) ----------
const tocLine = (label, page, indent = 0, bold = false) => new Paragraph({
  indent: { left: indent, right: 600, hanging: 0 },
  tabStops: [{ type: TabStopType.RIGHT, position: W, leader: 'dot' }],
  spacing: { after: 60, line: 276 },
  children: [new TextRun({ text: label, bold }), new TextRun({ text: `\t${page}`, bold })],
});

module.exports = {
  W, LINE, L, C, J, R, B, I, BI, state, runs, para, p, np, blank, center, runIn, item, list,
  chapter, front, major, h2, h3, appendix, table, ntable, tcaption, tnote, gap, fcaption, tocLine, scale, borders,
};
