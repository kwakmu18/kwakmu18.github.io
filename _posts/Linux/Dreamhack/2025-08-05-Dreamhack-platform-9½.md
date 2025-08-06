---
title:  "[Dreamhack] Platform 9½"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-08-05
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/2103">https://dreamhack.io/wargame/challenges/2103</a>

## 문제 설명
You can board <b>Dreamhack Express</b> from platform 9½!

## 문제 분석
스택이 다음과 같은 구조를 가진다.
```c
    // ... some local variables ...
    char *s[10];
    char buf[128];
    char dummy[16];
    __int64 stackcanary;
    __int64 sfp;
    __int64 ret_addr;
```
위와 같은 스택에 다음과 같은 행위를 할 수 있다.
```c
int index;

// 1(view)
scanf("%d", &index);
puts(s[index-1]);

// 2(edit)
scanf("%d", &index);
read(0, buf, size); // size는 전역 변수, 기본 값 0x80
strcpy(s[index-1], buf);
```
- 두 행위 모두 인덱스에 대한 검사가 없으므로, OOB가 발생할 수 있고, 임의 주소 쓰기와 읽기가 가능하다.
- 스택 상에 존재하는 값들을 활용하여 libc base와 PIE base, stack canary를 확보할 수 있다.

가능한 익스플로잇 방법은 여러가지가 있지만, 나는 아래 방법을 활용하였다. (ROP)
- buf[8] ~ buf[15] 위치에 `main 함수의 반환 주소`를 작성하고, 12번째 인덱스를 edit하여 `pop_rdi 가젯`으로 덮어쓴다.
- buf[8] ~ buf[15] 위치에 `main 함수의 반환 주소+8`를 작성하고, 12번째 인덱스를 edit하여 `"/bin/sh" 주소`으로 덮어쓴다.
- ...

## 새롭게 알게된 점
