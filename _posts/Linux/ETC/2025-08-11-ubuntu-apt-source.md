---
title:  "Ubuntu apt source list"
search: true
categories: ['Linux']
last_modified_at: 2025-08-11
comments: true 
published: true
---

`/etc/apt/sources.list` 파일을 수정하여 서버를 국내 서버로 설정하면, 더 빠르게 apt update, apt upgrade가 가능하다.
```
# See sources.list(5) manpage for more information
# Remember that CD-ROMs, DVDs and such are managed through the apt-cdrom tool.

# 네이버 미러
deb http://mirror.navercorp.com/ubuntu bionic main restricted universe multiverse
deb http://mirror.navercorp.com/ubuntu bionic-updates main restricted universe multiverse
deb http://mirror.navercorp.com/ubuntu bionic-security main restricted universe multiverse
deb http://mirror.navercorp.com/ubuntu bionic-backports main restricted universe multiverse
```
우분투 버전에 따라 위 내용의 "bionic"을 모두 아래처럼 변경한다.
- 24.04: `noble`
- 22.04: `jammy`
- 20.04: `focal`
- 18.04: `bionic`
- 16.04: `xenial` (동작 미확인)