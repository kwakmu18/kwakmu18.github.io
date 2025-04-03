---
title:  "피사노 주기"
search: true
categories: [Algorithm & Data Structure]
last_modified_at: 2022-01-01
comments: true 
math: true
---

- 피보나치 수를 `K`로 나눈 나머지는 항상 주기를 갖는다.
- 주기의 길이를 `P`라고 하면, `N`번째 피보나치를 `M`으로 나눈 나머지는 `N%P`번째 피보나치 수를 `M`으로 나눈 것과 같다.
- 주기는 \\( M=10^k (k>2) \\)일 때 항상 \\( 15*10^{k-1} \\) 이다.

- \\( n(n\le1,000,000,000,000,000,000) \\)번째 피보나치 수를 \\( 1,000,000 \\)으로 나눈 나머지를 구하는 코드
    - K = 1,000,000 → 주기는 1,500,000

```c++
#include <bits/stdc++.h>
#define fastio ios_base::sync_with_stdio(0); cin.tie(0);

using namespace std;

long long fibo[1500000];

int main(void) {
    fastio;

    fibo[0] = 0; fibo[1] = 1;
    for(int i=2;i<1500000;i++) {
        fibo[i] = (fibo[i-1]+fibo[i-2])%1000000;
    }
    long long n;
    cin >> n;

    cout << fibo[n%1500000];

}
```