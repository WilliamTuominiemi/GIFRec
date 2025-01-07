import cv2
import numpy as np
import mss
import time
from pynput import mouse
import subprocess

start_pos = None
end_pos = None

def on_click(x, y, button, pressed):
    global start_pos, end_pos
    if pressed:
        print(f"Mouse pressed at ({x}, {y})")
        start_pos = (x, y)
    else:
        print(f"Mouse released at ({x}, {y})")
        end_pos = (x, y)
        return False

def select_screen_region():
    print("Drag the mouse to draw a rectangle for screen recording...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    if start_pos and end_pos:
        left = min(start_pos[0], end_pos[0])
        top = min(start_pos[1], end_pos[1])
        width = abs(start_pos[0] - end_pos[0])
        height = abs(start_pos[1] - end_pos[1])

        print(f"Selected region: Top-Left ({left}, {top}), Width: {width}, Height: {height}")
        return {"top": top, "left": left, "width": width, "height": height}
    else:
        print("No region selected.")
        return None

screen_region = select_screen_region()

output_video_file = "rec.avi"
output_gif_file = "rec.gif"
fps = 20.0

with mss.mss() as sct:
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_video_file, fourcc, fps, (screen_region["width"], screen_region["height"]))

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

print("Converting video to GIF using ffmpeg...")
subprocess.run([
    'ffmpeg', '-i', output_video_file, '-vf', 'fps=20,scale=320:-1:flags=lanczos', '-c:v', 'gif', output_gif_file])

print(f"GIF saved as {output_gif_file}")
