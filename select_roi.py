import cv2
import json
import os

CONFIG_FILE = "cam_config.json"

drawing = False
ix, iy = -1, -1
roi = None


def mouse_callback(event, x, y, flags, param):
    global ix, iy, drawing, roi

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        roi = None

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        roi = (ix, iy, x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        roi = (ix, iy, x, y)


def main():
    global roi

    # Load config
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    
    rtsp_url = config["rtsp_url"]
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise RuntimeError("Failed to open camera stream")

    cv2.namedWindow("Select ROI")
    cv2.setMouseCallback("Select ROI", mouse_callback)

    print("🖱 Click and drag to draw ROI")
    print("💾 Press 's' to save ROI")
    print("❌ Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        display = frame.copy()

        if roi is not None:
            x1, y1, x2, y2 = roi
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imshow("Select ROI", display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s") and roi is not None:
            x1, y1, x2, y2 = roi
            x1, x2 = sorted((x1, x2))
            y1, y2 = sorted((y1, y2))

            roi_data = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            }

            # Update config with new ROI
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                
                config["roi"] = roi_data
                
                with open(CONFIG_FILE, "w") as f:
                    json.dump(config, f, indent=2)

                print(f"✅ ROI saved to {CONFIG_FILE}: {roi_data}")
            except (IOError, json.JSONDecodeError) as e:
                print(f"❌ Error saving ROI: {e}")

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()