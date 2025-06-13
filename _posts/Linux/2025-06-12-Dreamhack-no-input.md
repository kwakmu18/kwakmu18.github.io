---
title:  "[Dreamhack] no-input"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-12
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1343">https://dreamhack.io/wargame/challenges/1343</a>

## 문제 설명
"All user input is error." - Elon Musk

## 문제 분석
- no-input 바이너리는 root 소유 setuid 바이너리이며, 다음과 같은 동작이 수행된다.
  - `init` 함수에서 `setreuid`, `setregid` 함수를 호출하여 현재 프로세스는 완전히 루트 권한이 된다.
  - `login` 함수를 호출하여 "guest:guest"로 로그인을 시도한다.
    - `getpwnam` 함수를 호출하여, 사용자 이름("guest")을 기반으로 passwd 구조체를 생성한다.
    - 해당 시스템은 비밀번호 해시 값을 "/etc/shadow"에 저장하므로, passwd 구조체의 비밀번호 필드에는 "x"가 들어 있다.
    - 이어서 `getspnam` 함수를 호출하여, 사용자 이름("guest")을 기반으로 비밀번호 해시값을 "/etc/shadow"로부터 가져온다.
    - 직접 계산한 해시값과 비교하여 일치하는 경우 `LOGIN_SUCCESS`를 반환하고, 일치하지 않는 경우 `LOGIN_FAILED`를 반환한다.
  - 로그인에 성공한 경우 `print_banner` 함수를 호출하여 "/etc/banner" 파일의 내용을 표준 출력에 출력한다.
  - `set_priv` 함수를 호출하여 권한을 "guest" 계정으로 설정한다.
    - 해당 함수에서도 `getpwnam` 함수를 호출하여 passwd 구조체를 가져온다.
    - passwd 구조체로부터 uid와 gid를 추출하고 `setreuid`, `setregid` 함수를 호출하여 권한을 설정한다.
  - `execl` 함수를 호출하여 "/bin/sh"를 실행한다.
- `getpwnam` 함수는 "/etc/passwd" 파일로부터 정보를 추출하여 passwd 구조체를 생성하므로, 내부적으로 `open` 시스템 콜이 호출된다.
  - 만약 파일 디스크립터에 여유 공간이 없는 경우, `getpwnam` 함수 호출은 실패하게 된다.
  - 하지만 `print_banner` 함수 호출 이후 `set_priv` 함수에서는 `getpwnam` 함수가 실패하더라도 프로그램이 계속해서 실행되므로, 권한이 "guest"로 설정되지 않은 채로 "/bin/sh"가 실행될 수 있다. 이 경우 "/bin/sh"는 guest 계정이 아닌 admin 계정으로 실행되어 "/flag" 파일을 읽을 수 있다.

## 새롭게 알게된 점
- `getpwnam` 함수
```c
struct passwd *getpwnam(const char *name);
```
  - 사용자 이름 `name`을 기반으로 "/etc/passwd" 파일을 파싱하여 passwd 구조체를 반환한다.

- `getspnam` 함수
```c
struct spwd *getspnam(const char *name);
```
  - "/etc/shadow"를 사용하는 시스템에서는 "/etc/passwd"의 비밀번호 필드에 "x"가 저장되어 있다.
  - `getspnam` 함수는 이러한 시스템에서 "/etc/shadow" 파일을 파싱하여 spwd 구조체를 반환한다.

- `sendfile` 시스템 콜
```c
ssize_t sendfile(int out_fd, int in_fd, off_t *offset, size_t count);
```
  - `out_fd` 파일 디스크립터로부터 `in_fd` 파일 디스크립터로 `offset` 오프셋부터 `count`바이트만큼 데이터를 복사한다.
  - 커널 내에서 복사가 이루어지므로 `read`, `write` 시스템 콜 조합보다 효율적이다.