---
title:  "[Dreamhack] Dream Restaurant"
search: true
categories: ['Linux', 'Dreamhack-Pwn']
last_modified_at: 2025-08-19
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/547">https://dreamhack.io/wargame/challenges/547</a>

## 문제 설명
드림 레스토랑이 오픈했어요.<br>
취약점을 익스플로잇해 "flag" 파일을 읽으세요.<br>
플래그의 형식은 DH{...} 입니다.

## 문제 분석
메뉴 이름을 입력하면 스레드가 생성되며, 해당 스레드에서 전역 변수 `dish`를 조작하여 요리를 한다.
```c
struct dish_t {
    uint8_t food_type;
    void *food_ptr;
};
```

요리는 총 2가지 타입(rice, noodle)이 있으며, 각 요리 타입을 처리하는 함수는 다음과 같다.
```c
void CookRiceMenu(const struct food_menu_t *food_menu) {
    struct rice_t *rice_food;

    printf("\n\nCooking rice food '%s'...\n", food_menu->name);
    usleep(food_menu->cooking_time);
    dish.food_type = food_menu->food_type;
    usleep(31337);
    rice_food = (struct rice_t *)dish.food_ptr;
    memset(rice_food, 0x00, FOOD_SIZE);
    strcpy(rice_food->name, food_menu->name);
    rice_food->price = food_menu->price;
    rice_food->review_len = food_menu->review_len;
    rice_food->cooking_time = food_menu->cooking_time;

    puts("\nYour dish has arrived!");
}

void CookNoodleMenu(const struct food_menu_t *food_menu) {
    struct noodle_t *noodle_food;

    printf("\n\nCooking noodle food '%s'...\n", food_menu->name);
    usleep(food_menu->cooking_time);
    dish.food_type = food_menu->food_type;
    noodle_food = (struct noodle_t *)dish.food_ptr;
    memset(noodle_food, 0x00, FOOD_SIZE);
    strcpy(noodle_food->name, food_menu->name);
    noodle_food->price = food_menu->price;
    noodle_food->review_len = food_menu->review_len;
    noodle_food->cooking_time = food_menu->cooking_time;
    puts("\nYour dish has arrived!");
}
```
- rice 음식은 noodle 음식과 달리 `dish.food_type`을 변경하고 `usleep(31337)`을 호출하는 것을 확인할 수 있다.
- 따라서, 두 스레드를 적절한 타이밍에 생성하고 실행하면 Type Confusion이 발생할 수 있다.
    - 타입은 rice이지만 noodle 음식
    - 타입은 noodle이지만 rice 음식

타입이 중요한 이유는, rice와 noodle 음식의 구조체 형태에 있다.
```c
struct rice_t {
    char name[16];
    size_t review_len;
    unsigned int price;
    unsigned int cooking_time;
};

struct noodle_t {
    char name[12];
    size_t review_len;
    unsigned int price;
    unsigned int cooking_time;
};
```
- rice 음식은 `name`이 16바이트이지만, noodle 음식은 `name`이 12바이트이다.
- 따라서, 음식은 rice이지만 타입은 noodle일 경우 음식 이름의 일부가 `review_len`으로써 사용될 여지가 있다.

`review_len`은 프로그램을 종료할 때 사용된다.
```c
void LeaveReviewForRiceMenu() {
    char review[MAX_REVIEW_SIZE]; // 128
    struct rice_t *rice_menu;

    rice_menu = dish.food_ptr;
    printf("How about our rice food '%s'? ", rice_menu->name);
    fgets(review, rice_menu->review_len, stdin);
    puts("Thank you for writing review. It will help improve our restaurant.");
}

void LeaveReviewForNoodleMenu() {
    char review[MAX_REVIEW_SIZE]; // 128
    struct noodle_t *noodle_menu;

    noodle_menu = dish.food_ptr;
    printf("How about our noodle food '%s'? ", noodle_menu->name);
    fgets(review, noodle_menu->review_len, stdin);
    puts("Thank you for writing review. It will help improve our restaurant.");
}
```
- 현재 음식의 타입(`dish->food_type`)에 따라 두 함수 중 하나가 호출된다.
- 스택에 128바이트의 배열이 선언되어 있고, 그 배열에 최대 `review_len`바이트만큼 입력할 수 있다.
- 만약 Type Confusion이 발생하여 `review_len`이 큰 수로 지정되면, 스택 버퍼 오버플로우가 발생할 수 있다.

PIE와 Stack Canary가 적용되어 있지 않고, 바이너리는 static link이므로 libc base leak이 필요가 없다.<br>
그냥 ROP를 이용해서 셸을 얻고 플래그를 읽으면 된다.<br>
다만 `system` 함수나 `execve` 함수가 존재하지 않으므로, 직접 syscall을 호출하여야 한다.


## 새롭게 알게된 점
레이스 컨디션을 익스플로잇할 때 적용할 딜레이 시간(sleep)을 잘 모르겠다면, 이분 탐색을 활용하도록 하자...
```py
low, high = 0,4
while True:
    mid = (low+high)/2

    # Exploit...
    time.sleep(mid)
    # Exploit...

    # 결과가 맞으면 처리
    # 결과가 다르면 low=mid 혹은 high=mid를 적용하여 윈도우 조절
```