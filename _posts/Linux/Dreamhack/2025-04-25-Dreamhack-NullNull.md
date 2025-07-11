---
title:  "[Dreamhack] NullNull"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-04-25
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/456">https://dreamhack.io/wargame/challenges/456</a>

## 문제 설명
I know there's been some trust issues on "baby" CTF chals, but this really is a NullNull(colloquially "spacious", "easy" in KR) pwnable chal...

## 문제 분석
- 2번 메뉴를 이용하면 스택을 8바이트 단위로 32번째 값까지 임의로 입력할 수 있다. 이때 "32"는 `sub_12F0` 함수가 호출되었을 당시의 `a1` 값에 의해 결정된다.
- 3번 메뉴를 이용하면 스택을 8바이트 단위로 32번째 값까지 출력할 수 있다. 이때 "32"는 `sub_12F0` 함수가 호출되었을 당시의 `a1` 값에 의해 결정된다.
- 1번 메뉴를 이용하면 80바이트의 배열에 80바이트만큼 입력할 수 있다. 이때 81번째 바이트에 널바이트가 입력되어 SFP가 조작될 수 있다.
    - rbp의 오프셋이 조작되면, `a1` 값 자체가 조작되어 더 넓은 영역의 스택을 읽고 쓸 수 있다.
    - 이를 이용하여 libc base와 PIE base를 leak하고, ROP를 수행한다.

## 새롭게 알게된 점