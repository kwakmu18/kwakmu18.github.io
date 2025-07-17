---
title:  "[2025 Hacksium Busan 예선] File Share Server"
search: true
categories: ['CTF', '2025 Hacksium Busan']
last_modified_at: 2025-07-16
comments: true 
published: true
---

## 카테고리
**Pwnable**

## 문제 분석 및 풀이
Command에 "upload"를 입력하면 파일을 업로드할 수 있고, "download"를 입력하면 파일을 다운로드할 수 있다.<br>
파일을 다운로드하기 위해 파일의 이름을 입력할 때, 검증이 없기 때문에 Path Traversal이 발생할 수 있다.<br>
파일 이름을 입력할 때 flag 파일의 경로를 입력하면 플래그를 얻을 수 있다.