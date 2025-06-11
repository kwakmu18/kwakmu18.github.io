---
title:  "libc GOT overwrite"
search: true
categories: ['Linux', 'Userland']
last_modified_at: 2025-04-08
comments: true 
published: true
---

### RELRO
- 메모리 보호 기법 중 **RELRO(RELocate Read-Only)**라는 것이 있다. 이는 쓰기 권한이 불필요한 데이터 영역에 쓰기 권한을 제거한다.
- RELRO 적용 대상 중 유심히 여겨봐야 할 것은 **GOT(Global Offset Table)**이다.
    - 현대의 바이너리 실행 환경에서는 **ASLR(Address Space Layout Randomize)**이 적용되어, 공유 라이브러리의 매핑 주소가 랜덤하게 변한다.
    - 바이너리에서 라이브러리 함수를 호출하고자 하는데, 호출할 때마다 그 함수의 주소를 찾으려고 하면 매우 번거롭고 시간이 많이 들 것이다.
    - 따라서 데이터 영역에 **PLT(Procedure Linkage Table)**와 GOT라는 테이블을 두고, 이를 라이브러리 함수 호출에 사용한다.
    - 바이너리에서 `printf` 함수를 호출하면 실제로는 `printf@plt`를 호출한다.
```
   0x555555555177 <main+30>    mov    rsi, rax
   0x55555555517a <main+33>    lea    rax, [rip + 0xe90]                RAX => 0x555555556011 ◂— 'printf: %p\n'
   0x555555555181 <main+40>    mov    rdi, rax
   0x555555555184 <main+43>    mov    eax, 0                            EAX => 0
   0x555555555189 <main+48>    call   printf@plt                  <printf@plt>
```
    - PLT는 호출한 함수에 맞는 GOT 영역에 작성되어 있는 함수 주소로 점프한다.
```
pwndbg> x/5i 0x555555555060
=> 0x555555555060 <puts@plt>:           endbr64
     0x555555555064 <puts@plt+4>:         bnd jmp QWORD PTR [rip+0x2f5d]        # 0x555555557fc8 <puts@got.plt>
     0x55555555506b <puts@plt+11>:        nop    DWORD PTR [rax+rax*1+0x0]
```

### No/Partial vs. Full
- 바이너리에 적용된 RELRO가 No RELRO 혹은 Partial RELRO인지 Full RELRO인지에 따라 동작 방식이 달라지게 된다.

#### No RELRO/Partial RELRO
- No RELRO/Partial RELRO는 특정 함수가 호출되는 시점에 해당 함수의 주소를 찾는 **Lazy Binding**이 적용된다.
- 함수 주소를 찾기 위해 `_dl_runtime_resolve_xsavec` 함수가 호출된다.
```
0x401050       <puts@plt>                        endbr64
0x401054       <puts@plt+4>                      bnd jmp qword ptr [rip + 0x2fbd]   <0x401030>
↓
0x401030                                         endbr64
0x401034                                         push   0
0x401039                                         bnd jmp 0x401020                   <0x401020>
↓
0x401020                                         push   qword ptr [rip + 0x2fe2]
0x401026                                         bnd jmp qword ptr [rip + 0x2fe3]   <_dl_runtime_resolve_xsavec>
↓
0x7ffff7fd8d30 <_dl_runtime_resolve_xsavec>      endbr64
0x7ffff7fd8d34 <_dl_runtime_resolve_xsavec+4>    push   rbx
0x7ffff7fd8d35 <_dl_runtime_resolve_xsavec+5>    mov    rbx, rsp                    RBX => 0x7fffffffdf50 ◂— 0
0x7ffff7fd8d38 <_dl_runtime_resolve_xsavec+8>    and    rsp, 0xffffffffffffffc0     RSP => 0x7fffffffdf40 (0x7fffffffdf50 & -0x40)
```
- 해당 함수의 주소를 찾은 후에는 GOT 영역에 작성을 해줘야 하므로, No RELRO/Partial RELRO 바이너리에는 GOT 영역에 쓰기 권한이 있다.
```
pwndbg> got
Filtering out read-only entries (display them with -r or --show-readonly)
State of the GOT of /mnt/d/kwakmu18/CTF/wargame/toxic_malloc/deploy/test2:
GOT protection: Partial RELRO | Found 1 GOT entries passing the filter
[0x404018] puts@GLIBC_2.2.5 -> 0x401030 ◂— endbr64
pwndbg> vmmap 0x404018
LEGEND: STACK | HEAP | CODE | DATA | WX | RODATA
               Start                End Perm     Size Offset File
            0x403000           0x404000 r--p     1000   2000 /mnt/d/kwakmu18/CTF/wargame/toxic_malloc/deploy/test2
►         0x404000           0x405000 rw-p     1000   3000 /mnt/d/kwakmu18/CTF/wargame/toxic_malloc/deploy/test2 +0x18
      0x7ffff7d88000     0x7ffff7d8b000 rw-p     3000      0 [anon_7ffff7d88]
```

