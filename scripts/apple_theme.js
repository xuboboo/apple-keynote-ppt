/**
 * apple_theme.js — 苹果发布会风格 pptxgenjs 主题库
 *
 * 视觉规范见 references/design-language.md，版式坐标见 references/layouts.md。
 * 本文件把色板、字号、留白固化为代码，保证每次输出风格一致。
 * 用法：通常不需要直接 require 本文件——用 build_deck.js + outline.json 即可；
 * 只有自定义新版式时才在此扩展，并在 build_deck.js 的 LAYOUTS 注册。
 */

'use strict';

const GRAD_STOPS = ['8B5CF6', '4F8DEB', '46C7C7', '58C878']; // 紫→蓝→青→绿，从左到右

const PALETTES = {
  light: { bg: 'FBFBFD', text: '1D1D1F', muted: '86868B', panel: 'FFFFFF', line: 'D2D2D7', accent: '0071E3' },
  dark: { bg: '000000', text: 'F5F5F7', muted: '86868B', panel: '1D1D1F', line: '424245', accent: '0A84FF' },
};

const FONT_ZH = 'Microsoft YaHei';
const FONT_EN = 'Segoe UI';
const CJK_RE = /[\u2E80-\u9FFF\uF900-\uFAFF\uFF00-\uFFEF]/;

function cleanHex(c) {
  if (!c) return undefined;
  const s = String(c).replace('#', '').trim();
  return /^[0-9A-Fa-f]{6}$/.test(s) ? s.toUpperCase() : /^[0-9A-Fa-f]{8}$/i ? s.slice(0, 6).toUpperCase() : undefined;
}

function pickFont(text) {
  return CJK_RE.test(text || '') ? FONT_ZH : FONT_EN;
}

function makeTheme(mode) {
  const p = PALETTES[mode] || PALETTES.dark;
  return { mode, ...p, gradStops: GRAD_STOPS, fontZh: FONT_ZH, fontEn: FONT_EN };
}

let gradCounter = 0;
function gradTag() {
  gradCounter += 1;
  return `grad:e${gradCounter}`;
}

/** 统一文本入口：自动字体、默认颜色、渐变标记 */
function addT(slide, t, text, opts) {
  opts = opts || {};
  const color = cleanHex(opts.color) || t.text;
  let runs = Array.isArray(text) ? text : [{ text: String(text) }];
  runs = runs.map((r) => ({
    text: r.text,
    options: Object.assign(
      {
        fontFace: r.options && r.options.fontFace ? r.options.fontFace : pickFont(r.text),
        color: cleanHex(r.options && r.options.color) || color,
      },
      opts,
      r.options || {}
    ),
  }));
  if (opts.gradient) {
    opts.objectName = gradTag();
    runs.forEach((r) => {
      r.options.color = t.gradStops[0]; // 真实渐变由 postprocess_gradient.py 写入
    });
  }
  const final = Object.assign({}, opts);
  delete final.gradient;
  return slide.addText(runs, final);
}

function kickerOpts(t) {
  return { fontSize: 16, color: t.muted, charSpacing: 3, bold: false, align: 'center' };
}

/** 把 "2倍" / "40min" / "¥19" 拆成大字号数字 + 缩小单位的 runs */
function valueRuns(value, size, t, opts) {
  opts = opts || {};
  const color = cleanHex(opts.color) || t.text;
  const mk = (text, scale) => ({
    text,
    options: {
      fontSize: Math.round(size * scale),
      fontFace: pickFont(text),
      color,
      bold: opts.bold !== false,
    },
  });
  const isBig = (ch) => /[A-Za-z0-9 .,%+/×x-]/.test(ch);
  const isCur = (ch) => /[¥$€£]/.test(ch);
  const hasBig = [...value].some(isBig);
  if (!hasBig || value.length <= 2) return [mk(value, 1)];
  const runs = [];
  let buf = '';
  let kind = ''; // big | cur | small
  const flush = () => {
    if (!buf) return;
    runs.push(mk(buf, kind === 'big' ? 1 : kind === 'cur' ? 0.6 : 0.42));
    buf = '';
  };
  for (const ch of value) {
    const k = isBig(ch) ? 'big' : isCur(ch) ? 'cur' : 'small';
    if (k !== kind) flush();
    kind = k;
    buf += ch;
  }
  flush();
  return runs;
}

