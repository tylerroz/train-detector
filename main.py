import cv2

# this is okay, only exposed locally
RTSP_URL = "rtsp://traincam:unionpacific111@192.168.1.233:554/stream1"

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    raise RuntimeError("Could not connect to camera")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame grab failed")
        break

    cv2.imshow("Network Cam", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
