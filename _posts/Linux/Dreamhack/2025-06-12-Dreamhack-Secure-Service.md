---
title:  "[Dreamhack] Secure Service"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-12
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1249">https://dreamhack.io/wargame/challenges/1249</a>

## 문제 설명
We made a nice _"sandbox"_ program. feel free to attack our service :)

## 문제 분석
- 2번을 선택하는 경우, 최대 0x80바이트만큼의 shellcode를 입력 후 실행할 수 있다. 실행하기 전 `sandbox` 함수가 호출된다.
  - `prctl(PR_SET_NO_NEW_PRIVS, 1LL)`를 호출하여 현재 프로세스와 자식 프로세스들의 권한 상승이 불가하도록 제한한다.
  - `prctl(PR_SET_SECCOMP, seccomp_mode, &prog)`를 호출하여 seccomp를 적용한다.
    - `seccomp_mode` 변수에는 1이 저장되어 있다.
    - 1은 `SECCOMP_MODE_STRICT`로, `write`, `read`, `sigreturn`, `exit` 시스템 콜만 호출하도록 제한한다.
    - seccomp를 설정할 때 두 번째 인자가 `SECCOMP_MODE_STRICT`일 경우 세 번째 인자(필터 프로그램 주소) `prog`은 무시된다.

- 1번을 선택하는 경우, data 영역의 배열 `g_buf`에 최대 278바이트만큼 입력할 수 있다.
  - 이때, data 영역에서 버퍼 오버플로우가 발생하여, 위에서 봤던 `seccomp_mode`와 `prog` 필터 프로그램의 필터를 덮어쓸 수 있다.
  - 이를 이용하여 `seccomp_mode`를 2(`SECCOMP_MODE_FILTER`)로 조작하고, `prog` 필터 프로그램의 필터를 다음과 같이 조작하면, 모든 시스템 콜을 허용하도록 할 수 있다.
  ```
  line  CODE  JT   JF      K
  =================================
  0000: 0x06 0x00 0x00 0x7fff0000  return ALLOW
  ```

## 새롭게 알게된 점
- `prctl(PR_SET_SECCOMP, seccomp_mode, &prog)`
  - `prog` 구조체
    ```c
    struct sock_fprog {
        unsigned short     len;     /* BPF 인스트럭션 개수 */
        struct sock_filter *filter; /* BPF 인스트럭션들의 배열의 포인터 */
    };
    ``` 
  - `sock_filter` 구조체
    ```c
    struct sock_filter {            /* 필터 블록 */
        __u16 code;                 /* 실제 필터 코드 */
        __u8  jt;                   /* 참 점프 */
        __u8  jf;                   /* 거짓 점프 */
        __u32 k;                    /* 범용 다용도 필드 */
    };
    ```