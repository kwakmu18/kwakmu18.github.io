---
title:  "kdnet 사용법"
search: true
categories: 
  - WinDbg
last_modified_at: 2025-03-23
comments: true 
published: true
---

- kdnet(Kernel Debugger over Network)은 커널 디버깅을 할 때 사용하는 네트워크 기반 디버깅 프로토콜이다.
  - Windows 가상머신을 설치한 후, WinDbg를 이용해 커널 디버깅을 할 수 있다.
  - Windows SDK를 설치할 때 함께 설치된다. kdnet의 경로는 아래와 같다.
  - `C:\\Program Files (x86)\Windows Kits\10\Debuggers\x64`
<br><br>
- 가상머신의 경우 VMware나 Hyper-V, VirtualBox 등 뭐든 상관 없으나, 이 글에서는 VMware를 기준으로 한다.
- 우선 가상머신을 켜고, 위 경로에서 두 개의 파일을 복사하여 가상머신에 붙여넣는다.
  - `kdnet.exe`
  - `VerifiedNICList.xml`
- 호스트(디버깅을 하는 컴퓨터)에서 `ipconfig` 명령을 이용하여 IP 주소를 확인한다.
  - VMware 기준 "이더넷 어댑터 VMware Network Adapter VMnet~"의 IPv4 주소를 확인하면 된다.
  - 사진처럼 2개의 어댑터가 나올 수 있는데, 가상머신에서 ping을 해봤을 때 응답이 오는 IPv4 주소를 선택한다.<br>
  <img src="/assets/img/windbg/7.png" class="post-image">
  - 여기서는 "이더넷 어댑터 VMware Network Adapter VMnet1"의 주소인 `192.168.30.1`이 정답이었다.<br>
  <img src="/assets/img/windbg/8.png" class="post-image">
- 가상머신에서 cmd를 관리자 권한으로 켜고, kdnet.exe가 위치하는 디렉터리로 이동한 후 다음과 같이 명령어를 입력한다.
  - `kdnet <host-ip> <port>`
  - 포트는 50000번대 중 적당히 선택한다.
- 명령어를 입력하면 아래와 같이 key 값이 나오게 되는데, 이를 복사해둔다.<br>
  <img src="/assets/img/windbg/9.png" class="post-image">
- 이제 호스트에서 WinDbg를 켜고, 파일 - Attach to kernel 탭으로 들어가서 아까 선택했던 포트와 복사해둔 Key를 입력하고, OK를 누른다.<br>
  <img src="/assets/img/windbg/10.png" class="post-image">
- WinDbg의 Command 창을 보면 Waiting to reconnect... 라는 말과 함께 더 이상 진행되지 않는데, 가상머신을 한 번 재부팅해준다.
  - 가상머신 cmd에서 `shutdown -r -t 0` 명령어를 입력하면 재부팅할 수 있다.<br>
  <img src="/assets/img/windbg/11.png" class="post-image">
- 재부팅을 하면, WinDbg의 Command 창에서 연결에 성공했다는 메시지를 볼 수 있으며, 디버깅 대상 정보와 kernel base 주소를 확인할 수 있다.(kASLR)<br>
  <img src="/assets/img/windbg/12.png" class="post-image">
<br><br>

- VMware는 디버거 연결 상태로 재부팅을 하면 간혹 블루스크린이 발생할 수 있는데, 당황하지 말고 Command 창에 g를 입력해주자.
- 처음 디버거를 연결하면 부팅 중 갑자기 Breakpoint에 걸리는 경우가 있는데, 이때도 당황하지 말고 Command 창에 g를 입력해주면 정상적으로 진행된다.