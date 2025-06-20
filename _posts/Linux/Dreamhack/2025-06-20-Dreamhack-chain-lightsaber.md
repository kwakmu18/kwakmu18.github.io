---
title:  "[Dreamhack] chain-lightsaber"
search: true
categories: ['Linux', 'Dreamhack Wargame']
last_modified_at: 2025-06-20
comments: true 
published: true
---

## 문제 링크
<a target="_blank" href="https://dreamhack.io/wargame/challenges/1943">https://dreamhack.io/wargame/challenges/1943</a>

## 문제 설명
Magic: the Assemblage Prototype!<br>
Do you guys take notes during class? Cuz I don't.

This is a challenge modified from chain-lightning.

```
$ xxd mta > mta.hex; xxd mta2 > mta2.hex; diff mta.hex mta2.hex
409c409
< 00001980: 7df8 488b 45f8 c700 1400 0000 488b 45f8  }.H.E.......H.E.
---
> 00001980: 7df8 488b 45f8 c700 1000 0000 488b 45f8  }.H.E.......H.E.
456c456
< 00001c70: 0048 89c7 b800 0000 00e8 b2f4 ffff baff  .H..............
---
> 00001c70: 0048 89c7 b800 0000 00e8 b2f4 ffff ba01  .H..............
```

Flag format: `DH{…}`

## 문제 분석
- <a target="_blank" href="https://dreamhack.io/wargame/challenges/1935">chain-lightning</a> 문제에서 note 작성 기능이 제거되었고, 상대방의 체력이 16으로 조정되었다.
    - 정확히는 `note` 배열에 최대 `0xff`바이트만큼 입력할 수 있었으나 `0x1`바이트만 입력할 수 있도록 수정되었다. 따라서 fake 구조체를 만들 수 없다.
    - lightning bolt를 6번 사용하여야 셸을 얻을 수 있다.
- 취약점 자체는 동일하므로, `next` 포인터를 조작할 수 있다.
    - 이전 문제와 동일한 방법으로 PIE base를 얻은 후, `next` 포인터를 조작하여 카드 목록 배열을 읽어 힙 주소를 얻는다.
    - 이후 2번째 카드를 사용하여 3의 대미지를 준다.
    - 3번째 카드를 사용할 때는 `next` 포인터를 2번째 카드의 주소로 조작한 후 사용하면 3 -> 2 순서로 사용되어 6의 대미지를 줄 수 있다.
    - 4번째 카드를 사용할 때는 `next` 포인터를 3번째 카드의 주소로 조작한 후 사용하면 4 -> 3 -> 2 순서로 사용되어 9의 대미지를 줄 수 있다.
    - 따라서 2 -> 3 -> 2 -> 4 -> 3 -> 2 총 6번의 lightning bolt로 18의 대미지를 주어 셸을 얻을 수 있다.

## 새롭게 알게된 점