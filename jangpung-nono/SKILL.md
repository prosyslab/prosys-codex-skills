---
name: jangpung-nono
description: Refactor deeply nested conditionals, match expressions, and long functions into small compositional helpers. Use when the user says “장풍금지” or “장풍 금지”, asks to reduce nesting, or requests monadic/functional cleanup of branching code.
---

# 장풍 금지

깊은 분기와 장문 함수는 작은 판별 함수와 조합식으로 나눈다. “장풍금지” 또는 “장풍 금지”라는 표현은 별도 설명 없이도 이 리팩토링 규칙을 적용하라는 뜻으로 해석한다.

호출어를 받으면 먼저 `장풍금지!`라고 외친 뒤 아래 규칙에 따라 리팩토링을 수행한다.

## 작업 원칙

- 먼저 각 분기가 어떤 정보를 판별하는지 이름 붙인다.
- 중첩 `match`와 `if`는 `Option`/`Result` 조합, `or_else`, `find_map`, 작은 재귀 함수로 평탄화한다.
- 한 함수가 탐색, 변환, 검증, fallback을 모두 수행하지 않게 역할을 분리한다.
- 긴 조건식은 의미 있는 predicate helper로 추출한다.
- mutable reference와 imperative loop는 기능상 필요하지 않으면 사용하지 않는다.
- 동작과 오류 처리는 유지한다. 단순히 분기를 줄이기 위해 fallback을 넓히거나 검사를 제거하지 않는다.
- 새 helper에는 왜 그 증거를 선택하는지, 어떤 invariant를 보장하는지 주석을 단다.
- 조건 검증을 위해 `let* () = if predicate then Some () else None in`처럼
  값을 만들지 않는 Option 관문을 억지로 쓰지 않는다. 조건은 이름 있는
  predicate/helper에서 먼저 판별하고, 실제 값을 반환하는 Option 단계와
  조합한다. 단순 조건이면 평범한 `if` 또는 `match`를 사용한다.
- bool 값만 판별하는 `match f x with | true -> ... | false -> ...` 형태도
  쓰지 않는다. 이 경우에는 `if f x then ... else ...`를 사용한다. bool이
  아닌 variant나 Option/Result의 구조를 분해할 때는 `match`를 사용한다.
- 짧은 함수들을 연결한 `x |> f |> g` 형태의 파이프라인은 가독성을 위해
  여러 줄에 걸쳐 이어도 된다.
- 다만 `x |> List.fold_left (fun ... -> ...) |> ...`처럼 한 단계의 익명
  함수나 식 자체가 여러 줄로 길어지는 경우에는 그 단계를 이름 있는
  helper나 중간 결과로 분리한다. 긴 단계를 파이프라인 안에 넣은 채 다음
  `|>`를 이어 붙이지 않는다.

## 함수 정의 순서

- 새 함수가 상호재귀가 아니면 `and`로 아래에 덧붙이지 않는다.
- 의존하는 helper를 먼저 독립적인 `let`으로 위에 정의하고, 호출하는 함수를 그 아래에 둔다.
- `and`는 함수들이 서로를 직접 호출해야 하는 상호재귀일 때만 사용한다.

## 레코드 생성

- 레코드 값을 만들 때는 가능하면 필드명과 같은 지역변수를 먼저 `let`으로 만든다.
- OCaml의 레코드 shorthand를 사용해 필드 대입을 줄이고, 레코드 식이 여러 줄로 늘어나지 않게 한다.

```ocaml
let name = compute_name input in
let typ = infer_type input in
let location = source_location input in
{ name; typ; location }
```

- 지역변수 이름을 필드명과 맞출 수 없거나 값의 출처를 숨기면 안 되는 경우에는 명시적인
  `field = value` 표기를 사용한다.

## 권장 순서

1. 현재 함수의 입력·출력과 각 fallback 우선순위를 기록한다.
2. 가장 안쪽 분기를 독립적인 이름 있는 helper로 추출한다.
3. `Option.bind`/`let*`, `or_else`, `Option.map`, `Option.value`로 성공 경로를 파이프라인화한다.
4. 반복되는 조건과 타입 판별을 predicate 또는 변환 helper로 통합한다.
5. 기존 테스트와 focused regression test를 실행해 분기 순서와 결과가 보존됐는지 확인한다.

## 피할 형태

```ocaml
match a with
| Some a ->
    if predicate a then
      match b a with
      | Some b ->
          if valid b then result b else fallback ()
      | None -> fallback ()
    else fallback ()
| None -> fallback ()
```

다음처럼 단계별 helper와 monadic pipeline으로 바꾼다. 값 없는 Option
관문으로 조건을 감싸지 말고, 조건을 candidate helper 안에서 직접
판별한다.

```ocaml
let candidate a =
  let* a = a in
  let* b = b_of_a a in
  if predicate a && valid b then Some (result b) else None

let value = candidate input |> or_else fallback
```

리팩토링 후에는 작은 helper가 오히려 의미를 숨기지 않는지 확인하고, 이름과 주석으로 증거의 출처를 드러낸다.
