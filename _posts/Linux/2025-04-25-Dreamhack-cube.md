---
title:  "[Dreamhack] cube"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-04-25
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/216">https://dreamhack.io/wargame/challenges/216</a>

## 문제 설명
루트 권한으로 실행되는 서비스를 찾았습니다.
그러나, 큐브안에 갇혀서 빠져나올 수가 없습니다. 큐브를 탈출하고 플래그를 획득하세요!

## 문제 분석
- 함수 초기에 `chroot("/home/cube/cube_box")`가 호출되어 루트 디렉터리가 "/home/cube/cube_box"로 고정된다.
- `chroot` 함수가 cwd(current working direcotry) 자체를 이동하진 않으므로, 현재 cwd는 "/home/cube/cube_box"가 아니다.
- `main` 함수에서는 셸코드를 입력받아 실행할 수 있으므로, 현재 cwd를 "/"로 옮기고, 루트 디렉터리를 "."로 하게 되면 문제 없이 셸을 실행할 수 있다.

## 새롭게 알게된 점
- `chroot` 함수가 cwd(current working direcotry) 자체를 이동하진 않는다.