#### Full RELRO
- Full RELRO는 바이너리 시작 시점에 미리 함수 주소를 모두 찾는 **Now Binding**이 적용된다.
- 바이너리 실행 중에는 GOT가 변경될 일이 없으므로 GOT 영역에 쓰기 권한이 없다. (읽기 전용)
```
pwndbg> got -r
State of the GOT of /mnt/d/kwakmu18/CTF/wargame/toxic_malloc/deploy/test:
GOT protection: Full RELRO | Found 7 GOT entries passing the filter
[0x555555557fc8] puts@GLIBC_2.2.5 -> 0x7ffff7e0be50 (puts) ◂— endbr64
[0x555555557fd0] __libc_start_main@GLIBC_2.34 -> 0x7ffff7db4dc0 (__libc_start_main) ◂— endbr64
[0x555555557fd8] _ITM_deregisterTMCloneTable -> 0
[0x555555557fe0] printf@GLIBC_2.2.5 -> 0x7ffff7deb6f0 (printf) ◂— endbr64
[0x555555557fe8] __gmon_start__ -> 0
[0x555555557ff0] _ITM_registerTMCloneTable -> 0
[0x555555557ff8] __cxa_finalize@GLIBC_2.2.5 -> 0x7ffff7dd09a0 (__cxa_finalize) ◂— endbr64
pwndbg> vmmap 0x555555557fc8
LEGEND: STACK | HEAP | CODE | DATA | WX | RODATA
               Start                End Perm     Size Offset File
      0x555555556000     0x555555557000 r--p     1000   2000 /mnt/d/kwakmu18/CTF/wargame/toxic_malloc/deploy/test
►   0x555555557000     0x555555558000 r--p     1000   2000 /mnt/d/kwakmu18/CTF/wargame/toxic_malloc/deploy/test +0xfc8
      0x555555558000     0x555555559000 rw-p     1000   3000 /mnt/d/kwakmu18/CTF/wargame/toxic_malloc/deploy/test
```

### GOT Overwrite?
- 바이너리 공격 기법 중 **GOT Overwrite**가 있다. GOT 영역에 쓰기 권한이 있고, AAW(Arbitrary Address Write) Primitive가 있을 때 GOT 영역의 임의 함수 주소를 덮어써서 원하는 함수를 실행할 수 있는 공격 기법이다.
- `printf("/bin/sh")`를 호출하여 "/bin/sh"를 출력하고자 한다.
    - 위 함수를 호출하면 `printf@plt`가 호출되어 `printf` 함수의 GOT 영역에 작성된 주소를 참조할 것이다.
    - 만약 `printf` 함수의 GOT가 `system` 함수의 주소로 조작되어 있다면? 실제로는 `system("/bin/sh")`가 호출되어 문자열을 출력하지 않고 셸을 실행하게 된다.

