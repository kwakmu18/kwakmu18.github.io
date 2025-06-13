---
title:  "[Dreamhack] Santa House"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-12
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1071">https://dreamhack.io/wargame/challenges/1071</a>

## 문제 설명
산타 할아버지가 크리스마스를 맞아 드림이들을 모두 집에 초대해서 선물을 나눠주신대요!<br>
착한 아이는 어쩌면 비밀스러운 선물을 받을 수 있을지도 몰라요. 시간은 넉넉하니 산타 할아버지 댁에서 여유롭게 즐겨주세요!

혹시 필요하다면 pwntools 익스플로잇 코드에 context.timeout=pwnlib.timeout.maximum를 추가하세요.

## 문제 분석
- main 함수의 스택 구조는 다음과 같다.
```c
  char buf[8]; // rbp-0x48
  char v5[16]; // rbp-0x40
  char v6[40]; // rbp-0x30
  ssize_t v7;  // rbp-0x8
```
- 첫 입력은 `buf`에 최대 8바이트만큼 입력한 후, 다음 코드가 실행된다.

  ```c
  int fd;

  fd = open("./flag", 1);
  read(fd, buf, 6);
  *buf ^= *buf << 12;
  ```

  - flag 파일을 `open` 함수로 열 때 권한이 `O_RDONLY(0)`가 아닌 `O_WRONLY(1)`이므로, 다음의 `read` 함수 호출은 권한 문제로 실패한다.
  - 따라서 `buf`에는 입력한 값이 그대로 남아 있다. 만약 1바이트(`\n`)만을 입력했을 경우, 쓰레기 값이 연산에 사용된다. 이때 그 쓰레기 값은 스택의 주소이다.
  - 위 연산은 다음 연산으로 역연산을 수행할 수 있다.
```py
x ^ (x << 12) ^ (x << 24) ^ (x << 36) ^ (x << 48) ^ (x << 60)
```
  - 하위 1바이트는 `\n`으로 덮여 있는데, 가장 처음 알려주는 key 값이 원래의 하위 1바이트이므로 이를 더해주면 스택 주소를 깔끔하게 복원할 수 있다.

- 두 번째 입력은 `v5`에 16바이트만큼 입력한 후 위와 동일하게 read-open-xor이 수행된다.
  - 이때 v5[8]~v5[15]에 `__libc_csu_init` 함수의 주소가 존재하므로, 이를 복원하여 PIE base를 계산할 수 있다.

- 세 번째 입력은 `v6`에 64바이트만큼 입력할 수 있어 스택 버퍼 오버플로우가 발생한다.
  - 스택 버퍼 오버플로우가 발생하는 크기가 작으므로, `leave; ret` 리턴 가젯을 활용하는 Stack Pivoting을 수행한다.
  - 이전 단계에서 얻었던 스택 주소를 활용하고, 셸을 획득하도록 ROP 페이로드를 구성하여 전송하면 셸을 획득할 수 있다.

## 새롭게 알게된 점
- 어떤 8바이트 수 `x`가 있고, `x ^ (x << 12)`를 알고 있을 때, 원래의 x를 복원하려면
```py
x ^ (x << 12) ^ (x << 24) ^ (x << 36) ^ (x << 48) ^ (x << 60)
```
  - 이는 libc에서 힙 청크의 next pointer를 관리할 때(safe linking)도 사용되는 로직이다.