---
title:  "WinDbg 심볼 서버 설정"
search: true
categories: [Windows, WinDbg]
last_modified_at: 2025-03-23
comments: true
published: true
---

- WinDbg에서는 심볼 파일이 저장될 경로와, 심볼 파일을 다운로드할 서버의 주소를 직접 지정할 수 있다.
  - 이 글에서는 WinDbg Classic이 아닌 최신의 WinDbg를 기준으로 설명합니다.
- WinDbg를 실행한 후, 파일 - Settings - Debugging Settings 탭으로 들어간다. 기본적으로는 다음과 같이 되어 있을 것이다. <br>
  <img src="/assets/img/windbg/5.png" class="post-image">
- "Default symbol path: " 부분에 다음과 같이 입력 후 저장한다.
  - `srv*심볼_저장_경로*심볼_서버_주소`
  - Microsoft에서 제공하는 심볼 서버 주소는 "https://msdl.microsoft.com/download/symbols"이므로 아래와 같이 입력하면 된다.
  - `srv*C:\SYMBOLS*https://msdl.microsoft.com/download/symbols`
<br>

- 이제 다음부터 `.reload /f` 커맨드를 통해 심볼 로드를 시도하면, "https://msdl.microsoft.com/download/symbols"로부터 심볼 파일을 다운로드하여 `C:\SYMBOLS` 경로에 저장한다. 저장된 모습은 아래와 같다.<BR>
  <img src="/assets/img/windbg/6.png" class="post-image">