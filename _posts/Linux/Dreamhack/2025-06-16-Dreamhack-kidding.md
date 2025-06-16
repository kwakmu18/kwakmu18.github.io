---
title:  "[Dreamhack] kidding"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-16
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1679">https://dreamhack.io/wargame/challenges/1679</a>

## 문제 설명
https://www.youtube.com/watch?v=rDFUl2mHIW4

## 문제 분석
- `scanf` 함수로 스택 버퍼 오버플로우가 발생하는 바이너리를 python qiling 라이브러리로 에뮬레이팅한다.
- qiling 라이브러리 코드에 일부 수정이 이루어진 후 실행된다. (apply.diff)

  ```diff
  diff --git a/qiling/loader/elf.py b/qiling/loader/elf.py
  index 1a00bcec..8be543f5 100644
  --- a/qiling/loader/elf.py
  +++ b/qiling/loader/elf.py
  @@ -5,9 +5,11 @@
  
  import io
  import os
  +import random
  +import time
  
  from enum import IntEnum
  -from typing import AnyStr, Optional, Sequence, Mapping, Tuple
  +from typing import AnyStr, Optional, Sequence, Mapping, Tuple, Union
  
  from elftools.common.utils import preserve_stream_pos
  from elftools.elf.constants import P_FLAGS, SH_FLAGS
  @@ -70,6 +72,7 @@ class QlLoaderELF(QlLoader):
          super().__init__(ql)
  
      def run(self):
  +        random.seed(int(time.time()))
          if self.ql.code:
              self.ql.mem.map(self.ql.os.entry_point, self.ql.os.code_ram_size, info="[shellcode_stack]")
  
  @@ -286,11 +289,14 @@ class QlLoaderELF(QlLoader):
  
              return top
  
  -        def __push_str(top: int, s: str) -> int:
  +        def __push_str(top: int, s: Union[str, bytes]) -> int:
              """A convinient method for writing a string to stack memory.
              """
  +            if isinstance(s, str):
  +                return __push_bytes(top, s.encode('latin'))
  
  -            return __push_bytes(top, s.encode('latin'))
  +            if isinstance(s, bytes):
  +                return __push_bytes(top, s)
  
          # write argc
          elf_table.extend(self.ql.pack(len(argv)))
  @@ -316,7 +322,7 @@ class QlLoaderELF(QlLoader):
          # add a nullptr sentinel
          elf_table.extend(self.ql.pack(0))
  
  -        new_stack = randstraddr = __push_str(new_stack, 'a' * 16)
  +        new_stack = randstraddr = __push_str(new_stack, random.randbytes(16))
          new_stack = cpustraddr  = __push_str(new_stack, 'i686')
          new_stack = execfn      = __push_str(new_stack, argv[0])
  ```
  - 현재 시간을 시드 값으로 설정한다. (`random.seed(int(time.time()))`)
  - 기존에는 "a" 16바이트가 스택에 삽입되었으나, 코드 수정 결과 랜덤한 16바이트가 스택에 삽입된다.
    - 이때 삽입되는 16바이트는 `AT_RANDOM` 값으로, 스택 카나리가 결정될 때 사용되는 값이다.
    - 스택 카나리는 `AT_RANDOM[:8]&(~0xff)`으로 결정된다.
- 스택 카나리가 랜덤화되었으나, 시드값이 현재 시간이므로 서버와 동일한 순간에 시드를 설정하면 동일한 스택 카나리를 얻을 수 있다.
- 이후 스택 버퍼 오버플로우로 rop payload를 전송하여 실행한다.
  - 이유는 모르겠으나 `system("/bin/sh")`, `execve("/bin/sh", NULL, NULL)` 모두 호출에 실패하였다..
  - 대신 `read(0, bss, 0x40)`으로 파일명 입력 -> `open(플래그, O_RDONLY)` -> `read(3, bss, 0x50)` -> `write(1, bss, 0x50)` 순서로 rop payload를 작성하여 해결하였다.

## 새롭게 알게된 점