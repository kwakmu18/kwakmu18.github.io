---
title:  "[Dreamhack] linked-list"
search: true
categories: ['Linux', 'Linux-Userland']
last_modified_at: 2025-04-25
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/198">https://dreamhack.io/wargame/challenges/198</a>

## 문제 설명
이제 막 자료구조를 배운 드림이는 단일 linked list로 사람의 개인정보를 저장하는 프로그램을 만들었어요. 그리고 자랑을 하고싶어서 자신이 만든 프로그램을 서버에서 돌려서 누구나 사용해볼 수 있도록 했습니다. 그런데 코드에 오타가 있네요...? 드림이는 아직 오타가 난줄 모르고 있습니다. 드림이가 알아채기 전에 취약점을 찾고 flag를 읽으세요.

## 문제 분석
- 이름을 입력받고 출력하는 과정에서 Format String Bug가 발생한다. 이를 이용해서 libc나 stack canary, stack 주소 등을 leak할 수 있다.
- 연결 리스트를 구성하는 구조체는 다음과 같은 형태를 가지고 있다.
```c
struct USER {
    char number[8];
    char name[16];
    char phone[16];
    char etc[256];
    char next[8];
};
```
    - 하지만 edit 함수로 특정 연결 리스트 항목을 수정할 때, etc에 `0x108`바이트만큼 입력할 수 있으므로 특정 항목의 `next` 포인터를 조작할 수 있다.
    - 이를 이용하여 aaw(arbitrary address write)를 수행할 수 있다.

## 새롭게 알게된 점