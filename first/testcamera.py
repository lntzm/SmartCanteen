import cv2
import time

cap = cv2.VideoCapture(0)
count = 0
start = time.perf_counter()

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("No camera")
        break
    
#     if count != 30:
#         print('.')
#         count += 1
#         continue
    
#     count = 0
#     print('test')
    cv2.imshow('client', frame)
    # print(time.perf_counter() - start)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
        