function bgSlide(pres, t) {
  const slide = pres.addSlide();
  slide.background = { color: t.bg };
  return slide;
}

/* ---------------- 12 种版式 ---------------- */

function cover(pres, t, d) {
  const s = bgSlide(pres, t);
  if (d.kicker) addT(s, t, d.kicker.toUpperCase(), { ...kickerOpts(t), x: 0, y: 2.0, w: 13.33, h: 0.4 });
  const size = d.title.length > 16 ? 48 : d.title.length > 10 ? 56 : 64;
  addT(s, t, d.title, {
    x: 0.67, y: 2.45, w: 12, h: 1.9, fontSize: size, bold: true, align: 'center', charSpacing: 1,
    gradient: d.gradient !== false,
  });
  if (d.subtitle) addT(s, t, d.subtitle, { x: 1.67, y: 4.45, w: 10, h: 0.6, fontSize: 22, color: t.muted, align: 'center' });
  if (d.date) addT(s, t, d.date, { x: 0, y: 6.55, w: 13.33, h: 0.4, fontSize: 15, color: t.muted, align: 'center' });
}

function statement(pres, t, d) {
  const s = bgSlide(pres, t);
  const size = d.text.length > 20 ? 36 : d.text.length > 14 ? 44 : 54;
  addT(s, t, d.text, {
    x: 1.42, y: 0, w: 10.5, h: 7.5, fontSize: size, bold: true, align: 'center', valign: 'middle',
    lineSpacingMultiple: 1.15, gradient: !!d.gradient,
  });
}

function section(pres, t, d) {
  const s = bgSlide(pres, t);
  if (d.number) addT(s, t, d.number, { x: 1.1, y: 1.35, w: 5, h: 1.7, fontSize: 96, bold: true, color: t.muted, gradient: !!d.gradient });
  addT(s, t, d.title, { x: 1.1, y: 3.15, w: 10.5, h: 1.3, fontSize: 48, bold: true });
  if (d.subtitle) addT(s, t, d.subtitle, { x: 1.1, y: 4.55, w: 10, h: 0.6, fontSize: 20, color: t.muted });
}

function bignum(pres, t, d) {
  const s = bgSlide(pres, t);
  if (d.kicker) addT(s, t, d.kicker.toUpperCase(), { ...kickerOpts(t), x: 0, y: 1.15, w: 13.33, h: 0.4 });
  addT(s, t, valueRuns(d.value, 120, t), {
    x: 0.67, y: 1.7, w: 12, h: 2.3, align: 'center', valign: 'middle', bold: true,
    gradient: d.gradient !== false,
  });
  if (d.label) addT(s, t, d.label, { x: 0.67, y: 4.15, w: 12, h: 0.7, fontSize: 26, bold: true, align: 'center' });
  if (d.caption) addT(s, t, d.caption, { x: 1.67, y: 4.95, w: 10, h: 0.9, fontSize: 17, color: t.muted, align: 'center' });
}

function productHero(pres, t, d) {
  const s = bgSlide(pres, t);
  if (d.image) {
    addT(s, t, d.title, { x: 0.67, y: 0.85, w: 12, h: 1.0, fontSize: 36, bold: true, align: 'center' });
    if (d.subtitle) addT(s, t, d.subtitle, { x: 1.67, y: 1.85, w: 10, h: 0.55, fontSize: 20, color: t.muted, align: 'center' });
    s.addImage({ path: d.image, x: 3.17, y: 2.55, w: 7, h: 4.35, sizing: { type: 'contain', w: 7, h: 4.35 } });
  } else {
    addT(s, t, d.title, { x: 0.67, y: 2.5, w: 12, h: 1.6, fontSize: 54, bold: true, align: 'center', valign: 'middle', gradient: !!d.gradient });
    if (d.subtitle) addT(s, t, d.subtitle, { x: 1.67, y: 4.35, w: 10, h: 0.6, fontSize: 20, color: t.muted, align: 'center' });
  }
}

