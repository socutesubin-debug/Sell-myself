#!/usr/bin/env python3
"""지어낸 숫자 잡기: 최종 글에 나온 숫자가 근거(경험 은행, 이번에 받은 메모)에 실제로 있는지 대조한다.

사용법: python3 fact_check.py <최종글.md> <근거파일1.md> [근거파일2.md ...] [--section 이름]
결과: 근거에 없는 숫자 목록. 하나라도 나오면 종료 코드 1. 사용자에게 확인받기 전까지 그 숫자를 쓰지 않는다.
한계: 숫자만 기계적으로 본다. 회사명·프로젝트명·역할 같은 사실은 SKILL.md 절차대로 눈으로 대조한다.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from count import extract_section  # noqa: E402

UNIT = r"(?:%|퍼센트|배|명|개|건|회|원|만|억|천|시간|분|초|일|주|개월|달|년|위|등|점|p|pt|x|X|k|K|M)?"


def norm(s: str) -> str:
    s = s.translate({c: c - 0xFEE0 for c in range(ord("０"), ord("９") + 1)})
    return re.sub(r"(\d),(?=\d{3})", r"\1", s)


def main():
    p = argparse.ArgumentParser(description="근거에 없는 숫자 찾기")
    p.add_argument("draft")
    p.add_argument("evidence", nargs="+")
    p.add_argument("--section")
    a = p.parse_args()

    with open(a.draft, encoding="utf-8") as f:
        draft = f.read()
    if a.section:
        draft = extract_section(draft, a.section)
    evidence = ""
    for path in a.evidence:
        with open(path, encoding="utf-8") as f:
            evidence += f.read() + "\n"

    ev_nums = set(re.findall(r"\d+(?:\.\d+)?", norm(evidence)))
    # 줄 맨 앞 목록 번호("1. ")는 사실이 아니므로 제외.
    body = re.sub(r"^\s*\d+[.)]\s", "", norm(draft), flags=re.M)

    missing = []
    for m in re.finditer(r"\d+(?:\.\d+)?\s*" + UNIT, body):
        num = re.match(r"\d+(?:\.\d+)?", m.group(0)).group(0)
        if num not in ev_nums:
            s, e = max(0, m.start() - 15), min(len(body), m.end() + 15)
            missing.append((m.group(0).strip(), re.sub(r"\s+", " ", body[s:e])))

    if not missing:
        print("통과: 최종 글의 숫자가 모두 근거 파일에 있습니다.")
        return
    print(f"확인 필요: 근거 파일에 없는 숫자 {len(missing)}개")
    for value, ctx in missing:
        print(f"- {value}  …{ctx}…")
    sys.exit(1)


if __name__ == "__main__":
    main()
