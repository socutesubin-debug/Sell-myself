# Sell-myself

자기소개서·포트폴리오 설명글을 쓰는 Claude 스킬 kit.

내 말이나 메모 → 문항별 초안 → AI 티 제거 + 글자수 맞춤 → Markdown 문서. 경험과 숫자는 내가 실제로 말한 것만 쓰고 지어내지 않는다.

## 쓰는 법

**기본: claude.ai 프로젝트로 앱처럼 쓰기.** 스킬 zip을 올리고, 경험 은행을 프로젝트 지식에 넣어두고, 프로젝트에서 채팅을 열어 문항을 붙여넣는다. 단계별 설정은 [claude-ai-프로젝트-설정.md](claude-ai-프로젝트-설정.md).

**Claude Code에서 쓰기.** 이 레포에서 Claude Code를 열면 스킬이 자동으로 잡힌다. 경험 은행은 `me/experience-bank.md`(없으면 `templates/experience-bank.md`를 복사), 결과는 `작성본/`에 저장된다. 둘 다 `.gitignore`로 git에 안 올라간다.

글자수만 따로 셀 때:

```bash
python3 .claude/skills/sell-myself/scripts/count.py 파일.md --section "Q1" --target 700 --unit with
```

## 구성

```
.claude/skills/sell-myself/
  SKILL.md                         전체 절차
  references/
    cover-letter-questions.md      자주 나오는 자소서 문항 8개와 작성 요령
    tone-guide.md                  말투 3가지(담백/자신감/이야기)와 문항별 추천
    portfolio-formats.md           VIN 케이스 스터디 / Behance / PDF 형식
    humanizer/                     korean-humanizer 원문 (MIT)
  scripts/
    count.py                       글자수 세기 (공백 포함/제외, 목표 판정). 표준 라이브러리만 사용
    fact_check.py                  최종 글의 숫자가 근거에 있는지 대조
  templates/
    experience-bank.md             경험 은행 양식
    output-cover-letter.md         자소서 결과 문서 양식
    output-portfolio.md            설명글 결과 문서 양식
claude-ai-프로젝트-설정.md          claude.ai 프로젝트 세팅 가이드
me/, 작성본/                        Claude Code용 개인 파일 (git 제외)
```

## 출처와 라이선스

`references/humanizer/`의 `instruction.md`, `ai-tell-taxonomy.md`는 [NomaDamas/k-skill](https://github.com/NomaDamas/k-skill)의 `korean-humanizer`(MIT, commit c41a117)를 복사했다(맨 위 출처 주석과 스크립트 경로 한 줄만 덧붙임). 원 라이선스는 `references/humanizer/LICENSE`. korean-humanizer는 [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai)(MIT)의 방법론을 바탕으로 한다.
