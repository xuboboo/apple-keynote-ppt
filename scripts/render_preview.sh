#!/usr/bin/env bash
# render_preview.sh — 把 .pptx 逐页导出为 PNG（Windows，PowerPoint COM，WPS 兜底）
#
# 用法: bash render_preview.sh <deck.pptx> [outdir]
# 输出: <outdir>/slide-01.png, slide-02.png, ...
# 优先用 Microsoft PowerPoint COM，不可用时回落 WPS 演示（KWPP）。
# 都不可用时提示改用 LibreOffice：soffice --headless --convert-to pdf <deck.pptx>
#   再用 pdftoppm -png -r 144 <pdf> <outdir>/slide
#
# 注意：Presentations.Open 的第 4 参 WithWindow 必须传 1（msoTrue），
# 传 $false/MsoTriState::msoFalse 在多数版本会直接 E_FAIL。

set -euo pipefail

PPT="${1:?用法: render_preview.sh <deck.pptx> [outdir]}"
OUT="${2:-$(dirname "$PPT")/preview}"
mkdir -p "$OUT"

PPT_WIN=$(cygpath -w "$(cd "$(dirname "$PPT")" && pwd)/$(basename "$PPT")")
OUT_WIN=$(cygpath -w "$(mkdir -p "$OUT" && cd "$OUT" && pwd)")

PS1_FILE="$(mktemp -t deck_export_XXXX.ps1)"
cat > "$PS1_FILE" <<EOF
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
\$pptPath = "$PPT_WIN"
\$outDir  = "$OUT_WIN"

function Export-Deck(\$appName) {
  \$app = New-Object -ComObject \$appName
  \$pres = \$null
  try {
    try { \$pres = \$app.Presentations.Open(\$pptPath, \$true, \$false, 1) }
    catch { \$pres = \$app.Presentations.Open(\$pptPath, 0, 0, 1) }
    foreach (\$slide in \$pres.Slides) {
      \$n = '{0:d2}' -f \$slide.SlideIndex
      \$slide.Export((Join-Path \$outDir "slide-\$n.png"), 'PNG', 1920, 1080)
    }
    \$count = \$pres.Slides.Count
  } finally {
    if (\$pres) { \$pres.Close() }
    \$app.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject(\$app) | Out-Null
  }
  Write-Output "OK \$count"
}

\$exported = \$null
foreach (\$appName in @('PowerPoint.Application', 'KWPP.Application')) {
  try { \$exported = Export-Deck \$appName; Write-Host "[preview] exported via \$appName"; break }
  catch {
    \$line = \$_.InvocationInfo.ScriptLineNumber
    Write-Host "[preview] \$appName unavailable (line \$line): \$(\$_.Exception.Message)"
    Write-Host \$_ | Out-String
  }
}
if (-not \$exported) {
  Write-Host '[preview] PowerPoint COM and WPS COM both unavailable. Install LibreOffice instead:'
  Write-Host "  soffice --headless --convert-to pdf \`"$PPT_WIN\`""
  Write-Host '  pdftoppm -png -r 144 deck.pdf slide'
  exit 3
}
EOF

powershell -NoProfile -ExecutionPolicy Bypass -File "$(cygpath -w "$PS1_FILE")"
if [ "${KEEP_PS:-0}" = "1" ]; then echo "[preview] ps1 kept at: $PS1_FILE"; else rm -f "$PS1_FILE"; fi

echo "[preview] PNG 输出目录: $OUT"
ls "$OUT" | head -30
