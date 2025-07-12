---
title:  "[프로세스와 잡] 프로세스 내부 구조"
search: true
categories: [Windows, Windows Internals]
last_modified_at: 2025-03-23
comments: true 
types: posts
toc: true
---

- 윈도우의 프로세스는 `EPROCESS(Executive Process)` 구조체로 표현된다.
  - 여러 가지 속성뿐만 아니라 연관된 여러 가지 다른 구조체들을 가리키는 포인터를 갖는다.
  - 예를 들어, `ETHREAD(Executive Thread)` 구조체로 표현되는 하나 또는 그 이상의 스레드를 가지고 있다.
- `EPROCESS`와 이와 관련된 모든 구조체들은 시스템 주소 공간(kernel space)에 위치한다.
  - 한 가지 예외는 `PEB(Process Environment Block)`으로, 프로세스 주소 공간(user space)에 위치한다.
- 윈도우 서브시스템 프로세스(csrss)는 각 프로세스에 대응되는 `CSR_PROCESS`라는 구조체를 관리한다.
- 커널 모드 쪽의 윈도우 서브시스템(win32k.sys) 또한 `W32PROCESS`라는 프로세스별 데이터 구조체를 관리한다.
  - 이 구조체는 스레드가 커널에 구현된 윈도우 USER나 GDI 함수를 최초로 호출하는 순간 생성된다.
  - 이는 user32.dll 라이브러리가 로드되자마자 이뤄지며, 이를 유발하는 전형적인 함수는 `CreateWindow(Ex)`와 `GetMessage`이다.
- 그래픽 디바이스 인터페이스 컴포넌트 인프라는 DirectX 그래픽 커널(Dxgkrnl.sys)로 하여금 자신의 `DXGPROCESS` 구조체를 초기화하게 한다.
  - 이 구조체는 DirectX 객체와 GPGPU 관련 카운터, 컴퓨터와 메모리 관리 관련 스케줄링에 대한 정책 설정에 대한 정보를 가진다.

## EPROCESS 구조체 형식
- 커널 디버깅을 이용하여 `EPROCESS` 구조체를 구성하는 필드의 리스트와 그 오프셋을 16진수로 표시할 수 있다. (`dt nt!_EPROCESS`)
  ```
  0: kd> dt nt!_EPROCESS
   +0x000 Pcb              : _KPROCESS
   +0x2d8 ProcessLock      : _EX_PUSH_LOCK
   +0x2e0 UniqueProcessId  : Ptr64 Void
   +0x2e8 ActiveProcessLinks : _LIST_ENTRY
   +0x2f8 RundownProtect   : _EX_RUNDOWN_REF
   +0x300 Flags2           : Uint4B
   +0x300 JobNotReallyActive : Pos 0, 1 Bit
   ...
   +0x7c8 VirtualTimerListLock : Uint8B
   +0x7d0 VirtualTimerListHead : _LIST_ENTRY
   +0x7e0 WakeChannel      : _WNF_STATE_NAME
   +0x7e0 WakeInfo         : _PS_PROCESS_WAKE_INFORMATION
   +0x810 Flags4           : Uint4B
   +0x810 PicoCreated      : Pos 0, 1 Bit
   +0x810 RestrictSetThreadContext : Pos 1, 1 Bit
  ```
  - Windows의 버전에 따라 오프셋이 서로 다를 수 있다. 위 출력 정보는 Windows 10 1703을 기준으로 한다.
  - `EPROCESS` 구조체의 첫 번째 필드는 프로세스 제어 블록(PCB)으로, 커널 프로세스를 위한 `KPROCESS` 타입의 구조체이다.
- 익스큐티브 루틴은 `EPROCESS`에 정보를 저장하지만 운영체제 커널의 일부인 디스패처나 스케줄러, 인터럽트, 시간 관리 코드는 `KPROCESS`를 사용한다.
  ```
  0: kd> dt nt!_KPROCESS
  +0x000 Header           : _DISPATCHER_HEADER
  +0x018 ProfileListHead  : _LIST_ENTRY
  +0x028 DirectoryTableBase : Uint8B
  +0x030 ThreadListHead   : _LIST_ENTRY
  +0x040 ProcessLock      : Uint4B
  +0x044 ProcessTimerDelay : Uint4B
  +0x048 DeepFreezeStartTime : Uint8B
  ...
  +0x268 FreezeCount      : Uint4B
  +0x26c KernelTime       : Uint4B
  +0x270 UserTime         : Uint4B
  +0x274 ReadyTime        : Uint4B
  +0x278 Spare2           : [80] UChar
  +0x2c8 InstrumentationCallback : Ptr64 Void
  +0x2d0 SecurePid        : Uint8B
  ```

