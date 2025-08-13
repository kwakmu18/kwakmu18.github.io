---
title:  "[Dreamhack] CSP Bypass"
search: true
categories: ['Web', 'Dreamhack-Web']
last_modified_at: 2025-08-13
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/435">https://dreamhack.io/wargame/challenges/435</a>

## 문제 설명
Exercise: CSP Bypass에서 실습하는 문제입니다.

## 문제 분석
문제의 기본적인 구조는 이전에 풀었던 XSS Filtering Bypass와 동일하다. 하지만, 이러한 동작이 추가되었다.
```py
@app.after_request
def add_header(response):
    global nonce
    response.headers[
        "Content-Security-Policy"
    ] = f"default-src 'self'; img-src https://dreamhack.io; style-src 'self' 'unsafe-inline'; script-src 'self' 'nonce-{nonce}'"
    nonce = os.urandom(16).hex()
    return response
```
- CSP 정책이 적용되고 있다. 적용되는 정책은 아래와 같다.
    - `-src`가 붙는 기본적인 정책들은 self(Same Origin)으로 출처가 제한된다.
    - 스타일시트의 경우 출처는 Same Origin으로 제한되지만, 'unsafe inline'이 적용되어 인라인 스크립트 삽입이 가능하다.
    - 스크립트의 경우 출처가 Same Origin으로 제한되며, 매 요청마다 새롭게 생성되는 nonce 값을 요구한다.

자바스크립트의 경우 nonce 값을 요구하지만, nonce는 인라인 스크립트에 대해서만 적용되므로 `<script src="~~"></script>`는 여전히 사용할 수 있다.<br>
하지만 출처가 Same Origin으로 제한되므로, 같은 오리진 내에서 자바스크립트를 반환해주는 곳을 찾아야 한다.<br>
가장 적절한 곳은 `/vuln` 엔드포인트이다.
```py
@app.route("/vuln")
def vuln():
    param = request.args.get("param", "")
    return param
```
- `/vuln` 엔드포인트는 "param" 파라미터로 받은 값을 html에 렌더링하는 것이 아니라 그대로 반환한다.
- `/flag` 엔드포인트에서 관리자에게 `/vuln` 엔드포인트에 요청하도록 한 후, "param" 파라미터에는 `/memo` 엔드포인트로 이동하도록 자바스크립트를 작성하면 된다. (`location.href`, `document.cookie` 활용)

## 새롭게 알게된 점