function split(pres, t, d) {
  const s = bgSlide(pres, t);
  const imgLeft = d.side === 'left';
  s.addImage({
    path: d.image,
    x: imgLeft ? 0 : 6.93, y: 0, w: 6.4, h: 7.5,
    sizing: { type: 'cover', w: 6.4, h: 7.5 },
  });
  const tx = imgLeft ? 7.0 : 0.9;
  if (d.kicker) addT(s, t, d.kicker.toUpperCase(), { x: tx, y: 2.05, w: 5.4, h: 0.4, fontSize: 15, color: t.muted, charSpacing: 3 });
  addT(s, t, d.title, { x: tx, y: 2.5, w: 5.4, h: 1.1, fontSize: 34, bold: true, lineSpacingMultiple: 1.1 });
  if (d.text) addT(s, t, d.text, { x: tx, y: 3.75, w: 5.2, h: 2.5, fontSize: 17, color: t.muted, lineSpacingMultiple: 1.35 });
}

function featureGrid(pres, t, d) {
  const s = bgSlide(pres, t);
  addT(s, t, d.title, { x: 1.1, y: 0.95, w: 10.5, h: 0.8, fontSize: 34, bold: true });
  const feats = (d.features || []).slice(0, 3);
  const gap = 0.35;
  const w = (11.13 - (feats.length - 1) * gap) / feats.length;
  feats.forEach((f, i) => {
    const x = 1.1 + i * (w + gap);
    addT(s, t, f.title, { x, y: 2.9, w, h: 0.6, fontSize: 21, bold: true });
    if (f.text) addT(s, t, f.text, { x, y: 3.55, w, h: 2.4, fontSize: 16, color: t.muted, lineSpacingMultiple: 1.35 });
  });
}

function compare(pres, t, d) {
  const s = bgSlide(pres, t);
  const L = { x: 1.3, w: 4.8 }, R = { x: 7.23, w: 5.4 };
  addT(s, t, (d.leftLabel || '').toUpperCase(), { x: L.x, y: 1.5, w: L.w, h: 0.4, fontSize: 16, color: t.muted, charSpacing: 2 });
  addT(s, t, (d.rightLabel || '').toUpperCase(), { x: R.x, y: 1.5, w: R.w, h: 0.4, fontSize: 16, color: t.accent, charSpacing: 2 });
  if (d.left && d.left.value) addT(s, t, d.left.value, { x: L.x, y: 2.0, w: L.w, h: 1.1, fontSize: 40, bold: true, color: t.muted });
  if (d.right && d.right.value)
    addT(s, t, d.right.value, { x: R.x, y: 2.0, w: R.w, h: 1.1, fontSize: 48, bold: true, gradient: !!d.gradient });
  const ptRuns = (points, size, color) =>
    (points || []).map((p) => ({ text: p, options: { fontSize: size, color, breakLine: true, paraSpaceAfter: 8, fontFace: pickFont(p) } }));
  if (d.left && d.left.points) addT(s, t, ptRuns(d.left.points, 15, t.muted), { x: L.x, y: 3.4, w: L.w, h: 3.2 });
  if (d.right && d.right.points) addT(s, t, ptRuns(d.right.points, 16, t.text), { x: R.x, y: 3.4, w: R.w, h: 3.2 });
  s.addShape('rect', { x: 6.665, y: 1.7, w: 0.008, h: 3.6, fill: { color: t.line } });
}

