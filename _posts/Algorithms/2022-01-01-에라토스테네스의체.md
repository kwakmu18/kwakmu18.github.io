---
title:  "에라토스테네스의 체"
search: true
categories: [Algorithm & Data Structure]
last_modified_at: 2022-01-01
comments: true 
---

- 에라토스테네스의 체는 고대 그리스의 수학자 에라토스테네스가 만들어 낸 **소수를 찾는 방법**으로, 체로 치듯이 수를 걸러낸다고 하여 '에라토스테네스의 체'라고 부른다.

### 방법
- 1부터 원하는 숫자 범위까지 숫자를 쓴다.
- 소수도 합성수도 아닌 1을 지운다.
- 다음에 만나는 2를 제외한 2의 모든 배수들을 지운다. 4,6,8,...
- 다음에 만나는 3을 제외한 3의 모든 배수들을 지운다. 3,6,9,...
- 다음에 만나는 4는 2에서 이미 지워졌다.
- 다음에 만나는 5를 제외한 5의 모든 배수들을 지운다. 5,10,15...
- 이를 원하는 숫자 범위 끝까지 반복하면 최종적으로는 소수만 남게 된다.

### 구현

```c++
#include <bits/stdc++.h>
#define NUM_MAX 100

using namespace std;

bool isPrime[NUM_MAX+1];

int main(void) {
    for(int i=1;i<NUM_MAX;i++) isPrime[i] = true; // 배열 초기화
    isPrime[1] = false; // 1은 소수도 합성수도 아니므로 제거

    for(int i=2;i<NUM_MAX;i++) {
        if (isPrime[i]) { // i가 지워지지 않은 경우에는 i의 배수들을 모두 제거
            for(int j=i*2;j<NUM_MAX;j+=i) isPrime[j] = false;
        }
    }

    for(int i=1;i<NUM_MAX;i++) {
        if (isPrime[i]) cout << i << " "; // 지워지지 않은 수들만 출력
    }
}
```

- 실행 결과
```
2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97
```