## 실제 프로세스 관찰하기
### `EPROCESS`와 `KPROCESS` 구조체
- 커널 디버거에서 `!process` 명령으로 프로세스 객체 내의 정보 및 그와 연관된 구조체를 볼 수 있다.
  - 가상머신에서 메모장을 실행하고, PID를 확인한 후 `!process <PID>`를 입력하여 메모장의 프로세스 정보를 조회할 수 있다.
    ```
    0: kd> !process 0n4532
    Searching for Process with Cid == 11b4
    PROCESS ffffc387d2d22080
    SessionId: 1  Cid: 11b4    Peb: fa2261b000  ParentCid: 12e8
    DirBase: 116967000  ObjectTable: ffff9d82e8ddcc40  HandleCount: 218.
    Image: notepad.exe
    VadRoot ffffc387d386ddd0 Vads 96 Clone 0 Private 559. Modified 4. Locked 0.
    DeviceMap ffff9d82e7226db0
    Token                             ffff9d82e99ec060
    ElapsedTime                       00:00:06.869
    UserTime                          00:00:00.000
    KernelTime                        00:00:00.000
    QuotaPoolUsage[PagedPool]         243560
    QuotaPoolUsage[NonPagedPool]      13312
    Working Set Sizes (now,min,max)  (3406, 50, 345) (13624KB, 200KB, 1380KB)
    PeakWorkingSetSize                3312
    VirtualSize                       2097283 Mb
    PeakVirtualSize                   2097290 Mb
    PageFaultCount                    3482
    MemoryPriority                    BACKGROUND
    BasePriority                      8
    CommitCharge                      749

        THREAD ffffc387d2d24080  Cid 11b4.1194  Teb: 000000fa2261c000 Win32Thread: ffffc387d328c360 WAIT: (WrUserRequest) UserMode Non-Alertable
            ffffc387d3985200  QueueObject
        Not impersonating
        DeviceMap                 ffff9d82e7226db0
        Owning Process            ffffc387d2d22080       Image:         notepad.exe
        Attached Process          N/A            Image:         N/A
        Wait Start TickCount      7605           Ticks: 19 (0:00:00:00.296)
        Context Switch Count      1764           IdealProcessor: 1             
        UserTime                  00:00:00.000
        KernelTime                00:00:00.031
        Win32 Start Address 0x00007ff799339450
        Stack Init ffff8d810a65bc90 Current ffff8d810a65b3d0
        Base ffff8d810a65c000 Limit ffff8d810a656000 Call 0000000000000000
        Priority 10  BasePriority 8  IoPriority 2  PagePriority 5

        Child-SP          RetAddr               Call Site
        ffff8d81`0a65b410 fffff801`8349ff8a     nt!KiSwapContext+0x76
        ffff8d81`0a65b550 fffff801`8349f951     nt!KiSwapThread+0x16a
        ffff8d81`0a65b600 fffff801`8349f268     nt!KiCommitThreadWait+0x101
        ffff8d81`0a65b6a0 ffff84e7`30453558     nt!KeWaitForSingleObject+0x2b8
        ffff8d81`0a65b770 ffff84e7`304531d3     win32kfull!xxxRealSleepThread+0x2d8
        ffff8d81`0a65b8a0 ffff84e7`30456f89     win32kfull!xxxSleepThread2+0x97
        ffff8d81`0a65b8f0 ffff84e7`3045399c     win32kfull!xxxRealInternalGetMessage+0x919
        ffff8d81`0a65ba60 fffff801`83601f13     win32kfull!NtUserGetMessage+0x8c
        ffff8d81`0a65bb00 00007ffa`c8e71144     nt!KiSystemServiceCopyEnd+0x13 (TrapFrame @ ffff8d81`0a65bb00)
        000000fa`224af9d8 00000000`00000000     0x00007ffa`c8e71144
        ...
    ```
  - 출력 값의 첫 부분은 기본적인 프로세스의 정보를 보여주며, 다음으로는 프로세스 내의 스레드 목록이 표시된다.
  - 출력 값 중 PROCESS가 해당 프로세스의 `EPROCESS` 구조체 주소이다.
  - Peb도 확인할 수 있는데, `PEB`는 유저 모드에 존재하므로 유저 모드 주소 공간을 사용하고 있음을 확인할 수 있다.
  - PEB는 유저 모드에서 접근해야 하는 이미지 로더와 힙 관리자, 기타 윈도우 컴포넌트가 필요로 하는 정보를 포함하고 있다.

