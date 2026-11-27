#!/usr/bin/env node
// 지어낸 숫자 잡기: 최종 글에 나온 숫자가 경험 은행(또는 이번에 받은 메모)에 실제로 있는지 대조한다.
// 사용법: node fact_check.js <최종글.md> <근거파일1.md> [근거파일2.md ...] [--section 이름]
// 결과: 근거에 없는 숫자 표현 목록. 하나라도 나오면 사용자에게 확인받기 전까지 쓰지 않는다.
// 한계: 숫자만 기계적으로 본다. 회사명·프로젝트명·역할 같은 사실은 SKILL.md 절차대로 사람이 눈으로 대조한다.

const fs = require("fs");
const path = require("path");
const { extractSection } = require(path.join(__dirname, "count.js"));

const args = process.argv.slice(2);
let section = null;
const files = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--section") section = args[++i];
  else files.push(args[i]);
}
if (files.length < 2) {
  console.error("사용법: node fact_check.js <최종글.md> <근거파일...> [--section 이름]");
  process.exit(2);
}

let draft = fs.readFileSync(files[0], "utf8");
if (section) draft = extractSection(draft, section);
const evidence = files.slice(1).map(f => fs.readFileSync(f, "utf8")).join("\n");

// 숫자 정규화: 쉼표 제거, 전각 숫자 반각으로.
const norm = s => s.replace(/[０-９]/g, d => String.fromCharCode(d.charCodeAt(0) - 0xFEE0)).replace(/(\d),(?=\d{3})/g, "$1");
const ev = norm(evidence);
const evNums = new Set((ev.match(/\d+(?:\.\d+)?/g) || []));

// 문항 번호·목록 번호(줄 맨 앞 "1." 등)는 사실이 아니므로 제외.
const body = norm(draft).replace(/^\s*\d+[.)]\s/gm, "");
const re = /\d+(?:\.\d+)?\s*(?:%|퍼센트|배|명|개|건|회|원|만|억|천|시간|분|초|일|주|개월|달|년|위|등|점|p|pt|x|X|k|K|M)?/g;
const missing = [];
let m;
while ((m = re.exec(body))) {
  const num = m[0].match(/\d+(?:\.\d+)?/)[0];
  if (!evNums.has(num)) {
    const s = Math.max(0, m.index - 15), e = Math.min(body.length, m.index + m[0].length + 15);
    missing.push({ value: m[0].trim(), context: body.slice(s, e).replace(/\s+/g, " ") });
  }
}

if (missing.length === 0) {
  console.log("통과: 최종 글의 숫자가 모두 근거 파일에 있습니다.");
} else {
  console.log(`확인 필요: 근거 파일에 없는 숫자 ${missing.length}개`);
  for (const x of missing) console.log(`- ${x.value}  …${x.context}…`);
  process.exit(1);
}
