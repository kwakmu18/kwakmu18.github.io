---
title:  "[Dreamhack] Holymoly"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-08-17
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/544">https://dreamhack.io/wargame/challenges/544</a>

## 문제 설명
홀리몰리 과카몰리 송을 알아듣는 서비스예요.<br>
바이너리와 소스 코드가 주어집니다.<br>
프로그램을 이해하고 익스플로잇해 "flag" 파일을 읽으세요.<br>
플래그의 형식은 DH{...} 입니다.

## 문제 분석
"holymoly", "rolypoly", "monopoly", "guacamole", "robocarpoli", "halligalli", "broccoli", "bordercollie", "blueberry", "cranberry", "mystery" 들로 구성된 문자열을 전송하면, 이를 해석하여 실행하는 일종의 vm? 문제이다.
각 단어들은 다음 기능을 한다.
- "holymoly" ~ "guacamole": `ptr` 혹은 `val`을 각각 0x1000, 0x100, 0x10, 0x1 증가시킨다.
- "robocarpoli" ~ "bordercollie": `ptr` 혹은 `val`을 각각 0x1000, 0x100, 0x10, 0x1 감소시킨다.
- "blueberry": `write(1, ptr, 8)`을 실행한다. 즉, `ptr` 위치의 8바이트를 출력한다. (AAR)
- "cranberry": `*ptr = val`을 실행한다. 즉, `ptr` 위치에 `val`을 8바이트만큼 쓴다. (AAW)
- "mystery": `ptr`을 조작할지 `val`을 조작할지 결정하는 스위치 함수이다.

해당 바이너리는 PIE가 적용되어 있지 않으며, Partial RELRO가 적용되어 있다.<br>
64비트 바이너리에서 PIE가 적용되지 않으면 `0x400000` 주소에 바이너리가 적재되므로, 비교적 작은 크기의 수이다.<br>
따라서, 0x1000/0x100/0x10/0x1을 가지고도 충분히 `ptr`이 GOT 영역을 가리키게 할 수 있다.<br>
이를 이용해서, `ptr`이 GOT 영역을 가리키게 한 후 "blueberry"를 이용해 libc base를 leak한다.<br>
더 이상 leak할 것은 없으므로, `write` 함수의 GOT를 `main` 함수의 주소로 조작하여 `main` 함수를 계속해서 호출할 수 있도록 한다.

libc base를 얻었으나, 이는 `0x7xxxxxxx` 주소 영역으로 매우 큰 수이므로, `ptr`이 libc 영역의 주소를 가리키게 하기 어렵다.<br>
따라서, GOT를 8바이트 한번에 덮지 말고, 1바이트씩 덮어쓰면 효율적으로 GOT를 덮어쓸 수 있다.<br>

`main` 함수가 실행되면 항상 `Init` 함수가 호출되어 `setvbuf`함수가 호출되는데, 이는 전역변수 `stdin`, `stdout`, `stderr`를 사용한다.<br>
데이터 영역 어딘가에 `sh`를 작성해두고, `stdin`/`stdout`/`stderr` 중 하나가 `sh` 문자열을 가리키도록 한 후, `setvbuf` 함수의 GOT를 `system` 함수의 주소로 덮어쓰고 다시 `main` 함수를 호출하면 셸을 획득할 수 있다.



## 새롭게 알게된 점
