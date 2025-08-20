---
title:  "[Dreamhack] dlmalloc"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-08-20
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/597">https://dreamhack.io/wargame/challenges/597</a>

## 문제 설명
Now, everyone knows how to exploit ptmalloc.<br>
So I miss the old good days of <a target="_blank" href="https://gee.cs.oswego.edu/pub/misc/malloc.c">dlmalloc</a>.

## 문제 분석
힙 청크 할당, 힙 데이터 수정, 힙 데이터 비우기 총 3가지의 기능을 가진 바이너리가 주어진다.<br>
한 가지 특이한 점은, 현재 glibc에서 기본으로 사용되는 memory allocator인 ptmalloc2가 아닌 dlmalloc을 사용한다는 점이다.<br>
물론 dlmalloc이라고 해서 ptmalloc2와 다르진 않다.

첫 번째 청크를 할당하고, 두 번째 청크부터 큰 크기의 청크를 할당하면 라이브러리 영역과 가까운 곳에(고정 오프셋) 힙 청크가 할당된다.<br>
해당 바이너리에서는 힙 청크가 할당된 후 주소를 출력해주기 때문에, 이를 이용해서 libc base 주소를 계산할 수 있다.

취약점은 힙 데이터 비우기(0으로 채우기) 기능에 있다.
```c
void storeClear()
{
    char *Store; // [rsp+8h] [rbp-18h]
    unsigned __int64 Index; // [rsp+10h] [rbp-10h]
    __int64 n; // [rsp+18h] [rbp-8h]

    Store = (char *)readStore(); // 힙 청크 선택
    Index = readIndex(Store);    // 0으로 채우기 시작할 인덱스 선택(8바이트 단위)
    printf("Size? ");
    n = readUint64();
    memset(&Store[8 * Index], 0, n);
}
```
- 힙 청크를 선택하고, 0으로 채우기 시작할 인덱스를 선택한 후 0으로 덮을 크기를 입력한다.
- 이때, 크기에 대한 검사가 없기 때문에 이후 청크의 size를 0으로 덮어쓸 수 있다.

청크의 size가 0이 되면, 인덱스를 선택하는 `readIndex` 함수에서 문제가 발생한다.
```c
unsigned __int64 __fastcall readIndex(void *a1)
{
    unsigned __int64 Uint64; // [rsp+18h] [rbp-18h]
    size_t v3; // [rsp+20h] [rbp-10h]

    printf("Index? ");
    Uint64 = readUint64();
    v3 = malloc_usable_size(a1);
    if ( Uint64 >> 61 || v3 <= 8 * Uint64 )
    {
        fwrite("[ERROR] Out-of-bound index.\n", 1u, 0x1Cu, stderr);
        exit(1);
    }
    return Uint64;
}
```
- `malloc_usable_size` 함수를 호출하여, 힙 청크의 실제 크기를 가져온다. (청크 헤더를 참조하여서)
- 힙 청크의 실제 크기는 힙 청크 헤더까지 포함된 크기이기 때문에, 유저에게 반환될 때는 0x10만큼 뺀 값이 반환된다.
- 하지만 앞선 단계에서 청크의 크기를 0으로 덮어써버렸기 때문에, `v3` 값은 `0xFFFFFFFFFFFFFFF0`이 된다.
- 따라서, 어떤 값을 입력하더라도 if문을 통과할 수 있다.

인덱스를 자유롭게 입력할 수 있게 되었다면, 힙 청크보다 높은 주소에 위치하는 임의 주소에 8바이트 쓰기를 할 수 있다.<br>
<a target="_blank" href="http://127.0.0.1:4000/posts/AAWtoACE/#__printf_arginfo_table-__printf_function_table-%EC%A1%B0%EC%9E%91%EC%9D%84-%ED%86%B5%ED%95%9C-%EC%9E%84%EC%9D%98-%EC%BD%94%EB%93%9C-%EC%8B%A4%ED%96%89">이전에 공부했던</a> `__printf_function_table`과 `__printf_arginfo_table`을 조작하여 셸을 실행했다.

## 새롭게 알게된 점
