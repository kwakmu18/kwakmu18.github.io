---
title:  "[Dreamhack] CSP Bypass Advanced"
search: true
categories: ['Web', 'Dreamhack-Web']
last_modified_at: 2025-08-13
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/436">https://dreamhack.io/wargame/challenges/436</a>

## 문제 설명
Exercise: CSP Bypass에서 실습하는 문제입니다.

## 문제 분석
문제는 거의 <a target="_blank" href="/posts/Dreamhack-CSP-Bypass/">이 문제</a>와 같지만, `/vuln` 엔드포인트가 변경되었다.
```py
@app.route("/vuln")
def vuln():
    param = request.args.get("param", "")
    return render_template("vuln.html", param=param, nonce=nonce)
```
- "vuln.html"을 렌더링하도록 변경되어서, 이전 문제와 동일한 방법을 사용할 수 없다. (자바스크립트 자체가 아닌 html을 반환하므로.)

적용된 CSP들을 살펴보면, base-uri에 대한 정책이 빠져 있음을 알 수 있다. base-uri는 적용하지 않는 경우 기본값이 없기 때문에, 이 사실을 이용한다.<br>
base-uri는 `<base href="<URL>">`과 같이 base 태그를 이용하여 변경할 수 있다. base-uri를 변경하는 경우 이후의 상대적 요청은 모두 `<URL>/~~`로 요청되게 된다.<br>
`/vuln` 엔드포인트에 접속해보면, 다음과 같이 두 개의 자바스크립트를 로드하는 것을 확인할 수 있다. 아직은 base-uri를 수정하지 않은 상태이다.<br>
<img src="/assets/img/web/1.png" class="post-image"><br>

이제 "param" 파라미터에 `<base href="https://www.example.com">`을 입력하여, base-uri를 "https://www.example.com"으로 수정하고 다시 요청을 보내보면 다음과 같다.<br>
<img src="/assets/img/web/2.png" class="post-image"><br>
이전과 다르게 "https://www.example.com"에서 "/static/js/jquery.min.js"를 가져오는 것을 확인할 수 있다.

이 점을 알았다면, 직접 열거나 깃허브의 도움을 받아 서버를 연 후, base-uri를 서버 주소로 하고 "/static/js/jquery.min.js" 위치에 memo로 이동하는 자바스크립트를 작성하고 관리자에게 요청하도록 하면 플래그를 얻을 수 있다.



## 새롭게 알게된 점