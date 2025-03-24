import numpy as np, cv2

def drawText(image, fontFace): # 각 키 정보와, 현재 모드에 대한 정보를 영상 좌상단에 띄우는 함수
    cv2.putText(image, "1 : Blurring, 2 : Shapening, 3 : Prewitt, 4 : Sobel, 5 : Laplacian", (50,50),fontFace, 1.3, (0,255,0),3)
    cv2.putText(image, f"mod : {modToFunc[mod][3]}", (50,100),fontFace, 1.3,(255,0,0),3)

def apply_filter(circle,mask,temp): # 특정 영역에 회선 마스크를 적용하는 함수
    # circle : 드래그한 원 영역 내에 포함되는 모든 점들, mask : 적용할 마스크, temp : 의미 없는 변수(apply_differential과 형식을 맞추기 위함)
    mask = np.array(mask,np.float32).reshape(3,3,3) # 인수로 받은 mask를 shape 3,3,3 & np.float32로 변환
    xcenter, ycenter = mask.shape[1] // 2, mask.shape[0] // 2  # xcenter, ycenter는 마스크의 중앙 인덱스
    for x,y in zip(circle[1],circle[0]): # circle에 들어 있는 모든 점 x,y에 대해서
            if y==0 or x==0 or y>=original_image.shape[0]-1 or x>=original_image.shape[1]-1 or used[y][x]:
                continue # 만약 x,y의 위치가 이미지의 끝 지점이거나, 이미 사용된 위치이면 처리하지 않음
            used[y][x]=True # 이미 처리한 지점으로 표시
            y1, y2 = y - ycenter, y + ycenter + 1 # y1, y2, x1, x2는 마스크를 적용할 이미지의 영역 좌표(3x3)
            x1, x2 = x - xcenter, x + xcenter + 1 
            roi = original_image[y1:y2, x1:x2].astype("float32") # 원본 이미지 original_image에서 3x3 영역 roi 가져오기
            s = cv2.convertScaleAbs(cv2.sumElems(cv2.multiply(roi, mask))).flatten() # roi 영역과 마스크를 1대1로 곱하고, 합계를 구한 후 8비트로 변환
            show_image[y,x],result1[y,x],result2[y,x] = s[:3],s[:3],[0,0,0] # s를 보여주는 이미지 show_image와, 두 결과 영상 result1, result2에 적용

def apply_differential(circle,mask_x,mask_y): # 특정 영역에 1차 미분 마스크를 적용하는 함수
    # circle : 드래그한 원 영역 내에 포함되는 모든 점들, mask_x,mask_y : x방향 마스크, y방향 마스크
    mask_x = np.array(mask_x,np.float32).reshape(3,3,3) # mask_x와 mask_y를 shape 3,3,3 & np.float32로 변환
    mask_y = np.array(mask_y,np.float32).reshape(3,3,3)
    xcenter, ycenter = mask_x.shape[1] // 2, mask_x.shape[0] // 2 # xcenter, ycenter는 마스크의 중앙 인덱스
    for x,y in zip(circle[1],circle[0]): # circle에 들어 있는 모든 점 x,y에 대해서
        if y==0 or x==0 or y>=original_image.shape[0]-1 or x>=original_image.shape[1]-1 or used[y][x]:
            continue # 만약 x,y의 위치가 이미지의 끝 지점이거나, 이미 사용된 위치이면 처리하지 않음
        used[y][x]=True # 이미 처리한 지점으로 표시
        y1, y2 = y - ycenter, y + ycenter + 1 # y1, y2, x1, x2는 마스크를 적용할 이미지의 영역 좌표(3x3)
        x1, x2 = x - xcenter, x + xcenter + 1
        roi = original_image[y1:y2, x1:x2].astype("float32") # 원본 이미지 original_image에서 3x3 영역 가져오기
        s1,s2 = np.array(cv2.sumElems(cv2.multiply(roi, mask_x)),np.float32), np.array(cv2.sumElems(cv2.multiply(roi, mask_y)),np.float32)
        # s1과 s2는 roi 영역에 각각 mask_x와 mask_y를 1대1로 곱하고, 합계를 구한 후 np.float32로 변환한 ndarray
        s = cv2.convertScaleAbs(cv2.magnitude(s1[:3], s2[:3])).flatten() # s는 s1과 s2의 크기를 계산하고, 8비트로 변환한 영상
        show_image[y,x],result1[y,x],result2[y,x] = s[:3],s[:3],[0,0,0] # s를 보여주는 이미지 show_image와, 두 결과 영상 result1, result2에 적용

