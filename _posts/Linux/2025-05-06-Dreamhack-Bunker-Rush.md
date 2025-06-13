---
title:  "[Dreamhack] Bunker Rush"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-05-06
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/513">https://dreamhack.io/wargame/challenges/513</a>

## 문제 설명
드림핵 회원 수가 22,222명을 달성했어요!!<br>
드림이는 기념으로 2의 상징을 공부해보기로 했어요.<br>
그게 바로 벙커링이래요!! 아 그게 아니라 버퍼링... 이라구요?<br>
```
Arch:     amd64-64-little
RELRO:    Full RELRO
Stack:    Canary found
NX:       NX enabled
PIE:      PIE enabled
```
문제환경은 ubuntu:20.04 (ubuntu@sha256:8ae9bafbb64f63a50caab98fd3a5e37b3eb837a3e0780b78e5218e63193961f9) 입니다.

## 문제 분석
- `setvbuf` 함수의 원형은 다음과 같다.
```c
int setvbuf(FILE* stream, char* buffer, int mode, size_t size);
```
    - `stream`: 버퍼링 방식을 변경할 파일 스트림을 가리키는 포인터
    - `buffer`: 버퍼링에 사용할 메모리 공간.
        - 버퍼를 직접 지정하는 경우, 그 크기를 4번째 매개변수 `size`로 지정해야 함.
        - 버퍼를 NULL로 지정하는 경우 라이브러리가 자동으로 4번째 매개변수 `size`만큼의 버퍼를 할당함.
    - `mode`: 버퍼링 정책.
        - `_IOFBF`: 버퍼가 가득 찼을 때만 입출력 작업 수행.
        - `_IOLBF`: 개행 문자를 만날 때마다, 버퍼가 가득 찼을 때, 입력이 요청될 때 입출력 작업 수행.
        - `_IONBF`: 버퍼링을 수행하지 않음.
    - `size`: 버퍼로 사용할 메모리의 크기(바이트 단위).
- 해당 바이너리의 경우 버퍼링에 사용할 메모리 공간의 주소를 임의로 지정할 수 있으므로, aaw(arbitrary-address-write)가 가능하다.
    - 이를 활용해 힙 청크에 데이터를 입력하여 문자열을 조작하면, 플래그를 획득할 수 있다.

## 새롭게 알게된 점