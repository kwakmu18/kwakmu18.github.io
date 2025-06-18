---
title:  "[Dreamhack] startlink"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-18
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1918">https://dreamhack.io/wargame/challenges/1918</a>

## 문제 설명
Starlink 대신 Startlink 어떠세요?<br>
[April 25, 2025 6:40 PM] 의도되지 않은 풀이 수정<br>
[April 25, 2025 7:24 PM] 의도되지 않은 풀이 수정 ( Thanks to keymoon )

## 문제 분석
- 각 노트는 이중 연결 리스트로 구성되며, 노트 구조체는 다음과 같은 형태를 가진다.
```c
struct note {
    struct note *bef;
    char data[0x400];
    struct note *next;
}
```
- 노트를 새롭게 생성할 때는 `note->data`에 최대 `0x400`바이트만큼 입력할 수 있지만, 이후 `edit` 메뉴로 노트의 데이터를 수정할 때는 최대 `0x408`바이트만큼 입력할 수 있어 오버플로우가 발생한다.
    - 노트 구조체의 `next` 포인터를 조작할 수 있으므로, 이를 got 영역으로 조작하여 libc base를 구한다.
    - libc base를 구했다면 libc의 `environ` 변수 주소를 구해 출력하여 스택 주소를 구한다.
    - 스택 주소를 구했다면 `main` 함수의 반환 주소 오프셋을 찾고, 반환 주소를 ROP Payload로 조작하여 셸을 획득한다. 

## 새롭게 알게된 점