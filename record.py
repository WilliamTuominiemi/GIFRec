import cv2
import numpy as np
import mss
import subprocess
import os
import tkinter as tk

class SelectionOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Selection Tool")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.root.overrideredirect(True)
        
        self.root.wait_visibility(self.root)
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        
        self.root.geometry(f'{screen_width}x{screen_height}+0+0')
        
        self.canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
            cursor="cross",
            bg='grey'
        )
        self.canvas.pack(fill='both', expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection = None
        
        self.canvas.bind('<Button-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        instruction = tk.Label(
            self.root,
            text="Click and drag to select area. Press Esc to cancel.",
            fg="white",
            bg="grey",
            font=("Arial", 12)
        )
        instruction.place(relx=0.5, rely=0.02, anchor="n")
    
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
    
    def on_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=10
        )
    
    def on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        self.selection = {
            "left": x1,
            "top": y1,
            "width": x2 - x1,
            "height": y2 - y1
        }
        self.root.quit()
    
    def get_selection(self):
        self.root.mainloop()
        selection = self.selection
        self.root.destroy()
        return selection

def select_screen_region():
    print("Draw a rectangle to select the recording area (Press Esc to cancel)...")
    overlay = SelectionOverlay()
    return overlay.get_selection()

screen_region = select_screen_region()
if not screen_region:
    print("Selection cancelled or no region selected.")
    exit()

temp_video_file = "temp_recording.avi"
output_gif_file = "rec.gif"
fps = 20.0

with mss.mss() as sct:
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(temp_video_file, fourcc, fps, 
                         (screen_region["width"], screen_region["height"]))
    
    print("Recording... Press 'Ctrl+C' to stop.")
    try:
        while True:
            img = np.array(sct.grab(screen_region))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            out.write(frame)
            
    except KeyboardInterrupt:
        print("Recording stopped.")
    finally:
        out.release()
        cv2.destroyAllWindows()

print("Converting video to GIF using ffmpeg...")
subprocess.run([
    'ffmpeg', '-y', '-i', temp_video_file,
    '-filter_complex',
    '[0:v] fps=24,setpts=0.5*PTS,scale=1000:-1,split [a][b];[a] palettegen [p];[b][p] paletteuse',
    output_gif_file
])

os.remove(temp_video_file)
print(f"GIF saved as {output_gif_file}")