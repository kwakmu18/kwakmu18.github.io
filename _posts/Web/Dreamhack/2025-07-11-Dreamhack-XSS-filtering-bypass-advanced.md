---
title:  "[Dreamhack] XSS Filtering Bypass Advanced"
search: true
categories: ['Web', 'Dreamhack-Web']
last_modified_at: 2025-07-11
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/434">https://dreamhack.io/wargame/challenges/434</a>

## 문제 설명
Exercise: XSS Filtering Bypass의 패치된 문제입니다.

## 문제 분석
`/flag` 엔드포인트에서 POST 요청을 보내면, 셀레늄을 이용해 `/vuln` 엔드포인트에 사용자가 지정한 param 파라미터를 가지고 GET 요청을 전송한다.<br>
이때, param에는 이전 문제보다 더욱 강력한 필터링이 적용된다.
```py
def xss_filter(text):
    _filter = ["script", "on", "javascript"]
    for f in _filter:
        if f in text.lower():
            return "filtered!!!"

    advanced_filter = ["window", "self", "this", "document", "location", "(", ")", "&#"]
    for f in advanced_filter:
        if f in text.lower():
            return "filtered!!!"

    return text
```
param 파라미터에 "script", "on", "javascript" 문자열이 존재하는 경우 이를 "filtered!!!"으로 치환하여, `<scscriptript>`와 같이 입력해서는 필터링을 통과할 순 없게 되었다.<br>
또한 `advanced_filter`가 존재하여, "window", "self", "this", "document", "location", "()", "$#"를 모두 필터링하고 있다. <br>
하지만 키워드 기반으로 필터링을 수행하므로, 키워드 사이에 탭 문자 등을 끼워넣으면 그대로 우회가 가능하다.<br>
이 점과 iframe을 이용하여 `/memo` 엔드포인트 혹은 dreamhack tools로 쿠키와 함께 GET 요청을 하도록 하여 플래그를 획득한다.

## 새롭게 알게된 점
iframe으로 외부 URL을 열었을 때는 워게임 페이지에서의 쿠키가 전달되지 않지만, `/memo` 엔드포인트를 열었을 때는 쿠키가 그대로 남아 있다.<br>
정확한 원인은 알 수 없지만, 감히 예상해보자면 최근 브라우저에서는 쿠키의 SameSite 속성이 기본적으로 'Lax'로 설정되기 때문에, 외부 사이트에 접속하면 쿠키가 공유되지 않지만 `/memo` 엔드포인트는 같은 도메인이기 때문에 공유되는 것으로 보인다. <br>
SameSite 속성의 종류는 다음과 같다.
- 'None': 모든 Cross-Site 요청에 쿠키를 전송한다.
- 'Lax': 최상위 탐색에 대해서만 쿠키를 전송한다.
    - 쿠키가 전송되는 경우
        - 동일 도메인 내에서의 요청
        - 외부 사이트(another-site.com)에서 example.com으로 GET 요청을 통한 최상위 탐색 (예: `<a href="example.com">` 링크 클릭)
    - 쿠키가 전송되지 않는 경우
        - 외부 사이트(another-site.com)에서 example.com으로 보내는 POST 요청
        - 외부 사이트에서 example.com으로 보내는 백그라운드 요청 (iframe, img, AJAX 요청 등)
- 'Strict': 현재 사이트와 동일한 사이트 요청에서만 쿠키를 전송한다.