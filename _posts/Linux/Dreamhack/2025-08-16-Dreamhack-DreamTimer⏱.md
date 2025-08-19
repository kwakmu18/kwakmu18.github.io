---
title:  "[Dreamhack] DreamTimer⏱"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-08-16
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/213">https://dreamhack.io/wargame/challenges/213</a>

## 문제 설명
평소 Thread에 관심이 많았던 드림이는 Dreamhack 문제 업로드 기능 추가를 기념하여 "DreamTimer ⏱"를 만들었습니다.🎉<br>
안타깝게도 제작기간 도중에 코드가 없어졌는데, 블랙해커인 사심이가 프로그램의 코드를 갈취했다는 사실을 알게 되었습니다.<br>
마침 친구가 드림이에게 사심이가 수정된 프로그램을 테스트하고 있다고 알려주었고, 드림이는 테스트하고 있는 파일과 사용하고 있는 서버를 전달받게 됩니다. 드림이는 우리에게 사심이의 서버에서 자신의 코드를 다시 가져와달라고 도움을 요청하였습니다.<br>
드림이를 대신해 괘씸한 사심이의 서버를 쟁취하세요!💯

## 문제 분석
타이머를 생성하면 타이머 구조체와 함께 스레드를 생성한다. 이때 타이머 구조체는 아래와 같은 형태를 가진다.
```c
struct timer {
    __int64 timerNumber;
    __int64 timerMinute;
    __int64 timerSecond;
    __int64 timerRandomBase;
    char timerComment[8];
    char *timerName;
}
```
- `timerMinute`과 `timerSecond`는 Init 단계에서 초기화된다.
- `timerName`은 `malloc`을 통해 동적 할당받으며, 최대 0x300 크기만큼 이름을 입력할 수 있다.

우선 타이머를 하나 할당했다가 삭제한 후, 동일한 크기로 할당을 하면, tcache의 next 포인터가 그대로 남아 있으므로 이를 이용하여 Heap Base를 leak한다.

타이머를 삭제할 때는 다음과 같은 특이사항이 있다.
```c
void ReadOneMoreByte(void *ptr, int size) {
    read(0, ptr, size+1);
    return strcspn((const char *)ptr, "\n");
}

void DeleteTimer(index) {
    ...
    printf("[?] Any short comments? : ");
    ReadOneMoreByte(timers[index]->timerComment, 8);
    ...
}
```
- 타이머 구조체의 comment에 입력을 받는데, 이때 최대 8+1=9바이트만큼 입력할 수 있다.
- 이를 이용하여 timerComment 배열과 접해 있는 `timerName`의 하위 1바이트를 조작할 수 있다.
- `timerName` 하위 1바이트를 조작한다면, 기존의 `timerName` 힙 청크가 아닌 다른 청크를 해제할 수 있다.

스레드를 생성하다보면 힙 영역에 0x120바이트 크기의 스레드 관련 데이터가 생성된다.<br>
위 취약점을 이용해 이 청크를 해제한 후, 이를 타이머 이름으로써 할당하면 libc base를 leak할 수 있다.

위 취약점을 한 번 더 이용해서 이번에는 `tcache_entry`(Heap 주소 영역의 최하위 주소에 자동으로 할당되는 tcache 관리 구조체, 0x280바이트)를 해제했다가 타이머 이름으로써 할당하면 `tcache_entry` 자체를 조작하여 원하는 주소에 힙 청크를 할당하도록 할 수 있다.

이를 이용하여 `__free_hook` 위치에 힙 청크를 할당받은 후, `__free_hook`을 `system` 함수 주소로 덮어쓰고 "/bin/sh"가 저장된 영역을 해제하도록 하면 셸을 얻을 수 있다.

셸을 얻고 나면, `sh`, `bash`, `echo`, `date`를 제외하고 "/bin" 디렉터리의 모든 바이너리가 삭제된 상태이다.<br>
`ls`나 `cat`을 사용할 수 없으므로, 다른 방법으로 플래그 파일을 읽어야 한다.<br>
`date` 명령어에는 `-f` 옵션이 있는데, 이는 파일을 읽어서 날짜 데이터를 파싱하는 기능이다. 이를 이용하면 플래그는 당연히 날짜 형식이 아닐테니 오류 메시지가 출력되는데, 이를 이용해서 플래그를 읽을 수 있다.

## 새롭게 알게된 점
