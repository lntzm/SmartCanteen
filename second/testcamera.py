import cv2
# from PIL import Image, ImageEnhance
# import numpy as np


if __name__ == '__main__':
    cap = cv2.VideoCapture(1)
    while True:
        ret, frame = cap.read()
        if not ret:
            print('No camera')
            continue
        # frame_pil = Image.fromarray(np.uint8(frame))
        # frame_light = ImageEnhance.Brightness(frame_pil)
        # frame_show = frame_light.enhance(0.5)
        # frame_show.show()
        cv2.imshow("client", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