### `PEB` 구조체
- 커널 디버거에서 `!peb` 명령어로 프로세스의 PEB 구조체를 볼 수 있다.
  ```
  0: kd> .process /P ffffc387d2d22080; !peb fa2261b000
    Implicit process is now ffffc387`d2d22080
    .cache forcedecodeptes done
    PEB at 000000fa2261b000
    InheritedAddressSpace:    No
    ReadImageFileExecOptions: No
    BeingDebugged:            No
    ImageBaseAddress:         00007ff799320000
    NtGlobalFlag:             0
    NtGlobalFlag2:            0
    Ldr                       00007ffacba8b340
    Ldr.Initialized:          Yes
    Ldr.InInitializationOrderModuleList: 000002d51bbe2350 . 000002d51bbf17b0
    Ldr.InLoadOrderModuleList:           000002d51bbe24c0 . 000002d51bbf0490
    Ldr.InMemoryOrderModuleList:         000002d51bbe24d0 . 000002d51bbf04a0
                    <로드된 모듈 정보...>
    SubSystemData:     00007ffac5eb02d0
    ProcessHeap:       000002d51bbe0000
    ProcessParameters: 000002d51bbe1b20
    CurrentDirectory:  'C:\Users\mckkk\'
    WindowTitle:  'C:\Windows\system32\notepad.exe'
    ImageFile:    'C:\Windows\system32\notepad.exe'
    CommandLine:  '"C:\Windows\system32\notepad.exe" '
    DllPath:      '< Name not readable >'
    Environment:  000002d51bbe0fc0
        <환경 변수 정보...>
  ```

### `CSR_PROCESS` 구조체
- `CSR_PROCESS` 구조체는 윈도우 서브시스템(Csrss)에 대한 특정적인 프로세스 정보를 관리한다.
- Csrss 프로세스는 보호되고 있으므로 유저 모드 디버거로는 Csrss 프로세스에 연결할 수 없다.
  - 커널 디버거에서 `!process 0 0 csrss.exe`를 입력하여 Csrss 프로세스를 나열한다.
    ```
    0: kd> !process 0 0 csrss.exe
    PROCESS ffffc387d12ea7c0
        SessionId: 0  Cid: 0190    Peb: f8845b4000  ParentCid: 0184
        DirBase: 1065ad000  ObjectTable: ffff9d82e10f7cc0  HandleCount: 503.
        Image: csrss.exe

    PROCESS ffffc387d23657c0
        SessionId: 1  Cid: 01e4    Peb: 36c5b20000  ParentCid: 01d4
        DirBase: 1076cb000  ObjectTable: ffff9d82e1ac8440  HandleCount: 298.
        Image: csrss.exe
    ```
  - 이 중 하나를 선택하여, 해당 프로세스가 디버거 컨텍스트를 가리키게 변경하여 프로세스의 유저 모드 모듈이 보이게 한다.
    ```
    0: kd> .process /r /P ffffc387d12ea7c0
    Implicit process is now ffffc387`d12ea7c0
    .cache forcedecodeptes done
    Loading User Symbols
    ..................
    ```
    - `/P` 옵션은 디버거의 프로세스 컨텍스트를 제공한 프로세스 객체로 변경한다.(Implicit)
    - `/r` 옵션은 유저 모드 심볼 로드를 요청한다.
  - 이제 `lm` 명령어를 사용해 모듈과 `CSR_PROCESS` 구조체를 살펴볼 수 있다.
    ```
    0: kd> dt csrss!_CSR_PROCESS
   +0x000 ClientId         : _CLIENT_ID
   +0x010 ListLink         : _LIST_ENTRY
   +0x020 ThreadList       : _LIST_ENTRY
   +0x030 NtSession        : Ptr64 _CSR_NT_SESSION
   +0x038 ClientPort       : Ptr64 Void
   +0x040 ClientViewBase   : Ptr64 Char
   +0x048 ClientViewBounds : Ptr64 Char
   +0x050 ProcessHandle    : Ptr64 Void
   +0x058 SequenceNumber   : Uint4B
   +0x05c Flags            : Uint4B
   +0x060 DebugFlags       : Uint4B
   +0x064 ReferenceCount   : Int4B
   +0x068 ProcessGroupId   : Uint4B
   +0x06c ProcessGroupSequence : Uint4B
   +0x070 LastMessageSequence : Uint4B
   +0x074 NumOutstandingMessages : Uint4B
   +0x078 ShutdownLevel    : Uint4B
   +0x07c ShutdownFlags    : Uint4B
   +0x080 Luid             : _LUID
   +0x088 ServerDllPerProcessData : [1] Ptr64 Void
   ```

### `W32PROCESS` 구조체
- `W32PROCESS` 구조체는 커널 내에서 윈도우 그래픽이나 윈도우 관리 코드가 GUI 프로세스의 상태 정보를 관리하기 위해 필요한 모든 정보를 포함하고 있다.
- win32k 구조체의 타입 정보는 공개 심볼로는 이용할 수 없다. 