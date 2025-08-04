---
title:  "[Dreamhack] wheat-and-barley"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-06-25
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/2146">https://dreamhack.io/wargame/challenges/2146</a>

## 문제 설명

### Description
You reap what you sow.

## 문제 분석
- `stdout` (`_IO_2_1_stdout`) 으로부터 최대 `0x2000`만큼 떨어진 위치에 총 2번의 임의 값 쓰기가 가능하다.
- `stdout`과 가까운 위치에 `__printf_function_table`과 `__printf_arginfo_table`이 위치하므로, 이를 조작하여 `win` 함수를 실행하면 셸을 실행할 수 있다.
- 해당 방법에 대한 분석은 아래 링크를 참고한다.

## 새롭게 알게된 점
- <a target="_blank" href="/posts/AAWtoACE/#__printf_arginfo_table-__printf_function_table-조작을-통한-임의-코드-실행">참고링크</a>