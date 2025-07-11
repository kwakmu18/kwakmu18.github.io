---
title:  "[Dreamhack] chain-lighting"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-06-19
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1935">https://dreamhack.io/wargame/challenges/1935</a>

## 문제 설명
Magic: the Assemblage Prototype!<br>
When time is running out and you have not enough damage in your hand...

Flag format: `DH{...}`

## 문제 분석
- 카드 구조체는 다음과 같은 형태를 가진다.
```c
struct card {
    int num;
    char name[0x24];
    void *target;      // enemy or self
    void *func;        // card resolve function ptr
    struct card *next; // stack linked-list
}
```

    - `func` 필드에는 스택이 resolve될 때 호출될 함수 포인터가 저장된다.

- 카드를 사용(스택에 push)하기 전 카드의 이름(`name` 필드)을 수정할 수 있는데, 최대 `0x3c`바이트만큼 입력할 수 있으므로 버퍼 오버플로우가 발생한다.
    - `target`, `func`, `next` 포인터들을 모두 조작할 수 있다.
    - `func` 포인터를 조작할 경우 임의 함수를 호출할 수 있을 것으로 기대했으나, resolve 과정에서 `registered_effects` 배열에 포함되는 함수들만 호출할 수 있도록 검사하는 과정이 있으므로 이 방법은 불가능하다. (`resolve_lightningbolt`, `resolve_counterspell` 함수만 호출 가능)
    - 다만 카드 이름 출력 과정에서 오버플로우를 이용하여 `func` 주소까지 출력하도록 할 수 있으므로, 여기서 PIE base를 얻을 수 있다.
- 스택이 비어 있는 경우, 카드를 스택에 push할 때 `next` 필드는 초기화하지 않으므로 조작한 `next` 포인터가 그대로 유지된다.
    - 4번 메뉴를 이용하면 bss 영역의 `0x100` 크기 배열에 입력할 수 있는데, 이곳에 fake 카드 구조체들을 입력 및 `next` 포인터로 서로 연결하고, 기존 카드의 `next` 포인터를 해당 영역의 주소로 조작하면 최대 8번의 lightning bolt를 사용할 수 있다.
    - 상대방의 체력은 20이고, lightning bolt를 8번 사용하면 3씩 8번 총 24를 감소시킬 수 있으므로 승리하여 셸을 획득할 수 있다.

## 새롭게 알게된 점