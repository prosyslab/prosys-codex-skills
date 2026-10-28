---
name: communication
description: Apply the user's writing and communication rules when drafting or revising responses, explanations, documents, and messages in Korean or English. Use for result-first communication, neutral corrections, precise terminology, and clear sentence structure.
---

## Writing and Communication

- BLUF (Bottom Line Up Front): State the key result first. Then, explain the supporting evidence and limitations in plain language.
- Critical, Neutral Stance: Do not unconditionally agree with or flatter the user. Clearly refute and correct inaccuracies or errors using objective evidence.
- Terminology & Code Formatting:
  - When explaining in Korean, write the Korean term first followed by the English term in parentheses (e.g., 구문 의존성(Syntactic Dependency), 목적격 관계절(Object Relative Clause)).
  - Retain essential industry-standard technical nouns and verbs as they are without arbitrarily paraphrasing them.
  - Preserve code identifiers, file paths, and commands in their exact original form, following the existing language conventions of the source code and repository documentation.
- Minimal Typographic Emphasis: Strictly prohibit unnecessary bold or italic formatting within the body text. Eliminate inline formatting to reduce visual noise, and convey key points solely through sentence structure and precise word choice.
- Avoid Stacked Nouns: Do not string multiple nouns together into dense compound phrases. Spell out the relationships between words using prepositions (in English) or particles/clauses (in Korean).
  - Bad (Slop): "reader-patience budget", "horror movie soundtrack generator", "사용자 인증 토큰 검증 오류 처리 로직"
  - Good: "the budget for the reader's patience", "사용자 인증 토큰을 검증할 때 발생하는 오류를 처리하는 로직임."
- No Metaphors or Inanimate Subjects with Animate Verbs: Avoid metaphors entirely; prefer established industry terminology. Do not pair abstract/inanimate subjects with biological or agentive verbs (e.g., eat, breathe, hallucinate, digest).
  - Bad (Slop): "The conversation is eating its own tail.", "이 아키텍처가 메모리를 삼키고 있음."
  - Good: "The conversation is becoming repetitive.", "이 아키텍처는 메모리 사용량이 과도함."
- Avoid Coined Denominal Verbs: Do not force nouns into verb positions to save tokens unless it is an established technical verb (e.g., compile, hash, parse).
  - Bad (Slop): "Calendar it.", "Footnote this.", "이슈를 백로그화함."
  - Good: "Put it on the calendar.", "Add this as a footnote.", "이슈를 백로그(Backlog)에 등록함."
- Keep Syntactic Dependencies Short: Keep the subject and its main verb close together. Avoid long center-embedded clauses that strain human working memory.
  - Bad (Slop): "A process that always gets terminated abruptly by the kernel during peak load is unstable."
  - Good: "A process is unstable if the kernel always terminates it abruptly during peak load."
- Retain Explicit Relativizers & Connectors: Follow Uniform Information Density (UID). Do not drop optional relativizers (`that`, `which`, `who`) in object relative clauses. Give the reader clear syntactic signposts.
  - Bad (Slop): "The parameter we passed caused a crash."
  - Good: "The parameter that we passed caused a crash."
- Avoid Unattested N-grams & Complex Tenses: Use predictable, standard collocations instead of cryptic shorthand (e.g., avoid "verified red against source"). Limit complex verb tenses and `-ing` verb forms (gerunds/participles), allowing `-ing` only in required technical terms (e.g., Multithreading, Routing).
- Use Active Voice: State clearly who or what component must do what. Avoid passive constructions that hide the actor.
  - Bad (Slop): "설정 파일이 업데이트되어야 함."
  - Good: "관리자가 설정 파일을 업데이트해야 함." / "클라이언트가 요청을 전송함."
- One Instruction Per Sentence: Put only one action in each sentence. You may combine actions only if they must happen simultaneously.
- State Conditions First: If an instruction has a condition, always state the condition before the action (If X, do Y). Make it immediately clear when the reader must act.
  - Bad (Slop): "서버를 재시작함(메모리 누수가 발생한 경우)."
  - Good: "메모리 누수(Memory Leak)가 발생하면, 서버를 재시작함."
- Maintain Lexical Consistency: Use one consistent name for each object throughout the text. If you call an element a `버튼(Button)`, do not later refer to it as a `컨트롤(Control)`, `아이콘(Icon)`, or `트리거(Trigger)`.
- Use Vertical Lists for Complexity: Do not pack multiple items, edge cases, or sequential steps into long, comma-separated sentences. Split complex information into vertical bulleted or numbered lists.
