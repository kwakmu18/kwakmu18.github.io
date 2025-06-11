---
title:  "[Dreamhack] DreamSanta's Present"
search: true
categories: ['Linux', 'Linux-Userland']
last_modified_at: 2025-04-25
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/404">https://dreamhack.io/wargame/challenges/404</a>

## 문제 설명
크리스마스 기념 드림산타가 선물을 준비했어요!! 취약점, 플래그, 쉘도 맘대로 준다던데..?

## 문제 분석
- 1번 메뉴를 이용하면 `gets` 함수를 이용하여 입력할 수 있어 스택 버퍼 오버플로우가 발생한다.
    - 하지만 canary, libc 등을 leak할 방법이 없으므로 활용이 불가하다.
- 2번 메뉴를 이용하면 "/home/ctf/flag" 파일을 읽어온 후 0~2번째 인덱스까지의 데이터만을 보여준다.
    - 여기서 중요한 것은, 파일을 연 후 닫지 않는다는 것이다.
- 3번 메뉴를 이용하면 `system("/bin/sh")`를 실행해준다. 하지만 권한이 root가 아니므로 플래그 파일을 읽을 수 없다.
    - 하지만 셸을 획득했고, 홈 디렉터리에 쓰기 권한이 있으므로 이를 이용해 임의 바이너리를 실행할 수 있다.
    - 파일 디스크립터의 경우 기본적으로 자식 프로세스에 상속되므로, "/home/ctf/flag" 파일의 파일 디스크립터 값을 이용하여 read-write하는 바이너리를 작성하고 셸에서 실행하면 플래그를 읽어올 수 있다.

## 새롭게 알게된 점