function gallery(pres, t, d) {
  const s = bgSlide(pres, t);
  if (d.title) addT(s, t, d.title, { x: 0.67, y: 0.75, w: 12, h: 0.7, fontSize: 30, bold: true, align: 'center' });
  const items = (d.items || []).slice(0, 6);
  const gap = items.length > 4 ? 0.25 : 0.33;
  const w = (11.13 - (items.length - 1) * gap) / items.length;
  items.forEach((it, i) => {
    const x = 1.1 + i * (w + gap);
    if (it.image) {
      s.addImage({ path: it.image, x, y: 1.9, w, h: 2.6, sizing: { type: 'contain', w, h: 2.6 } });
    } else if (it.color) {
      s.addShape('roundRect', { x, y: 1.9, w, h: 2.6, fill: { color: cleanHex(it.color) || t.panel }, rectRadius: 0.25 });
    } else {
      s.addShape('roundRect', { x, y: 1.9, w, h: 2.6, fill: { color: t.panel }, rectRadius: 0.25 });
    }
    addT(s, t, it.name, { x, y: 4.75, w, h: 0.5, fontSize: 18, bold: true, align: 'center' });
    if (it.desc) addT(s, t, it.desc, { x, y: 5.3, w, h: 0.8, fontSize: 14, color: t.muted, align: 'center' });
  });
}

function quote(pres, t, d) {
  const s = bgSlide(pres, t);
  const size = d.text.length > 24 ? 28 : d.text.length > 16 ? 32 : 36;
  addT(s, t, d.text, { x: 1.67, y: 2.1, w: 10, h: 2.4, fontSize: size, bold: true, align: 'center', valign: 'middle', lineSpacingMultiple: 1.2 });
  if (d.attribution) addT(s, t, d.attribution, { x: 0, y: 4.9, w: 13.33, h: 0.5, fontSize: 17, color: t.muted, align: 'center' });
}

function pricing(pres, t, d) {
  const s = bgSlide(pres, t);
  addT(s, t, valueRuns(d.value, 96, t), {
    x: 0.67, y: 1.9, w: 12, h: 2.0, align: 'center', valign: 'middle', bold: true, gradient: !!d.gradient,
  });
  if (d.label) addT(s, t, d.label, { x: 0, y: 4.0, w: 13.33, h: 0.6, fontSize: 22, bold: true, align: 'center' });
  if (d.config) addT(s, t, d.config, { x: 1.67, y: 4.75, w: 10, h: 0.6, fontSize: 18, color: t.muted, align: 'center' });
  if (d.note) addT(s, t, d.note, { x: 1.67, y: 6.5, w: 10, h: 0.4, fontSize: 13, color: t.muted, align: 'center' });
}

function closing(pres, t, d) {
  const s = bgSlide(pres, t);
  addT(s, t, d.title, {
    x: 0.67, y: 2.7, w: 12, h: 1.5, fontSize: 54, bold: true, align: 'center', valign: 'middle',
    gradient: d.gradient !== false,
  });
  if (d.subtitle) addT(s, t, d.subtitle, { x: 1.67, y: 4.35, w: 10, h: 0.6, fontSize: 20, color: t.muted, align: 'center' });
  if (d.event) addT(s, t, d.event, { x: 0, y: 6.55, w: 13.33, h: 0.4, fontSize: 14, color: t.muted, align: 'center' });
}

const LAYOUTS = { cover, statement, section, bignum, productHero, split, featureGrid, compare, gallery, quote, pricing, closing };

/** outline.json → pptx。图片路径需为绝对路径或已解析。 */
function buildDeck(outline, outputPath) {
  const PptxGenJS = require('pptxgenjs');
  const pres = new PptxGenJS();
  pres.layout = 'LAYOUT_WIDE'; // 13.33 × 7.5in
  const t = makeTheme(outline.mode || 'dark');
  if (outline.title) {
    pres.title = outline.title;
    pres.subject = outline.title;
    pres.author = outline.author || 'apple-keynote-ppt';
  }
  const unknown = [];
  (outline.slides || []).forEach((d) => {
    const fn = LAYOUTS[d.type];
    if (!fn) {
      unknown.push(d.type);
      return;
    }
    fn(pres, t, d);
  });
  if (unknown.length) console.warn('[apple-theme] 未识别的版式已跳过: ' + unknown.join(', '));
  return pres.writeFile({ fileName: outputPath });
}

module.exports = { buildDeck, LAYOUTS, makeTheme, cleanHex, pickFont, valueRuns, PALETTES, GRAD_STOPS };
