import cv2
import os

def user_register(user_id, device_id=0):
    cap = cv2.VideoCapture(device_id)
    frame_count = 0
    count = 0
    flag = False
    root = os.path.split(os.path.realpath(__file__))[0]

    user_dir = os.path.join(root, "face_db", user_id)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    while(cap.isOpened()):
        _, frame = cap.read()


        if frame_count % 50 == 0 and flag:
            img_path = os.path.join(root, "face_db", user_id, str(count)) + ".jpg"
            cv2.imencode('.jpg', frame)[1].tofile(img_path)
            count += 1

        if flag:

            cv2.putText(frame, str(count) + " images loaded", (50, 100), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 0), 2)
            frame_count += 1
        else:
            cv2.putText(frame, "Press s to start", (50, 100), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 0), 2)

        cv2.imshow('frame', frame)
        key = cv2.waitKey(3)
        if  key & 0xFF == 27:
            break
        elif key & 0xFF == ord("s"):
            flag = True

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # user_id = input("Input user id :")
    user_register("杨东杰", device_id=0)

    