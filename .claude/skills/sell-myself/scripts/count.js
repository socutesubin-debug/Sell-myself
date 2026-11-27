#!/usr/bin/env node
// 자소서·설명글 글자수 세기 (추정 없이 결정론적으로).
// 사용법:
//   node count.js 파일.md            파일 전체
//   node count.js 파일.md --section "1번"   "## 1번..." 헤딩 아래 본문만
//   echo "텍스트" | node count.js -
//   옵션: --target 1000 --unit with|without  (목표 대비 ±5% 판정)
//         --json
// 규칙:
//   공백 포함 = 유니코드 grapheme 수 (줄바꿈 1개 = 1자, CRLF도 1자)
//   공백 제외 = 공백·탭·줄바꿈 등 모든 whitespace를 뺀 grapheme 수
//   바이트(UTF-8) 와 바이트(한글 2B·영문 1B, 일부 채용 사이트 방식)도 같이 보여준다.
//   앞뒤 공백은 자르지 않는다. 채용 사이트마다 줄바꿈 처리가 다를 수 있으니 최종 제출 전 사이트 카운터로 한 번 더 확인.

const fs = require("fs");

function parseArgs(argv) {
  const o = { file: null, section: null, target: null, unit: "with", json: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--section") o.section = argv[++i];
    else if (a === "--target") o.target = Number(argv[++i]);
    else if (a === "--unit") o.unit = argv[++i];
    else if (a === "--json") o.json = true;
    else if (!o.file) o.file = a;
  }
  return o;
}

function extractSection(text, name) {
  const lines = text.split(/\r\n|\n|\r/);
  let start = -1, level = 0;
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(#{1,6})\s+(.*)$/);
    if (m && m[2].includes(name)) { start = i + 1; level = m[1].length; break; }
  }
  if (start < 0) throw new Error(`섹션을 찾지 못함: ${name}`);
  let end = lines.length;
  for (let i = start; i < lines.length; i++) {
    const m = lines[i].match(/^(#{1,6})\s+/);
    if (m && m[1].length <= level) { end = i; break; }
  }
  // 섹션 안의 메타 줄(> 로 시작하는 인용 메모, <!-- --> 주석)은 본문이 아니므로 뺀다.
  const body = lines.slice(start, end)
    .filter(l => !/^\s*>/.test(l))
    .join("\n")
    .replace(/<!--[\s\S]*?-->/g, "");
  return body.replace(/^\s*\n+/, "").replace(/\n+\s*$/, "");
}

function count(text) {
  const seg = new Intl.Segmenter("ko", { granularity: "grapheme" });
  const norm = text.replace(/\r\n/g, "\n");
  const g = [...seg.segment(norm)].map(s => s.segment);
  const withSpaces = g.length;
  const withoutSpaces = g.filter(c => !/^\s+$/u.test(c)).length;
  const lines = norm.length === 0 ? 0 : norm.split(/\n|\r|\u2028|\u2029/).length;
  const utf8 = Buffer.byteLength(norm, "utf8");
  let kr2 = 0;
  for (const c of g) {
    if (c === "\n") kr2 += 2;
    else if (/^[\x00-\x7F]$/.test(c)) kr2 += 1;
    else kr2 += 2;
  }
  return { withSpaces, withoutSpaces, lines, bytesUtf8: utf8, bytesKr2: kr2 };
}

function main() {
  const o = parseArgs(process.argv.slice(2));
  if (!o.file) {
    console.error("사용법: node count.js <파일|-> [--section 이름] [--target N] [--unit with|without] [--json]");
    process.exit(2);
  }
  let text = o.file === "-" ? fs.readFileSync(0, "utf8") : fs.readFileSync(o.file, "utf8");
  if (o.section) text = extractSection(text, o.section);
  const r = count(text);
  if (o.target) {
    const actual = o.unit === "without" ? r.withoutSpaces : r.withSpaces;
    const lo = Math.round(o.target * 0.95), hi = o.target;
    r.target = { unit: o.unit === "without" ? "공백 제외" : "공백 포함", target: o.target, actual,
      // 자소서는 상한을 넘으면 제출이 안 되므로 목표 이하 + 95% 이상을 합격으로 본다.
      range: [lo, hi], ok: actual >= lo && actual <= hi, diff: actual - o.target };
  }
  if (o.json) { console.log(JSON.stringify(r, null, 2)); return; }
  console.log(`공백 포함: ${r.withSpaces}자`);
  console.log(`공백 제외: ${r.withoutSpaces}자`);
  console.log(`줄 수: ${r.lines}`);
  console.log(`바이트: UTF-8 ${r.bytesUtf8}B / 한글2B 방식 ${r.bytesKr2}B`);
  if (r.target) {
    const t = r.target;
    console.log(`목표(${t.unit}) ${t.target}자 → 실제 ${t.actual}자, 허용 ${t.range[0]}~${t.range[1]}자: ${t.ok ? "통과" : (t.diff > 0 ? `초과 ${t.diff}자` : `부족 ${t.range[0] - t.actual}자`)}`);
  }
}

if (require.main === module) main();
module.exports = { count, extractSection };
