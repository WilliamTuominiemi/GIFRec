import cv2
import numpy as np
import mss
import time

screen_region = {"top": 0, "left": 0, "width": 1920, "height": 1080}

output_file = "rec.avi"
fps = 20.0

with mss.mss() as sct:
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_file, fourcc, fps, (screen_region["width"], screen_region["height"]))

    print("Recording... Press 'Ctrl+C' to stop.")
    try:
        while True:
            img = np.array(sct.grab(screen_region))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            out.write(frame)
            cv2.imshow("Recording", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Recording stopped.")
    finally:
        out.release()
        cv2.destroyAllWindows()
