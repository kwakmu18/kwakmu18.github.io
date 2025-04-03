---
title:  "상호 배타적 집합 & 유니온 파인드"
search: true
categories: [Algorithm & Data Structure]
last_modified_at: 2022-01-01
comments: true 
---

- 상호 배타적인 집합을 효율적으로 표현하기 위한 자료구조?이다.
- 서로 다른 두 개의 집합을 병합하는 `union_find` + 원소가 어떤 집합에 속해 있는지 판단하는 `find`로 구성된다.
- `parent` 배열에는 각 원소의 최상위 부모를 표현한다.

### Basic

- `find` 함수
    ```c
    int find(int parent[], int k) {
        if (parent[k]==k) return k;
        else return find(parent, parent[k]);
    }
    ```
    - `parent[k] == k`이면 `k`가 그 집합의 부모이므로 `k`를 반환한다.
    - 그렇지 않은 경우는 `k`의 부모를 찾을 때까지 재귀적으로 탐색한다.

- `union_find` 함수
    ```c
    void union_find(int parent[], int a, int b) {
        a=find(parent, a); b=find(parent,b); // a,b 각자의 최상위 부모를 find
        parent[b]=a; //b의 parent를 a로 설정 (항상 a<b로 가정)
    }
    ```
    - 원소 `a`, `b` 각자의 최상위 부모를 `find` 함수를 이용해서 찾는다.
    - 원소 `b`의 parent를 `a`로 설정함으로써 두 집합을 union한다. (항상 `a<b`로 가정)

### 최적화(경로 압축)

- `find` 함수
    ```c
    int find(int parent[], int k) {
        if (parent[k]==k) return k;
        else return parent[k] = find(parent, parent[k]);
    }
    ```
    - `k`의 부모를 찾을 때까지 재귀적으로 탐색하되, 거쳐 오는 모든 경로 상의 원소의 부모를 최상위 부모로 대체함으로써 경로를 압축한다.