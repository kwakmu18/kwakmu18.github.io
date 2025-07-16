---
title:  "[2025 Hacksium Busan 예선] File Stream"
search: true
categories: ['CTF', '2025 Hacksium Busan']
last_modified_at: 2025-07-16
comments: true 
published: false
---

## 카테고리
**Pwnable**

## 문제 분석 및 풀이
GLibc의 `stdout`에 최대 `0xe0`바이트만큼을 입력한 후 `puts` 함수가 호출된다.<br>
stdout을 원하는 대로 덮어쓸 수 있으므로 FSOP를 이용한다.<br>
GLibc 2.35버전이므로, 함수 포인터 호출이 대부분 제거된 상태이다. 따라서 `_IO_FILE`의 `_wide_data`와 `_IO_wide_jumps`를 활용한다.<br>
<a target="_blank" href="/posts/FSOP/#fsop-glibc--227">참고 링크</a>