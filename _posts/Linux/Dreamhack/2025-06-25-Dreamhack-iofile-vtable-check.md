---
title:  "[Dreamhack] iofile_vtable_check"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-25
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/57">https://dreamhack.io/wargame/challenges/57</a>

## 문제 설명

### Description
이 문제는 서버에서 작동하고 있는 서비스(iofile_vtable_check)의 바이너리와 소스 코드가 주어집니다.<br>
프로그램의 취약점을 찾고 익스플로잇해 셸을 획득한 후, "flag" 파일을 읽으세요.<br>
"flag" 파일의 내용을 워게임 사이트에 인증하면 점수를 획득할 수 있습니다.<br>
플래그의 형식은 DH{...} 입니다.

### Environment
```
Ubuntu 18.04
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

## 문제 분석
- "/dev/urandom" 파일을 `fopen` 함수로 연 결과인 `fp` 포인터에 사용자가 `0x300`바이트만큼 입력할 수 있다.
  - 하지만 Ubuntu-18.04 버전이므로 `_IO_FILE` 구조체의 `vtable` 필드에 대한 검증이 추가되어, `vtable`에 대한 조작은 어렵다.

- 프로그램 코드를 보면 사용자로부터 입력을 받은 후 `fclose(fp);`를 호출하는데, `fclose`는 내부적으로 `_IO_file_finish` 함수를 호출한다.
- `_IO_file_jumps` 가상 함수 테이블의 바로 뒤 영역(`+0xc0`)에는 `_IO_str_jumps` 가상 함수 테이블이 존재하는데, 이는 `_IO_file_jumps`와 동일한 형태를 가지고 있고, 해당 가상 함수 테이블을 사용하여도 가상 함수 테이블 검증에 걸리지 않는다.
  - 이때 `_IO_file_finish`와 대응되는 `_IO_str_finish` 함수는 다음과 같은 형태를 가진다.
    ```c
    void _IO_str_finish (_IO_FILE *fp, int dummy)
    {
      if (fp->_IO_buf_base && !(fp->_flags & _IO_USER_BUF))
        (((_IO_strfile *) fp)->_s._free_buffer) (fp->_IO_buf_base);
      fp->_IO_buf_base = NULL;

      _IO_default_finish (fp, 0);
    }
    ```
    - `fp->_IO_buf_base`가 0이 아니고, 플래그의 `fp->_IO_USER_BUF` 비트가 0인 경우 `fp->_s._free_buffer`를 함수 포인터로 하여 호출한다. 이때 인자는 `fp->_IO_buf_base`이다.
- 파일 구조체를 `_IO_strfile` 구조체로 변환하여 보면 다음과 같다.
```c
pwndbg> p/x *(_IO_strfile *)0x00007ffff7dce680
$4 = {
  _sbf = {
    _f = {
      _flags = 0xfbad2086,
      _IO_read_ptr = 0x0,
      _IO_read_end = 0x0,
      _IO_read_base = 0x0,
      _IO_write_base = 0x0,
      _IO_write_ptr = 0x0,
      _IO_write_end = 0x0,
      _IO_buf_base = 0x0,
      _IO_buf_end = 0x0,
      _IO_save_base = 0x0,
      _IO_backup_base = 0x0,
      _IO_save_end = 0x0,
      _markers = 0x0,
      _chain = 0x7ffff7dce760,
      _fileno = 0x2,
      _flags2 = 0x0,
      _old_offset = 0xffffffffffffffff,
      _cur_column = 0x0,
      _vtable_offset = 0x0,
      _shortbuf = {0x0},
      _lock = 0x7ffff7dcf8b0,
      _offset = 0xffffffffffffffff,
      _codecvt = 0x0,
      _wide_data = 0x7ffff7dcd780,
      _freeres_list = 0x0,
      _freeres_buf = 0x0,
      __pad5 = 0x0,
      _mode = 0x0,
      _unused2 = {0x0 <repeats 20 times>}
    },
    vtable = 0x7ffff7dca2a0
  },
  _s = {
    _allocate_buffer_unused = 0xfbad2887,
    _free_buffer_unused = 0x7ffff7dce7e3
  }
}
```
  - 최하단에 `_free_buffer` 필드가 있는 것을 확인할 수 있다.
  - 로컬 환경이 Ubuntu-18.04 최신 버전이므로 해당 필드는 unused 처리되어 더 이상 사용되지 않고 있는 상태이며, `fp->_s._free_buffer)`가 호출되는 것이 아닌 `free`가 호출되도록 패치되어 있는 상태이다.
  - 하지만 서버 환경은 패치되기 이전의 상태이므로 위 방법을 이용할 수 있다.
- 따라서, 파일 구조체를 덮어쓸 때 최하단의 `_free_buffer` 필드는 `system` 함수의 주소로, `_IO_buf_base` 필드는 "/bin/sh" 문자열 주소로 한 후, vtable 필드는 `+0xc0`만큼 떨어진 `_IO_str_jumps` 구조체를 가리키도록 조작하면, 셸을 얻을 수 있다.

## 새롭게 알게된 점
- <a target="_blank" href="https://dig06161.github.io/2023/03/15/dreamhack-iofile_vtable_check/">참고한 블로그</a>