### libc GOT Overwrite?
- 바이너리는 컴파일하면 기본적으로는 Full RELRO가 적용되므로 GOT 영역에 쓰기 권한이 없다. 하지만 Ubuntu 22.04까지의 libc 라이브러리는 checksec 유틸리티로 확인해보면 Partial RELRO가 적용되어 있는 것을 확인할 수 있다.
```
❯ checksec /lib/x86_64-linux-gnu/libc.so.6
[*] '/lib/x86_64-linux-gnu/libc.so.6'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        PIE enabled
    SHSTK:      Enabled
    IBT:        Enabled
```
- pwndbg로 일반 바이너리를 디버깅할 때, `got -p libc` 명령어를 입력하면 libc 라이브러리의 GOT를 확인할 수 있다.
```
pwndbg> got -p libc
Filtering by lib/objfile path: libc
Filtering out read-only entries (display them with -r or --show-readonly)
State of the GOT of /lib/x86_64-linux-gnu/libc.so.6:
GOT protection: Partial RELRO | Found 54 GOT entries passing the filter
[0x7ffff7fa5018] *ABS*+0xa8720 -> 0x7ffff7f28960 (__strnlen_avx2) ◂— endbr64
[0x7ffff7fa5020] *ABS*+0xaaf80 -> 0x7ffff7f24590 (__rawmemchr_avx2) ◂— endbr64
[0x7ffff7fa5028] realloc@@GLIBC_2.2.5 -> 0x7ffff7db3030 ◂— endbr64
[0x7ffff7fa5030] *ABS*+0xa9ac0 -> 0x7ffff7f267b0 (__strncasecmp_avx) ◂— endbr64
[0x7ffff7fa5038] _dl_exception_create@GLIBC_PRIVATE -> 0x7ffff7db3050 ◂— endbr64
[0x7ffff7fa5040] *ABS*+0xa97d0 -> 0x7ffff7f2b780 (__mempcpy_avx_unaligned_erms) ◂— endbr64
[0x7ffff7fa5048] *ABS*+0xc5b00 -> 0x7ffff7f2bed0 (__wmemset_avx2_unaligned) ◂— endbr64
[0x7ffff7fa5050] calloc@@GLIBC_2.2.5 -> 0x7ffff7db3080 ◂— endbr64
[0x7ffff7fa5058] *ABS*+0xa8b00 -> 0x7ffff7f23800 (__strspn_sse42) ◂— endbr64
[0x7ffff7fa5060] *ABS*+0xa93f0 -> 0x7ffff7f242c0 (__memchr_avx2) ◂— endbr64
[0x7ffff7fa5068] *ABS*+0xa95a0 -> 0x7ffff7f2b7c0 (__memmove_avx_unaligned_erms) ◂— endbr64
[0x7ffff7fa5070] *ABS*+0xc59b0 -> 0x7ffff7f2c4c0 (__wmemchr_avx2) ◂— endbr64
[0x7ffff7fa5078] *ABS*+0xa9950 -> 0x7ffff7f2a9a0 (__stpcpy_avx2) ◂— endbr64
[0x7ffff7fa5080] *ABS*+0xc5a40 -> 0x7ffff7f2c0c0 (__wmemcmp_avx2_movbe) ◂— endbr64
[0x7ffff7fa5088] _dl_find_dso_for_object@GLIBC_PRIVATE -> 0x7ffff7db30f0 ◂— endbr64
[0x7ffff7fa5090] *ABS*+0xa88d0 -> 0x7ffff7f2a040 (__strncpy_avx2) ◂— endbr64
[0x7ffff7fa5098] *ABS*+0xa86a0 -> 0x7ffff7f287e0 (__strlen_avx2) ◂— endbr64
...
```
- 이 중에서 `__strlen_avx2`에 주목해보자. 이는 우리가 아는 문자열 길이 계산 함수인 `strlen`이다.
    - `printf("Hello World!\n");`를 호출했을 때, 내부적으로 문자열의 길이를 계산하기 위해 `__strlen_avx2`를 호출한다. 브레이크포인트를 걸었을 때, 첫 번째 인자 `RDI`에 우리가 출력하고자 하는 문자열 자체가 전달되었음을 확인할 수 있다.
        <img src="/assets/img/linux/1.png" class="post-image">
    - 혹은 `printf("%s\n", "Hi!");`와 같이 `%s` 포맷 스트링으로 전달된 문자열 역시 `__strlen_avx2`가 호출된다. 브레이크포인트를 걸었을 때, 첫 번째 인자 `RDI`에 우리가 `%s` 포맷 스트링으로 출력하고자 하는 문자열 "Hi"가 전달되었음을 확인할 수 있다.
        <img src="/assets/img/linux/2.png" class="post-image">
- 여기서 libc의 GOT 영역은 쓰기 권한이 있으므로, 만약 `__strlen_avx2` 함수의 주소가 `system` 함수의 주소로 조작되어 있다면?
    - 바이너리가 `printf("/bin/sh")` 혹은 `printf("%s\n", "/bin/sh")`를 호출하도록 하면 셸을 획득할 수 있다!

### Experiment

- 실제로 이를 확인해보자. gdb로 GOT 영역과 함수 주소 오프셋을 확인한 후, C 코드 상에서 libc의 GOT 영역을 직접 덮어쓰도록 코드를 작성한다.

```c
#include <stdio.h>

int main(void) {
    unsigned char *libc_base = printf - 0x606f0;
    unsigned char *strlen_got = libc_base + 0x21a098;
    unsigned char *system_addr = libc_base + 0x50d70;

    printf("libc_base: %p\n", libc_base);
    printf("strlen_got: %p\n", strlen_got);
    printf("system_addr: %p\n", system_addr);

    printf("This is Before\n");
    printf("/bin/sh\n");

    *(long long *)strlen_got = (long long)system_addr;

    printf("This is After\n");
    printf("/bin/sh\n");
}
```

<img src="/assets/img/linux/3.png" class="post-image">

- 조작 전에는 "This is Before" 문자열과, "/bin/sh" 문자열이 정상적으로 출력된다.
- 조작 후에는 libc가 `__strlen_avx2` 함수 본연의 기능을 잃어버리기 때문에, 문자열 길이를 제대로 측정하지 못하여 출력이 깨지기 시작한다.
- 마지막 줄에서 `printf("/bin/sh\n")`가 실행되어 결국 셸을 획득한 것을 확인할 수 있다.