---
title:  "[Dreamhack] Avatar: Crude Shadow"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-11
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1042">https://dreamhack.io/wargame/challenges/1042</a>

## 문제 설명
### Description
Solved by two people together, but one monitor, one keyboard, each.<br>
Might be better if done alone!

### FYI
flag length = 33<br>
timeout = 20s

## 문제 분석
- 실행 초기에 `init_seccomp()` 함수가 호출되어 seccomp rule이 적용된다. 호출 가능한 시스템 콜은 다음과 같다.
  - `rt_sigreturn`, `exit`, `exit_group`
  - `read`, `write`, `open`, `openat`
- 1번 메뉴를 이용하면 지금까지 쌓인 반환 주소들을 확인할 수 있다.
  - `main` 함수에서 바로 확인해보면 `__libc_start_call_main+128`의 주소를 얻을 수 있으므로 이를 이용하여 libc base를 계산한다.
  - 3번 메뉴를 이용해 `nested_func` 함수로 진입한 후 1번 메뉴를 이용하면 `main+274`의 주소를 얻을 수 있으므로 이를 이용하여 PIE base를 계산한다.
- 2번 메뉴를 이용하면 큰 크기의 스택 버퍼 오버플로우를 일으킬 수 있다.
  - 스택 카나리가 적용되어 있지 않으므로 ROP를 수행하여 플래그 파일을 orw(open-read-write)한다.
  - 플래그 파일명은 바이너리 내 bss 영역에 저장되어 있다.

## 새롭게 알게된 점