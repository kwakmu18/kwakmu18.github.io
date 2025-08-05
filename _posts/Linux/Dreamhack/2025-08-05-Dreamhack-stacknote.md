---
title:  "[Dreamhack] stacknote"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-08-05
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1997">https://dreamhack.io/wargame/challenges/1997</a>

## 문제 설명
usually notes are stored in the heap, but this time it's stored in the stack.

## 문제 분석
하나의 노트는 다음과 같은 구조를 가지며, `main` 함수의 스택 영역에 총 10개(0~9 인덱스)를 저장할 수 있다.
```c
struct note {
    __int64 size;
    char    data[0x28];
}
```
노트에 대해 4개의 동작(create, read, update, remove)을 수행할 수 있는데, create를 제외한 동작들에는 아래와 같은 루틴이 있다.
```c
    __int64 index; // [rsp+10h] [rbp-10h] BYREF
    ...
    printf("index: ");
    __isoc99_scanf("%ld", &index);

    if ( index <= 9 && note[index].size )
    { 
        //동작 수행...
    }
```
인덱스를 입력하고 9보다 작은지 검증한다.<br>
하지만, 9보다 작은지 "부호 있는 비교"를 하므로, 음수 인덱스를 입력해도 note[index].size만 적절하다면 검증을 통과할 수 있다.

음수 인덱스를 적절히 입력하면 libc base와 PIE base, 스택 주소를 얻을 수 있다.

한편, 스택은 다음과 같은 구조를 가진다.
```c
    index -2         : 0x7fffffffdf30
    read ret address : 0x7fffffffdf48
    update_note rsp  : 0x7fffffffdf50
        Note addr    : 0x7fffffffdf58
        index var    : 0x7fffffffdf60
        ret address  : 0x7fffffffdf78
    index -1         : 0x7fffffffdf90 - 0x30 = 0x7fffffffdf60
    main rsp         : 0x7fffffffdf80
    index  0         : 0x7fffffffdf90
    index 10         : 0x7fffffffe170
    main rbp         : 0x7fffffffe180 -> ret address: 0x7fffffffe188
```
-2 인덱스를 이용하면, `read` 함수의 반환 주소를 덮어쓸 수 있음을 확인할 수 있다.<br>
하지만 덮어쓸 수 있는 공간의 크기가 다소 작으므로(`0x18`바이트),<br>`pop rbp;ret`와 `leave;ret`을 활용하여 Stack Pivoting을 수행한 후 ROP를 수행한다.

## 새롭게 알게된 점
