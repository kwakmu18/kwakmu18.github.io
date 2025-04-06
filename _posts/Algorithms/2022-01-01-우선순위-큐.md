---
title:  "우선순위 큐"
search: true
categories: [Algorithm & Data Structure]
last_modified_at: 2022-01-01
comments: true 
---

- 일반적인 큐는 연산의 결과로 먼저 들어간 데이터가 먼저 나오는 선입선출 구조이지만, 우선순위 큐는 들어간 순서에 상관없이 **우선순위가 높은** 데이터가 먼저 나온다.
- 두 가지 연산을 가진다.
    - `enqueue`: 우선순위 큐에 데이터를 삽입하는 행위
    - `dequeue`: 우선순위 큐에서 데이터를 꺼내는 행위
- 배열로 구현하면 비효율적이므로, 힙으로 구현한다.
    - 힙은 **완전 이진 트리**이며, 모든 노드에 저장된 값은 자식 노드에 저장된 값보다 크거나 같아야 한다. (최대 힙)
    - 새로운 데이터는 우선순위가 가장 낮다는 가정하에 마지막 위치에 저장하며, 부모 노드와의 우선순위를 비교하여 위치가 바뀌어야 한다면 제자리를 찾을 때까지 교환한다.
    - 데이터를 삭제할 때는 마지막 노드를 루트 노드의 자리로 옮긴 다음, 자식 노드와의 비교를 통해 제자리를 찾아가게 한다.
    - 루트의 인덱스를 `i`라고 하면, 왼쪽 자식의 인덱스는 `2*i`, 오른쪽 자식의 인덱스는 `2*i+1`이다.
- `enqueue` 함수
    ```c
    void enqueue(int pq[], int k) {
        if (size==1) {
            pq[size]=k; size++; return;
        }
        pq[size]=k;
        int findindex=size;
        while (findindex>1) {
            if (pq[findindex]<pq[findindex/2]) {
                swap(pq[findindex],pq[findindex/2]);
                findindex/=2;
            }
            else break;
        }
        size++;
    }
    ```
- `dequeue` 함수
    ```c
    int dequeue(int pq[]) {
        if (size==1) {
            cout << "우선순위 큐에 데이터가 없음\n";
            return -1;
        }
        else if (size==2) {
            size--; return pq[1];
        }
        int ret=pq[1];
        pq[1]=pq[size-1];
        int findindex=1;
        while (findindex<(size-1)/2) {
            if (pq[findindex]>pq[findindex*2]) {
                swap(pq[findindex], pq[findindex*2]);
                findindex*=2;
            }
            else if (pq[findindex]>pq[findindex*2+1]) {
                swap(pq[findindex], pq[findindex*2+1]);
                findindex=findindex*2+1;
            }
            else break;
        }
        size--;
        return ret;
    }
    ```

- c++에서는 `std::priority_queue<>` 자료구조를 이용할 수 있다.
    ```c++
    #include <bits/stdc++.h>
    using namespace std;
    int main(void) {
        priority_queue<int> pq;

        pq.push(4); // 데이터 삽입
        pq.push(3);
        pq.push(5);

        pq.pop();   // 데이터 제거
    }
    ```