---
title:  "[Dreamhack] iofile_vtable"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-06-25
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/56">https://dreamhack.io/wargame/challenges/56</a>

## 문제 설명

### Description
이 문제는 서버에서 작동하고 있는 서비스(iofile_vtable)의 바이너리와 소스 코드가 주어집니다.<br>
프로그램의 취약점을 찾고 익스플로잇해 get_shell 함수를 실행시키세요.<br>
셸을 획득한 후, "flag" 파일을 읽어 워게임 사이트에 인증하면 점수를 획득할 수 있습니다.<br>
플래그의 형식은 DH{...} 입니다.

### Environment
```
Ubuntu 16.04
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

## 문제 분석
- Ubuntu-16.04 버전이므로 _IO_FILE 구조체의 `vtable` 필드에 대한 검증이 없다.
- 4번 메뉴를 이용하면 `stderr+1` 위치에 8바이트를 입력할 수 있는데, 이는 곧 `stderr` 파일 구조체의 `vtable` 필드이다.
  - 바이너리를 처음 실행했을 때 입력할 수 있는 8바이트 `name` 배열에 `get_shell` 함수의 주소를 입력해둔다.
  - `stderr` 파일 구조체의 `vtable`을 `name-0x38` 주소로 조작한 후 2번 메뉴를 이용하여 `stderr` 출력을 유도한다.
    - `name-0x38`인 이유는, `fprintf` 함수를 호출했을 때 `vtable` 상에서 참조되는 함수인 `_IO_file_xsputn` 함수가 `vtable`로부터 `0x38`만큼 떨어져 있기 때문이다.

## 새롭게 알게된 점