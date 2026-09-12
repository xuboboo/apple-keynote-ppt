#!/usr/bin/env node
/**
 * build_deck.js — outline.json → 苹果发布会风格 .pptx
 *
 * 用法：node build_deck.js <outline.json> [output.pptx]
 * outline 格式见 references/layouts.md 与 example_outline.json。
 * 顶层 "gradient": false 可全篇关闭渐变（页内 gradient 字段仍可显式覆盖）。
 * 每页可选 "note" 字段写入 PPTX 演讲者备注。
 * 生成后自动调用 postprocess_gradient.py 写入渐变文字（python 缺失时跳过并警告）。
 */

'use strict';

const fs = require('fs');
const os = require('os');
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
  bars: ['title', 'items'],
  timeline: ['title', 'items'],
};

// —— 路径安全：动态路径一律经 safeResolve，限制在允许根目录之内，防路径穿越 ——
function allowedRoots(baseDir) {
  return [baseDir, process.cwd(), __dirname, os.homedir()].map((r) => path.resolve(r));
}

function safeResolve(input, baseDir, label) {
  const target = path.resolve(baseDir, input);
  if (/[\0\x00-\x1f]/.test(target)) throw new Error(`${label} 含非法控制字符: ${input}`);
  if (path.extname(target).toLowerCase() !== '.pptx' && label === '输出路径') {
    throw new Error('输出文件必须是 .pptx 后缀');
  }
  if (process.env.ALLOW_ANY_PATH === '1') return target;
  const inside = allowedRoots(baseDir).some((root) => target === root || target.startsWith(root + path.sep));
  if (!inside) {
    throw new Error(
      `${label} 越界: ${target}\n` +
      `  允许的根目录:\n    ${allowedRoots(baseDir).join('\n    ')}\n` +
      `  如确需访问其他位置，设置环境变量 ALLOW_ANY_PATH=1`
    );
  }
  return target;
}

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
    if ((d.type === 'bars' || d.type === 'timeline') && d.items && d.items.length > 4)
      errors.push(`slides[${i}]（${d.type}）最多 4 个条目，当前 ${d.items.length} 个`);
    if (d.type === 'bars' && Array.isArray(d.items))
      d.items.forEach((it, j) => {
        if (!it || Number.isNaN(Number(it.value)))
          errors.push(`slides[${i}]（bars）items[${j}].value 必须是数字`);
      });
  });
  return errors;
}

function resolveImages(outline, baseDir) {
  (outline.slides || []).forEach((d) => {
    if (d.image) d.image = safeResolve(d.image, baseDir, '图片路径');
    if (Array.isArray(d.items)) d.items.forEach((it) => { if (it.image) it.image = safeResolve(it.image, baseDir, '图片路径'); });
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

function addAnimations(pptxPath) {
  const script = path.join(__dirname, 'add_animations.py');
  try {
    const out = execFileSync('python', [script, pptxPath], { encoding: 'utf8', timeout: 60000 });
    console.log(out.trim());
  } catch (e) {
    console.warn(`[build_deck] 动画注入失败（PPT 仍可用，无转场/入场动画）: ${e.message.split('\n')[0]}`);
  }
}

async function main() {
  const [,, outlinePath, outArg] = process.argv;
  if (!outlinePath) {
    console.error('用法: node build_deck.js <outline.json> [output.pptx]');
    process.exit(2);
  }
  const absOutline = safeResolve(outlinePath, process.cwd(), 'outline 路径');
  const outline = JSON.parse(fs.readFileSync(absOutline, 'utf8'));

  // 顶层 gradient:false = 全篇关闭渐变（商务汇报风）；页内 gradient 仍可显式覆盖
  if (outline.gradient === false) {
    for (const s of outline.slides) {
      if (s.gradient === undefined) s.gradient = false;
    }
  }

  const errors = validate(outline);
  if (errors.length) {
    console.error('[build_deck] outline 校验失败：');
    errors.forEach((e) => console.error('  - ' + e));
    process.exit(1);
  }
  const baseDir = path.dirname(absOutline);
  resolveImages(outline, baseDir);

  const outPath = safeResolve(outArg || 'deck.pptx', baseDir, '输出路径');
  fs.mkdirSync(path.dirname(outPath), { recursive: true });

  const { buildDeck } = require('./apple_theme');
  await buildDeck(outline, outPath);
  console.log(`[build_deck] 已生成: ${outPath}（${outline.slides.length} 页，mode=${outline.mode || 'dark'}）`);

  // 后处理：转场/入场动画（顶层 "animations": false 可关闭）→ 渐变文字
  if (outline.animations !== false) addAnimations(outPath);
  postprocessGradient(outPath);
}

main().catch((e) => {
  console.error('[build_deck] 生成失败: ' + (e && e.stack ? e.stack.split('\n').slice(0, 4).join('\n') : e));
  process.exit(1);
});
