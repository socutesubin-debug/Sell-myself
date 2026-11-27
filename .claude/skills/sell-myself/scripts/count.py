#!/usr/bin/env python3
"""자소서·설명글 글자수 세기 (추정 없이 결정론적으로). 표준 라이브러리만 쓴다.

사용법:
  python3 count.py 파일.md                       파일 전체
  python3 count.py 파일.md --section "Q1"        "## Q1..." 헤딩 아래 본문만
  echo "텍스트" | python3 count.py -
  옵션: --target 700 --unit with|without   목표 판정 (목표의 95~100%면 통과, 초과는 실패)
        --json

규칙:
  공백 포함 = 사용자가 보는 글자(grapheme) 수. 줄바꿈 1개 = 1자, CRLF도 1자.
  공백 제외 = 공백·탭·줄바꿈 등 모든 whitespace를 뺀 글자 수.
  바이트는 UTF-8과 한글2B·영문1B(일부 채용 사이트 방식) 두 가지를 같이 보여준다.
  앞뒤 공백은 자르지 않는다. 사이트마다 줄바꿈 처리가 다를 수 있으니 제출 전 사이트 카운터로 한 번 더 확인.
"""
import argparse
import json
import re
import sys
import unicodedata


def _extends(ch: str) -> bool:
    """앞 글자에 붙어 한 글자를 이루는 문자인가 (결합 문자, 이모지 수식자 등)."""
    cp = ord(ch)
    if unicodedata.category(ch) in ("Mn", "Me", "Mc"):
        return True
    if 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF:  # variation selectors
        return True
    if 0x1F3FB <= cp <= 0x1F3FF:  # skin tone
        return True
    if 0xE0020 <= cp <= 0xE007F:  # tag characters (깃발)
        return True
    if cp == 0x200D:  # ZWJ
        return True
    return False


def _is_jamo_v_or_t(ch: str) -> bool:
    cp = ord(ch)
    return 0x1160 <= cp <= 0x11FF or 0xD7B0 <= cp <= 0xD7FF


def graphemes(text: str):
    """유니코드 grapheme cluster를 근사한다. 한글 완성형·조합형 자모, 이모지 ZWJ 시퀀스, 국기를 처리."""
    out = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "\r" and i + 1 < n and text[i + 1] == "\n":
            out.append("\r\n"); i += 2; continue
        j = i + 1
        cp = ord(ch)
        if 0x1F1E6 <= cp <= 0x1F1FF and j < n and 0x1F1E6 <= ord(text[j]) <= 0x1F1FF:
            j += 1  # 국기(지역 표시 문자 2개)
        elif 0x1100 <= cp <= 0x115F or 0xA960 <= cp <= 0xA97F:  # 조합형 초성
            while j < n and (0x1100 <= ord(text[j]) <= 0x115F or 0xA960 <= ord(text[j]) <= 0xA97F):
                j += 1
            while j < n and _is_jamo_v_or_t(text[j]):
                j += 1
        elif 0xAC00 <= cp <= 0xD7A3:  # 완성형 뒤 조합형 종성
            while j < n and _is_jamo_v_or_t(text[j]):
                j += 1
        if ch not in "\r\n":
            while j < n:
                if text[j] == "‍" and j + 1 < n:
                    j += 2  # ZWJ + 다음 글자까지 한 덩어리
                elif _extends(text[j]):
                    j += 1
                else:
                    break
        out.append(text[i:j])
        i = j
    return out


def extract_section(text: str, name: str) -> str:
    lines = re.split(r"\r\n|\n|\r", text)
    start, level = -1, 0
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m and name in m.group(2):
            start, level = i + 1, len(m.group(1))
            break
    if start < 0:
        raise SystemExit(f"섹션을 찾지 못함: {name}")
    end = len(lines)
    for i in range(start, len(lines)):
        m = re.match(r"^(#{1,6})\s+", lines[i])
        if m and len(m.group(1)) <= level:
            end = i
            break
    # 섹션 안의 메타 줄(> 인용 메모)과 <!-- --> 주석은 본문이 아니므로 뺀다.
    body = "\n".join(l for l in lines[start:end] if not re.match(r"^\s*>", l))
    body = re.sub(r"<!--[\s\S]*?-->", "", body)
    body = re.sub(r"^\s*\n+", "", body)
    return re.sub(r"\n+\s*$", "", body)


def count(text: str) -> dict:
    g = graphemes(text)
    with_spaces = len(g)
    without_spaces = sum(1 for c in g if not c.isspace())
    norm = text.replace("\r\n", "\n")
    lines = 0 if not norm else len(re.split(r"\n|\r| | ", norm))
    kr2 = 0
    for c in g:
        if c in ("\n", "\r\n", "\r"):
            kr2 += 2
        elif len(c) == 1 and ord(c) < 0x80:
            kr2 += 1
        else:
            kr2 += 2
    return {
        "withSpaces": with_spaces,
        "withoutSpaces": without_spaces,
        "lines": lines,
        "bytesUtf8": len(norm.encode("utf-8")),
        "bytesKr2": kr2,
    }


def main():
    p = argparse.ArgumentParser(description="한국어 글자수 세기")
    p.add_argument("file", help="파일 경로 또는 - (표준입력)")
    p.add_argument("--section")
    p.add_argument("--target", type=int)
    p.add_argument("--unit", choices=["with", "without"], default="with")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    if a.file == "-":
        text = sys.stdin.buffer.read().decode("utf-8")
    else:
        with open(a.file, encoding="utf-8", newline="") as f:
            text = f.read()
    if a.section:
        text = extract_section(text, a.section)
    r = count(text)

    if a.target:
        actual = r["withoutSpaces"] if a.unit == "without" else r["withSpaces"]
        lo, hi = round(a.target * 0.95), a.target
        r["target"] = {
            "unit": "공백 제외" if a.unit == "without" else "공백 포함",
            "target": a.target, "actual": actual, "range": [lo, hi],
            "ok": lo <= actual <= hi, "diff": actual - a.target,
        }

    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"공백 포함: {r['withSpaces']}자")
    print(f"공백 제외: {r['withoutSpaces']}자")
    print(f"줄 수: {r['lines']}")
    print(f"바이트: UTF-8 {r['bytesUtf8']}B / 한글2B 방식 {r['bytesKr2']}B")
    t = r.get("target")
    if t:
        if t["ok"]:
            verdict = "통과"
        elif t["diff"] > 0:
            verdict = f"초과 {t['diff']}자"
        else:
            verdict = f"부족 {t['range'][0] - t['actual']}자"
        print(f"목표({t['unit']}) {t['target']}자 → 실제 {t['actual']}자, 허용 {t['range'][0]}~{t['range'][1]}자: {verdict}")


if __name__ == "__main__":
    main()
