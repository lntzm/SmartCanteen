import cv2

"""
拍照模块
*运行相机 并拍一张照片（按esc进行拍照）*

cam_id = 0  默认为相机0（笔记本相机）
"""
def take_photo(cam_id=0):    
    cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)  

    while (cap.isOpened()):
        ret, frame = cap.read()

        cv2.imshow('frame', frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    
    return frame