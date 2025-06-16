---
title:  "[Dreamhack] oob"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-13
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1415">https://dreamhack.io/wargame/challenges/1415</a>

## 문제 설명
out of bound!

## 문제 분석
- 1번 메뉴는 bss 영역의 oob 배열로부터 인덱스 기반으로 1바이트씩 값을 읽을 수 있고, 2번 메뉴는 인덱스 기반으로 8바이트씩 값을 쓸 수 있다.
  - 인덱스 검사가 전혀 없으므로, 음수 인덱스나 큰 인덱스를 입력하여 out-of-bound read/write가 가능하다.
  - data 영역에서 바이너리 영역 주소와 libc 영역 주소(`_IO_stdout_2_1_`)를 얻을 수 있다.
- 서버 환경이 Ubuntu-22.04이므로, libc의 got에 쓰기 권한이 있다. (Partial RELRO)
  - `strlen` 함수의 got를 oneshot gadget의 주소로 덮어써봤지만 조건이 까다로워 성공하지 못했다.
  - libc의 주소를 알아냈으니, `environ` 변수의 값을 읽어 스택의 주소를 얻고, 이를 이용하여 `main` 함수의 반환 주소를 ROP payload로 덮어써 셸을 획득하였다.

## 새롭게 알게된 점
- libc의 `environ` 변수
  - glibc의 전역 변수로, 현재 실행 중인 프로세스의 환경 변수 목록을 가리키는 포인터.
  - 이를 이용하여 스택 주소를 leak할 수 있다.