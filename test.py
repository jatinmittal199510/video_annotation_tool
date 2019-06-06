import tkinter
import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
from tkinter.filedialog import askopenfilename
import json
import sys
import subprocess
import math
import os
import threading
from tkinter import *
from PIL import Image, ImageTk

m=tk.Tk()
window_width = m.winfo_screenwidth()
window_height = m.winfo_screenheight()
m.geometry(str(window_width) + "x" + str(window_height))
m.title('Video Annotation')
fr1 = tk.Frame(m, bg="red")
fr2 = tk.Frame(m, bg="blue")
fr3 = tk.Frame(m, bg="yellow")

fr1.grid(row=0, column=0, sticky="nsew")
fr2.grid(row=0, column=1, sticky="nsew")
fr3.grid(row=0, column=2, sticky="nsew")

m.grid_columnconfigure(0, weight=1, uniform="group1")
m.grid_columnconfigure(1, weight=1, uniform="group1")
m.grid_columnconfigure(2, weight=1, uniform="group1")
m.grid_rowconfigure(0, weight=1)
m.mainloop()


