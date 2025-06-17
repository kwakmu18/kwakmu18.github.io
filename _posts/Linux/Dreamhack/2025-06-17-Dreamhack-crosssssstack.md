---
title:  "[Dreamhack] crosssssstack"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-17
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1727">https://dreamhack.io/wargame/challenges/1727</a>

## 문제 설명
제 첫 번째 문제를 즐겨주세요~~

## 문제 분석
- 16바이트 크기의 배열(`rbp-0x10`)에 `read` 함수로 `0x28`바이트만큼 입력할 수 있어 스택 버퍼 오버플로우가 발생한다.
    - 스택 카나리가 적용되어 있지 않으므로 반환 주소를 조작할 수 있다.
    - 실제로 오버플로우가 발생하는 크기는 `0x18`바이트밖에 안되므로, rbp 레지스터를 bss 영역으로 조작하고 `leave; ret` 가젯을 활용하는 Stack Pivoting을 이용한다.
    - `puts@plt(puts@got)`로 libc base를 알아내고, `system("/bin/sh")`을 호출하도록 ROP Payload를 구성한다.

## 새롭게 알게된 점