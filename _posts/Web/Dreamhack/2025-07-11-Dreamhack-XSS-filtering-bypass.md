---
title:  "[Dreamhack] XSS Filtering Bypass"
search: true
categories: ['Web', 'Dreamhack-Web']
last_modified_at: 2025-07-11
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/433">https://dreamhack.io/wargame/challenges/433</a>

## 문제 설명
Exercise: XSS Filtering Bypass에서 실습하는 문제입니다.

## 문제 분석
`/flag` 엔드포인트에서 POST 요청을 보내면, 셀레늄을 이용해 `/vuln` 엔드포인트에 사용자가 지정한 param 파라미터를 가지고 GET 요청을 전송한다.<br>
이때, param에는 다음과 같은 필터링이 적용된다.
```py
def xss_filter(text):
    _filter = ["script", "on", "javascript:"]
    for f in _filter:
        if f in text.lower():
            text = text.replace(f, "")
    return text
```
param 파라미터에 "script", "on", "javascript" 문자열이 존재하는 경우 이를 제거하고 있다. (치환 방식 필터링)<br>
하지만 일회성 치환이므로 `<scscriptript>`와 같이 입력하는 경우 "script"가 한 번만 ""으로 치환되어 결과적으로 `<script>`가 된다.<br>
이 점을 이용하여 `/memo` 엔드포인트 혹은 dreamhack tools에 document.cookie와 함께 요청하도록 자바스크립트를 작성한다.

## 새롭게 알게된 점