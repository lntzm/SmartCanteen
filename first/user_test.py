from first.user import User
import cv2
from multiprocessing import Queue, Pipe, Process


def userRecognize(q: Queue):
    while True:
        frame = q.get()

        user = User()
        found = user.getID(frame)
        if not found:
            print("> user not found")
            continue


def userDisplay(q):
    count = 0
    while cap.isOpened():
        ret, show = cap.read()
        if not ret:
            print('No camera')
            continue

        # 传递帧给main_process进程，这里取隔100帧发送一次
        if count == 20:
            q.put(show)
            count = 0
        else:
            count += 1
        # cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        # cv2.reszieWindow('image', 680, 400)
        cv2.imshow('face_detect', show)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    face_captures = Queue()

    user_disp_process = Process(target=userDisplay, args=(face_captures,))
    user_recg_process = Process(target=userRecognize, args=(face_captures,))

    user_disp_process.start()
    user_recg_process.start()

    user_disp_process.join()
    user_recg_process.terminate()

    cap.release()
    cv2.destroyAllWindows()
