from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Manager


def plateRecognize(ns):
    while True:
        print(f"enable_plate_recg = {ns.enable_plate_recg}")
        if not ns.enable_plate_recg:
            continue

        ns.enable_plate_recg = False
        ns.enable_face_recg = True


def userRecognize(q: Queue, ns):
    while True:
        print(f"enable_face_recg = {ns.enable_face_recg}")
        if ns.enable_face_recg:
            continue

        ns.enable_plate_recg = True
        ns.enable_face_recg = False


if __name__ == '__main__':
    ns = Manager().Namespace()
    ns.enable_plate_recg = True
    ns.enable_face_recg = False

    plate_recg_process = Process(target=plateRecognize, args=(ns,))
    user_recg_process = Process(target=userRecognize, args=(ns))

    plate_recg_process.start()
    user_recg_process.start()

