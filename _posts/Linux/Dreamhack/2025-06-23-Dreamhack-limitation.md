---
title:  "[Dreamhack] limitation"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-23
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1953">https://dreamhack.io/wargame/challenges/1953</a>

## 문제 설명
OPEN file only if... \<redacted\>

## 문제 분석
- `mmap` 함수로 `0x1000`바이트 크기의 RWX 페이지를 할당하고, 사용자는 해당 페이지에 `read` 함수로 입력한다.
- `install_sys_filter` 함수를 호출하여 SECCOMP 필터를 적용한다. seccomp-tools로 적용된 필터를 확인해보면 다음과 같다.
```s
 line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x01 0x00 0xc000003e  if (A == ARCH_X86_64) goto 0003
 0002: 0x06 0x00 0x00 0x00000000  return KILL
 0003: 0x20 0x00 0x00 0x00000000  A = sys_number
 0004: 0x15 0x00 0x01 0x0000000f  if (A != rt_sigreturn) goto 0006
 0005: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0006: 0x15 0x00 0x01 0x000000e7  if (A != exit_group) goto 0008
 0007: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0008: 0x15 0x00 0x01 0x0000000c  if (A != brk) goto 0010
 0009: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0010: 0x15 0x00 0x01 0x00000000  if (A != read) goto 0012
 0011: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0012: 0x15 0x00 0x01 0x00000001  if (A != write) goto 0014
 0013: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0014: 0x20 0x00 0x00 0x00000000  A = sys_number
 0015: 0x15 0x00 0x03 0x00000002  if (A != open) goto 0019
 0016: 0x20 0x00 0x00 0x00000010  A = filename # open(filename, flags, mode)
 0017: 0x15 0x00 0x01 0x85c0f000  if (A != 0x85c0f000) goto 0019
 0018: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0019: 0x06 0x00 0x00 0x00000000  return KILL
``` 
    - 아키텍처는 x86_64로 고정된다.
    - 호출 가능한 시스템 콜은 `rt_sigreturn`, `exit_group`, `brk`, `read`, `write`, `open`이다.
    - `open` 시스템 콜을 호출할 때, 첫 번째 인자(파일명 문자열 주소)가 지정된 조건을 만족하지 않으면 프로그램을 중단한다.

- SECCOMP 필터 적용이 완료되면 사용자가 입력한 영역을 바이트코드로써 실행한다.
- `open`의 파일명 문자열 주소는 다음과 같은 조건을 가진다.
```c
__int64 get_rand_addr() {
  unsigned int buf; // [rsp+0h] [rbp-10h] BYREF
  int fd; // [rsp+4h] [rbp-Ch]
  unsigned __int64 v3; // [rsp+8h] [rbp-8h]

  v3 = __readfsqword(0x28u);
  buf = 0;
  fd = open("/dev/urandom", 0);
  if ( fd < 0 )
    return 0;
  read(fd, &buf, 4u);
  close(fd);
  return buf;
}
__int64 install_syscall_filter() {
    ...
    addr = get_rand_addr() & 0xFFFFF000;
    mmap((void *)addr, 0x1000u, 7, 50, -1, 0);
    ...
}
```
    - "/dev/urandom"으로부터 랜덤 4바이트를 읽어온 후, `0xFFFFF000`과 AND 연산한 값을 주소로 하는 페이지를 할당한다.
    - `open`의 파일명 문자열 주소가 해당 주소에 위치하여야만 위 필터를 통과할 수 있다.

- 위 주소(`addr`)는 스택에 저장되며, `install_syscall_filter` 함수 호출 후 곧바로 바이트코드를 실행하기 때문에, 바이트코드가 실행되는 시점에도 `addr`은 스택 영역에 그대로 남아 있다.
    - 이를 가져와 파일명을 해당 주소에 저장하고, `open` 시스템 콜의 첫 번째 인자로 해당 주소를 넘기면 필터를 통과할 수 있다.
    - 이후에는 `read` - `write` 시스템 콜을 호출하여 플래그를 읽고 출력한다.

## 새롭게 알게된 점