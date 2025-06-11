---
title:  "[Dreamhack] Broken Dahun's Heart"
search: true
categories: ['Linux', 'Linux-Userland']
last_modified_at: 2025-04-08
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1029">https://dreamhack.io/wargame/challenges/1029</a>

## 문제 설명
:( Dahun is sad

## 문제 분석
- main 함수 초반에 `srand()` 함수를 호출해 시드값을 설정하는데, 2바이트 정수로 설정하므로 브루트포싱을 통해 시드를 때려맞출 수 있다.
    - 시드 값이 일치할 때 `rand()` 함수로 얻어지는 랜덤 값들을 예측하여 조건에 맞게 charming point를 얻을 수 있다.
    - charming point는 1번 메뉴 혹은 4번 메뉴를 통해 얻을 수 있는데, 많아봐야 10포인트~200포인트 정도이다.
    - 5번 메뉴인 propose를 선택했을 때 charming point가 100000 이상이고, `rand()` 함수의 반환값을 200000000으로 나눈 나머지가 0이면 셸을 획득해주지만.. 이는 현실적으로 불가능하다.
- 3번 메뉴에서 `read()` 함수로 phone number와 message 배열에 입력하는데, 이를 초기화하지 않으므로 쓰레기 값들이 남아 있다. 이를 이용해 PIE_base, libc_base, stack canary 값을 leak한다.
- 이후 `system()` 함수, `/bin/sh` 문자열, `pop rdi; ret` 가젯 등의 주소를 계산한 후 Stack Buffer Overflow + ROP로 셸을 획득한다.
 
## 새롭게 알게된 점
- c++ iostream의 `std::cin()` 함수 역시 스택 버퍼 오버플로우에 취약하다...