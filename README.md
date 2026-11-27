# Sell-myself

자기소개서·포트폴리오 설명글을 쓰는 Claude 스킬 kit.

내 말이나 메모 → 문항별 초안 → AI 티 제거 + 글자수 맞춤 → Markdown 문서. 경험과 숫자는 내가 실제로 말한 것만 쓰고 지어내지 않는다.

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
    count.js                       글자수 세기 (공백 포함/제외, 목표 판정)
    fact_check.js                  최종 글의 숫자가 근거에 있는지 대조
  templates/
    experience-bank.md             경험 은행 양식
    output-cover-letter.md         자소서 결과 문서 양식
    output-portfolio.md            설명글 결과 문서 양식
me/experience-bank.md              내 경험 은행 (직접 채운다)
작성본/                            결과 문서가 저장되는 곳
```

## 쓰는 법

1. `me/experience-bank.md`에 경험을 메모하듯 적는다. 빈칸이 있어도 된다.
2. 이 레포에서 Claude Code를 열고 말한다.
   - "○○회사 UX 디자이너 자소서. 문항: (붙여넣기) 각 700자 공백 포함"
   - "기본 문항 Q1, Q5, Q8로 자소서 써줘"
   - "E2 프로젝트로 VIN 케이스 스터디랑 Behance 설명 써줘"
3. Claude가 문항별 말투를 묻고, 근거가 빈 곳은 질문한다.
4. 결과는 `작성본/` 아래 Markdown으로 저장된다. 제출 전에 채용 사이트 글자수 카운터로 한 번 더 확인한다(사이트마다 줄바꿈을 세는 방식이 다를 수 있다).

글자수만 따로 셀 때:

```bash
node .claude/skills/sell-myself/scripts/count.js 작성본/자소서/파일.md --section "Q1" --target 700 --unit with
```

claude.ai에서 쓰려면 `.claude/skills/sell-myself` 폴더를 zip으로 묶어 설정의 스킬 업로드에 올린다. 이 경우 경험 은행은 대화에 붙여넣는다.

## 출처와 라이선스

`references/humanizer/`의 `instruction.md`, `ai-tell-taxonomy.md`는 [NomaDamas/k-skill](https://github.com/NomaDamas/k-skill)의 `korean-humanizer`(MIT, commit c41a117)를 그대로 복사했다. 원 라이선스는 `references/humanizer/LICENSE`. korean-humanizer는 [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai)(MIT)의 방법론을 바탕으로 한다.
