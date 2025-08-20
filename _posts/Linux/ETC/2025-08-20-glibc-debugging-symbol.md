---
title:  "libc/ld 디버깅 심볼 받아오기"
search: true
categories: ['Linux']
last_modified_at: 2025-08-20
comments: true 
published: true
---

워게임/CTF를 풀 때 제공된 Dockerfile로 환경을 구성한 후 꺼낸 glibc는 디버깅 심볼이 포함되어 있지 않은 경우가 많다.<br>
예를 들어, 아래 사진처럼 `__printf_function_table`과 같은 심볼이 존재하지 않아 오프셋을 알아내기 힘들다.
<img src="/assets/img/linux/11.png" class="post-image">

그럴 때는 우선 꺼내온 libc를 실행해보면 버전 정보를 알 수 있으며, `file` 명령어로 확인해보면 BuildID 해시 정보를 볼 수 있다.
<img src="/assets/img/linux/12.png" class="post-image">

- 버전은 `GLIBC 2.31-0ubuntu9.17 (amd64)`
- 해시는 `0323ab4806bee6f846d9ad4bccfc29afdca49a58`

이 정보를 가지고, 구글에 다음과 같이 검색한 후 파일을 다운로드받는다.<br>
`libc6-dbg_2.31-0ubuntu9.17_amd64.deb`

파일을 다운로드받았다면, 다음 명령어를 활용하여 패키지 내용물을 압축해제한다. <br>
`dpkg -x libc6-dbg_2.31-0ubuntu9.17_amd64.deb ./`

압축 해제가 완료되면, `<경로>/usr/lib/debug/.build-id` 내에 다음과 같은 폴더들이 있는 것을 볼 수 있다.
<img src="/assets/img/linux/13.png" class="post-image">

어디에 들어가야하나 싶겠지만, 아까 확인했던 BuildID 해시가 "03"으로 시작하므로 03에 들어가면 된다.
<img src="/assets/img/linux/14.png" class="post-image">

BuildID 해시가 `0323ab4806bee6f846d9ad4bccfc29afdca49a58`이었으므로, "03" 뒷부분인 "23ab4806bee6f846d9ad4bccfc29afdca49a58.debug"가 우리가 찾던 디버깅 심볼이 포함된 libc 바이너리이다.

이를 gdb로 열고, 심볼을 찾아보면 잘 나오는 것을 확인할 수 있다.
<img src="/assets/img/linux/15.png" class="post-image">

ld 역시 동일한 방법으로 찾을 수 있다.
<img src="/assets/img/linux/16.png" class="post-image">