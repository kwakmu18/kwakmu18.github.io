---
title:  "[Dreamhack] Doodle-Note"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-24
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1002">https://dreamhack.io/wargame/challenges/1002</a>

## 문제 설명
### Description
저는 낙서하는 걸 좋아해요. 여러분도 그런가요?

### Environment
```
    Arch:     i386-32-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

## 문제 분석
- 노트를 생성할 때는 `mmap` 함수가 사용되며, 다음과 같이 구조체가 저장된다.
```c
Page * page = reinterpret_cast<Page *>(addr);
page->addr = addr;
page->size = page_size;
page->contents = reinterpret_cast<char *>(addr) + sizeof(Page);
memcpy(page->contents, contents.c_str(), contents.size());
```
  - 콘텐츠의 길이를 `0x1000`(한 페이지 크기)의 배수로 설정할 경우 `page`의 크기는 콘텐츠의 길이와 동일하다.
  - 하지만 `memcpy` 함수를 이용해 콘텐츠를 복사할 때는 `addr + sizeof(Page)` 위치에 복사하므로, 최대 `0xc`바이트만큼 오버플로우가 발생할 수 있다.
  - 문자열의 널바이트를 덮어써 청크의 주소를 알아낼 수 있고, 인접한 Page 구조체의 `addr`, `size`, `contents` 주소를 조작할 수 있다.
- Page 구조체를 이용할 때는 다음과 같은 검증이 있다.
```c
char * contents = note.at(page_idx)->contents;
if (reinterpret_cast<char*>(note.at(page_idx)->addr) + sizeof(Page) != contents) {
    cout << "[!] No Hack! (get_contents)\n";
    exit(0);
}
```
  - `addr+0xc == contents` 검증이 있다.
- 청크의 주소를 알아냈다면, 일정 오프셋을 더하거나 빼 libc의 주소를 구할 수 있다.
  - 오프셋 값은 환경에 따라 달라지므로 제공되는 Dockerfile을 빌드하여 확인하는 것을 추천한다.
  - libc의 주소를 구했다면, 인접한 Page 구조체의 `addr`, `contents`를 각각 `environ-0xc`, `environ` 주소로 조작한 후 출력하여 스택 주소를 알아낸다.
- 스택 주소를 알아냈다면 마찬가지로 인접한 Page 구조체의 `addr`, `contents`를 각각 `stack-0x200-0xc`, `stack`으로 조작한 후 출력하여 `main` 함수의 반환 주소 위치를 찾는다.
- `main` 함수의 반환 주소 위치를 찾아냈다면 인접한 Page 구조체의 `addr`, `contents`를 각각 `ret-0x200-0xc`, `ret`으로 조작한 후 rewrite 기능을 이용해 해당 위치에 ROP payload를 입력함으로써 셸을 획득할 수 있다.

## 새롭게 알게된 점
- <a target="_blank" href="https://wiimdy.medium.com/doodle-note-8bb300f6e0b0">참고한 블로그</a>