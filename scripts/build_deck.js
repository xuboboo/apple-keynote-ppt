#!/usr/bin/env node
/**
 * build_deck.js — outline.json → 苹果发布会风格 .pptx
 *
 * 用法：node build_deck.js <outline.json> [output.pptx]
 * outline 格式见 references/layouts.md 与 example_outline.json。
 * 生成后自动调用 postprocess_gradient.py 写入渐变文字（python 缺失时跳过并警告）。
 */

'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const REQUIRED = {
  cover: ['title'],
  statement: ['text'],
  section: ['title'],
  bignum: ['value', 'label'],
  productHero: ['title'],
  split: ['title', 'image'],
  featureGrid: ['title', 'features'],
  compare: ['leftLabel', 'rightLabel'],
  gallery: ['items'],
  quote: ['text'],
  pricing: ['value'],
  closing: ['title'],
};

function validate(outline) {
  const errors = [];
  if (!outline || typeof outline !== 'object') errors.push('outline 不是 JSON 对象');
  if (!Array.isArray(outline.slides) || outline.slides.length === 0) errors.push('outline.slides 必须是非空数组');
  (outline.slides || []).forEach((d, i) => {
    if (!d.type) {
      errors.push(`slides[${i}] 缺少 type 字段`);
      return;
    }
    const req = REQUIRED[d.type];
    if (!req) {
      errors.push(`slides[${i}] type "${d.type}" 不是合法版式（可选：${Object.keys(REQUIRED).join(', ')}）`);
      return;
    }
    req.forEach((k) => {
      const v = d[k];
      const empty = v == null || v === '' || (Array.isArray(v) && v.length === 0);
      if (empty) errors.push(`slides[${i}]（type=${d.type}）缺少必填字段 "${k}"`);
    });
    if (d.type === 'featureGrid' && d.features && d.features.length > 3)
      errors.push(`slides[${i}]（feature-grid）最多 3 个功能点，当前 ${d.features.length} 个——请拆页`);
  });
  return errors;
}

function resolveImages(outline, baseDir) {
  (outline.slides || []).forEach((d) => {
    if (d.image) d.image = path.resolve(baseDir, d.image);
    if (Array.isArray(d.items)) d.items.forEach((it) => { if (it.image) it.image = path.resolve(baseDir, it.image); });
  });
}

function postprocessGradient(pptxPath) {
  const script = path.join(__dirname, 'postprocess_gradient.py');
  try {
    const out = execFileSync('python', [script, pptxPath], { encoding: 'utf8', timeout: 60000 });
    console.log(out.trim());
  } catch (e) {
    console.warn(`[build_deck] 渐变文字后处理失败（PPT 仍可用，渐变退化为纯色）: ${e.message.split('\n')[0]}`);
  }
}

async function main() {
  const [,, outlinePath, outArg] = process.argv;
  if (!outlinePath) {
    console.error('用法: node build_deck.js <outline.json> [output.pptx]');
    process.exit(2);
  }
  const absOutline = path.resolve(outlinePath);
  const outline = JSON.parse(fs.readFileSync(absOutline, 'utf8'));

  const errors = validate(outline);
  if (errors.length) {
    console.error('[build_deck] outline 校验失败：');
    errors.forEach((e) => console.error('  - ' + e));
    process.exit(1);
  }
  resolveImages(outline, path.dirname(absOutline));

  const outPath = path.resolve(outArg || path.join(path.dirname(absOutline), 'deck.pptx'));
  fs.mkdirSync(path.dirname(outPath), { recursive: true });

  const { buildDeck } = require('./apple_theme');
  await buildDeck(outline, outPath);
  console.log(`[build_deck] 已生成: ${outPath}（${outline.slides.length} 页，mode=${outline.mode || 'dark'}）`);

  postprocessGradient(outPath);
}

main().catch((e) => {
  console.error('[build_deck] 生成失败: ' + (e && e.stack ? e.stack.split('\n').slice(0, 4).join('\n') : e));
  process.exit(1);
});
