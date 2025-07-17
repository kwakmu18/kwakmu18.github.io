---
title:  "[2025 Hacksium Busan 예선] XLSX Reader"
search: true
categories: ['CTF', '2025 Hacksium Busan']
last_modified_at: 2025-07-16
comments: true 
published: true
---

## 카테고리
**Web**

## 문제 분석 및 풀이
웹 상에 xlsx(엑셀) 파일을 업로드할 수 있고, 그 파일을 파싱하여 첫 번째 셀의 내용을 출력해준다.<br>
Dockerfile을 보면, Spreadsheet::ParseXLSX 0.27 버전을 사용하고 있음을 알 수 있다.<br>
CVE-2024-23525 취약점은 Spreadsheet::ParseXLSX 0.30 버전 이하에서 발생하며, 특수하게 조작된 엑셀 파일을 해당 라이브러리를 통해 파싱하는 경우 XXE 취약점이 발생하여 임의 파일을 읽을 수 있다.<br>
엑셀 파일을 압축 해제한 후, `xl/worksheets/sheet1.xml` 파일을 열어보면 시트와 셀에 대한 정보가 포함되어 있다.<br>
해당 xml에 다음과 같은 내용을 포함시키고,
```xml
<!DOCTYPE x [ <!ENTITY xxe PUBLIC "bar" "/app/flag"> ]>
```
첫 번째 셀의 내용을 다음과 같이 설정한 후 다시 압축한다.
```xml
<row r="1"><c r="A1" t="inlineStr"><is><t>&xxe;</t></is></c></row>
```
압축한 파일을 서버에 업로드하면, 파싱 과정에서 XXE 취약점에 의해 "/app/flag" 파일을 읽고 첫 번째 셀의 내용으로 대체하여 플래그가 출력된다.