def onMouse(event,x,y,flags,param=None): # 마우스 이벤트 처리 함수
    global circle_image,points,drag,nowXY # 전역 변수로써 사용
    if x<0 or y<0 or x>original_image.shape[1] or y>original_image.shape[0]: return # 만약 마우스가 영상을 벗어난 채로 드래그하면 중지
    if event==cv2.EVENT_MOUSEMOVE: # 마우스를 움직이는 이벤트인 경우
        if flags==cv2.EVENT_FLAG_LBUTTON: points.append((x,y)) # 드래그 하는 경우 points 리스트에 해당 점 좌표 추가
        nowXY=(x,y) # 현재 마우스 좌표 nowXY (마우스 포인터에 사용)
    elif event==cv2.EVENT_LBUTTONDOWN: # 마우스 왼쪽 버튼을 누른 경우
        drag=True # drag=True로 표시 (드래그 도중 모드 변경을 못하게 하기 위함)
        points = [] # points 리스트 초기화
    elif event==cv2.EVENT_LBUTTONUP:
        drag=False # drag=False로 표시
        pointLen = len(points) # 드래그하면서 가져온 점 좌표 갯수
        for i in range(pointLen-1): # points 리스트의 i번째, i+1번째 점 좌표에 대해서,
            cv2.line(circle_image, (points[i][0],points[i][1]),(points[i+1][0],points[i+1][1]),(0,0,255),60, cv2.LINE_AA)
            # circle_image에 두께 60, 빨간색의 선을 그리고, np.where을 이용해 빨간색의 선이 그려진 좌표를 모두 가져옴 -> circle
            circle = np.where(np.all(circle_image==(0,0,255),axis=-1))
            modToFunc[mod][0](circle,modToFunc[mod][1],modToFunc[mod][2]) # 각 모드에 따라 다른 함수, 마스크를 적용하여 알맞은 처리 함수 호출
        circle_image = original_image.copy() # circle_image는 원본 이미지로 초기화

mod = 1 # 현재 모드를 나타내는 값 (초기값은 1, Blurring)
modToFunc = { # 모드 번호와 [적용할 함수, 마스크, 해당 모드 문자열]을 매핑시키는 딕셔너리
    1 : [apply_filter,[1/9 for _ in range(27)], None, "Blurring"],
    2 : [apply_filter,[[0,0,0],[-1,-1,-1],[0,0,0],[-1,-1,-1],[5,5,5],[-1,-1,-1],[0,0,0],[-1,-1,-1],[0,0,0]], None, "Sharpening"],
    3 : [apply_differential,[[-1,-1,-1],[0,0,0],[1,1,1],[-2,-2,-2],[0,0,0],[2,2,2],[-1,-1,-1],[0,0,0],[1,1,1]],
         [[-1,-1,-1],[-1,-1,-1],[-1,-1,-1],[0,0,0],[0,0,0],[0,0,0],[1,1,1],[1,1,1],[1,1,1]], "Prewitt"],
    4 : [apply_differential,[[-1,-1,-1],[0,0,0],[1,1,1],[-2,-2,-2],[0,0,0],[2,2,2],[-1,-1,-1],[0,0,0],[1,1,1]],
         [[-1,-1,-1],[-2,-2,-2],[-1,-1,-1],[0,0,0],[0,0,0],[0,0,0],[1,1,1],[2,2,2],[1,1,1]], "Sobel"],
    5 : [apply_filter,[[1,1,1],[1,1,1],[1,1,1],[1,1,1],[-8,-8,-8],[1,1,1],[1,1,1],[1,1,1],[1,1,1]], None, "Laplacian"]
}
drag = False # 현재 드래그 중인지를 나타내는 변수
original_image = cv2.imread("input.jpg", cv2.IMREAD_UNCHANGED) # 어떠한 처리도 하지 않을, 원본의 영상
cursor_image = original_image.copy() # 마우스 포인터를 그릴 영상
circle_image = original_image.copy() # 두께 60, 빨간색의 선을 그릴 영상
show_image = original_image.copy() # 실시간으로 처리되어 사용자에게 보여줄 영상
result1 = original_image.copy() # 터치 효과가 적용된 결과로 저장할 영상
result2 = original_image.copy() # 터치 효과가 적용된 영역을 검정색으로 저장할 영상
used = np.array([[False for _ in range(original_image.shape[1])]for _ in range(original_image.shape[0])]) # 각 화소가 이미 처리되었음을 표시할 리스트
points,nowXY = None,None # 드래그하여 선택된 점들을 담는 points 리스트, 현재 마우스 좌표를 표시할 nowXY 

drawText(circle_image, cv2.FONT_ITALIC) # 영상에 텍스트 출력
cv2.imshow("image", result1) # 영상 전시
cv2.setMouseCallback("image", onMouse) # 마우스 이벤트 콜백 함수 등록

while True:
    key = cv2.waitKeyEx(5) # 키보드 입력
    if key==ord('q'): break # q를 입력했으면 중지
    if ord('1')<=key<=ord('5') and drag==False: mod=key-48 # 1~5 키를 입력했고 드래그 중이 아니라면, 모드 변경
    cursor_image[0:100,0:300]=result1[0:100,0:300] # 현재 사용중인 모드를 바꿔서 출력하기 위해 덮어쓰기
    cv2.circle(cursor_image, nowXY,30,(0,0,255),-1, cv2.LINE_AA) # 마우스 포인터 그리기
    cv2.addWeighted(show_image,0.5,cursor_image,0.5,0,cursor_image) # addWeighted를 이용하여 원을 반투명으로 표시
    drawText(cursor_image, cv2.FONT_ITALIC) # 영상에 텍스트 출력
    cv2.imshow("image", cursor_image) # 영상 전시

cv2.imwrite("20192108_1.jpg", result1) # result1(처리 결과)를 20192108_1.jpg로 저장
cv2.imwrite("20192108_2.jpg", result2) # result2(처리된 영역을 검정색으로 표시)를 20192108_2.jpg로 저장
cv2.destroyAllWindows() # 모든 윈도우 종료