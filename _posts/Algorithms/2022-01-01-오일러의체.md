---
title:  "오일러의 체"
search: true
categories: [Algorithm & Data Structure]
last_modified_at: 2022-01-01
comments: true
---

- 오일러의 체는 에라토스테네스의 체를 개선한 것으로, `N` 이하의 소수를 `O(N)`만에 찾고, `N` 이하의 자연수 소인수분해를 `O(logN)`에 할 수 있다. 

### 개념
- 소수가 아닌 수를 합성수라고 한다. 에라토스테네스의 체 구현에서 합성수는 두 번 이상 검사되므로 시간이 더 소모된다.
- 합성수는 `x = i * prime` 으로 나타낼 수 있다. 이때 `i`는 `i>=prime`을 만족하는 다른 인수이며, `prime`은 `x`의 최소 소인수이다.
- `prime`보다 작은 소수는 `i`를 나누어 떨어지게 할 수 있다.

### 방법
- 소수의 여부 대신, 해당 수의 최소 소인수(SPF; Smallest Prime Factor)를 나타내는 배열을 둔다.
- 현재까지 판별한 모든 소수에 대해 반복문을 돌면서 `spf[index * 소수] = 소수` 계산을 진행한다.
    - `spf[index * 소수]`는 소수가 아니면서 그 소인수는 소수라는 정보를 가지게 된다.
- 이때 `index`가 현재 순회중인 소수와 나누어 떨어지게 되면 반복문을 종료한다.

### 구현

```c++
#define MAX 10000

vector<int> spf(MAX+1, 0);
vector<int> primes;

for(int i=2;i<=MAX;i++) {                                          // i는 2부터 MAX까지 순회를 시작한다.
        if (spf[i]==0) {                                           // spf[i]==0이면 아직 방문하지 않은 것이므로, 소수로 판정한다.
            spf[i]=i;                                              // 따라서 최소 소인수는 자기 자신이 된다.
            primes.push_back(i);                                   // 소수 배열에 추가한다.
        }
        for(int j=0;j<primes.size() && i*primes[j]<=MAX; j++) {    // j는 primes 배열의 인덱스를 나타낸다.
            spf[i*primes[j]]=primes[j];                            // i*primes[j]의 최소 소인수는 primes[j]가 된다.
            if (i%primes[j]==0) break;                             // i가 소수로 나누어 떨어지면 반복문을 빠져나가는데, 
                                                                   // x = i * p 에서 i의 최소소인수가 p가 되었고 그 다음 소수를 q라 하면
                                                                   // i * q = a * p * q (p < q) 이기 때문에 q부터는 i * q 의 최소소인수가 절대 될 수 없기 때문이다.
        }
    }
```

- 위를 이용하여 구한 최소 소인수를 바탕으로 빠른 소인수분해
```c++
int input;
cin >> input;
while (input>1) {
	cout << spf[input] << " ";
	input/=spf[input];
}
```