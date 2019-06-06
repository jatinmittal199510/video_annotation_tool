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
import time

def ceildiv(a, b):
    return int(math.ceil(a / float(b)))

class App:
    def __init__(self, window, snippet_length, category_keyword_dict):
        self.window = window
        #self.window_width = self.window.winfo_screenwidth()
        #self.window_height = self.window.winfo_screenheight()
        self.window_width = 1368
        self.window_height = 768
        self.window.geometry(str(self.window_width) + "x" + str(self.window_height))
        self.window.title('Video Annotation')
        self.category_keyword_dictionary = category_keyword_dictionary

        self.flag_to_stop_video = False
        # self.video_size = (512, 512)
        self.snippet_length = snippet_length
        # self.video_capture = 0
        # self.no_of_categories = no_of_categories

        ##################################################################
        ## GUI design

        self.container_button_label_video_at_left = tk.Frame(self.window,bg="yellow")
        self.container_video_texts = tk.Frame(self.window)
        self.container_browse_play_previous = tk.Frame(self.window)
        self.container_next_goton_same_as_previous = tk.Frame(self.window)
        self.container_goton_textbox = tk.Frame(self.window)

        self.text_snippet_count = tk.StringVar()
        self.text_current_snippet = tk.StringVar()
        self.text_video_file_location = tk.StringVar()
        
        self.label_video = tk.Label(self.window)

        self.textbox_snippet_count = tk.Label(self.window, textvariable=self.text_snippet_count)
        self.textbox_file_location = tk.Label(self.window, textvariable=self.text_video_file_location)
        self.textbox_current_snippet = tk.Label(self.window, textvariable=self.text_current_snippet)
        self.textbox_goto = tk.Text(self.window, height=1.5, width=7)

        self.textbox_json = tk.Text(self.window)

        self.button_browse = tk.Button(self.window, text='BROWSE', width=15, command=self.browse)
        self.button_play = tk.Button(self.window, text='PLAY', state=DISABLED, width=15, command=self.play)
        self.button_previous = tk.Button(self.window, text='PREVIOUS', state=DISABLED, width=15, command=self.previous) 
        self.button_next = tk.Button(self.window, text='NEXT', state=DISABLED, width=15, command=self.next) #change to next 
        self.button_goto = tk.Button(self.window, text='GOTO N', state=DISABLED, width=7, command=self.goto) 
        self.button_same_as_previous = tk.Button(self.window, text='SAME AS PREVIOUS', state=DISABLED, width=15, command=self.same_as_previous) #need to implement
        
        self.label_video.pack(in_=self.container_video_texts, side=tk.TOP)

        self.textbox_snippet_count.pack(in_=self.container_video_texts, side=tk.TOP)
        self.textbox_current_snippet.pack(in_=self.container_video_texts, side=tk.TOP)
        self.textbox_file_location.pack(in_=self.container_video_texts, side=tk.TOP)

        self.button_browse.pack(in_=self.container_browse_play_previous, side=tk.LEFT) #button 1
        self.button_play.pack(in_=self.container_browse_play_previous, side=tk.LEFT) #button 2
        self.button_previous.pack(in_=self.container_browse_play_previous, side=tk.LEFT) #button 3
        
        self.button_next.pack(in_=self.container_next_goton_same_as_previous, side=tk.LEFT) #button 4

        self.textbox_goto.pack(in_=self.container_goton_textbox, side=tk.LEFT)
        self.button_goto.pack(in_=self.container_goton_textbox, side=tk.LEFT)
        self.container_goton_textbox.pack(in_=self.container_next_goton_same_as_previous, side=tk.LEFT) #button 5

        self.button_same_as_previous.pack(in_=self.container_next_goton_same_as_previous, side=tk.LEFT) #button 6
        
        
        self.container_video_texts.pack(in_=self.container_button_label_video_at_left, side=tk.TOP)
        self.container_browse_play_previous.pack(in_=self.container_button_label_video_at_left, side=tk.TOP)
        self.container_next_goton_same_as_previous.pack(in_=self.container_button_label_video_at_left, side=tk.TOP)
        #self.container_button_label_video_at_left.pack(in_=self.window, side=tk.LEFT, anchor=tk.NW)
        #self.container_button_label_video_at_left.pack(in_=self.window, side=tk.LEFT,expand = False)
        self.container_button_label_video_at_left.grid(row=0, column=0, sticky="nsew")

        self.create_checklist()
        self.textbox_json.grid(row=0, column=2, sticky="nsew")

        self.window.grid_columnconfigure(0, weight=1, uniform="group1")
        self.window.grid_columnconfigure(1, weight=1, uniform="group1")
        self.window.grid_columnconfigure(2, weight=1, uniform="group1")
        self.window.grid_rowconfigure(0, weight=1)
        ## GUI design
        ##################################################################
        self.window.mainloop()

    def create_checklist(self):
        self.container_categories = tk.Frame(self.window, bg="red")
        self.container_categories.grid(row=0, column=1, sticky="nsew")
        self.keyword_state_dict = {}
        self.new_keyword_dict = {}
        for self.category in self.category_keyword_dictionary:
            self.keyword_state_per_category = {}
            self.category_label = tk.StringVar()
            self.container_category_keyword = tk.Frame(self.window) 
            self.textbox_category_label = tk.Label(self.window, textvariable=self.category_label)
            self.category_label.set(self.category)
            self.textbox_category_label.pack(in_=self.container_category_keyword, side=tk.TOP)
            for self.keyword in self.category_keyword_dictionary[self.category]:
                self.keyword_variable = tk.IntVar()
                self.keyword_checkbox = tk.Checkbutton(self.window, text=self.keyword, variable=self.keyword_variable)
                self.keyword_checkbox.pack(in_=self.container_category_keyword, side=tk.TOP)
                self.keyword_state_per_category[self.keyword] = self.keyword_variable
                
            self.textbox_new_keyword = tk.Text(self.window, height=1, width=15)
            self.new_keyword_dict[self.category] = self.textbox_new_keyword
            self.textbox_new_keyword.pack(in_=self.container_category_keyword, side=tk.TOP)

            self.button_add_keyword = tk.Button(self.window, text='ADD KEYWORD', width=15, command=self.add_keyword)
            self.button_add_keyword.pack(in_=self.container_category_keyword, side=tk.TOP) 
            
            self.container_category_keyword.pack(in_=self.container_categories, side=tk.LEFT)
            self.keyword_state_dict[self.category] = self.keyword_state_per_category

        self.container_submit_add_category = tk.Frame(self.window)

        self.textbox_new_category = tk.Text(self.window, height=1, width=15)
        self.textbox_new_category.pack(in_=self.container_submit_add_category, side=tk.TOP)

        self.button_add_category = tk.Button(self.window, text='ADD CATEGORY', width=15, command=self.add_category)
        self.button_add_category.pack(in_=self.container_submit_add_category, side=tk.TOP) 
            
        self.text_sentence_label = tk.StringVar()
        self.textbox_sentence_label = tk.Label(self.window, textvariable=self.text_sentence_label)
        self.textbox_sentence_label.pack(in_=self.container_submit_add_category, side=tk.TOP) 
        self.text_sentence_label.set("Sentence for snippet:")

        self.textbox_sentence= tk.Text(self.window, height=2, width=30)
        self.textbox_sentence.pack(in_=self.container_submit_add_category, side=tk.TOP)

        self.button_submit = tk.Button(self.window, text='SUBMIT', state=DISABLED, width=15, command=self.submit)
        self.button_submit.pack(in_=self.container_submit_add_category, side=tk.TOP)
        self.container_submit_add_category.pack(in_=self.container_categories, side=tk.LEFT)


    def add_category(self):
        new_category = self.textbox_new_category.get("1.0", tk.END)
        new_category = new_category.strip()
        if(len(new_category) > 0):
            if(new_category not in self.category_keyword_dictionary):
                self.category_keyword_dictionary[new_category] = [] 
        with open(config_file_location, 'w') as fp:
            json.dump(self.category_keyword_dictionary, fp)
        self.container_categories.destroy()
        self.create_checklist()

    def add_keyword(self):
        for k in self.new_keyword_dict:
            new_keyword = self.new_keyword_dict[k].get("1.0", tk.END)
            new_keyword = new_keyword.strip()
            if(len(new_keyword) > 0):
                if(new_keyword not in self.category_keyword_dictionary[k]):
                    self.category_keyword_dictionary[k].append(new_keyword)
        with open(config_file_location, 'w') as fp:
            json.dump(self.category_keyword_dictionary, fp)
        self.container_categories.destroy()
        self.create_checklist()
        # for k in self.category_keyword_dictionary:
        #     print(k+': '+str(self.category_keyword_dictionary[k]))

    def submit(self):
        self.textbox_json.delete("1.0",tk.END)
        category_caption_dict = {}
        category_dict = {}
        for category in self.keyword_state_dict:
            keyword_dict = {}
            for keyword in self.keyword_state_dict[category]:
                keyword_dict[keyword] = self.keyword_state_dict[category][keyword].get()
            category_dict[category] = keyword_dict
        category_caption_dict['categories'] = category_dict
        category_caption_dict['caption'] = self.textbox_sentence.get("1.0",tk.END)
        
        self.output_dict[str(self.current_snippet)] = category_caption_dict
        with open(self.video_file_name_with_location + '.json', 'w') as fp:
            json.dump(self.output_dict, fp)
        self.textbox_json.insert(tk.END, str(self.output_dict))
        # for k in self.keyword_state_dict:
        #     print(k)
        #     for a in self.keyword_state_dict[k]:
        #         print(a.get())

    def same_as_previous(self):
        if(str(self.current_snippet - 1) in self.output_dict):
            self.textbox_json.delete("1.0",tk.END)
            self.output_dict[str(self.current_snippet)] = self.output_dict[str(self.current_snippet - 1)]
            with open(self.video_file_name_with_location + '.json', 'w') as fp:
                json.dump(self.output_dict, fp)
            self.textbox_json.insert(tk.END, str(self.output_dict))

    def resize(image):
        im = image
        new_siz = siz
        im.thumbnail(new_siz, Image.ANTIALIAS)
        return im

    def play_snippet(self):
        self.button_play.configure(state=DISABLED)
        self.snippet_location = '.tmp/' + str(self.current_snippet) + '.' + str(self.video_file_extension)
        self.snippet_capture = cv2.VideoCapture(self.snippet_location)
        while(self.snippet_capture.isOpened()):
            ret, frame = self.snippet_capture.read()
            if(ret == True and not self.flag_to_stop_video):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img =Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(img)
                self.label_video.config(image=imgtk)
                self.label_video.img = imgtk
                # cv2.waitKey(0)
                time.sleep(1/40)
            else:
                break
        self.snippet_capture.release()
        self.button_play.configure(state=NORMAL)
        if(self.current_snippet > 1):
            self.button_same_as_previous.configure(state=NORMAL)
        self.button_submit.configure(state=NORMAL)

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if(ret and not(self.flag_to_stop_video)):
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
        self.window.after(self.delay, self.update)

    def snippet_count(self):
        self.video_length = subprocess.check_output(("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", self.video_file_location)).strip()
        self.video_length = int(float(self.video_length))
        print("Video length in seconds: "+ str(self.video_length)) 
        self.snippet_count = ceildiv(self.video_length, self.snippet_length)

    def stop(self):
        self.flag_to_stop_video = True

    def play(self):
        self.flag_to_stop_video = False
        if(self.current_snippet <= self.snippet_count):
            self.text_current_snippet.set("Playing snippet number " + str(self.current_snippet))
            self.thread = threading.Thread(target=self.play_snippet)
            self.thread.start()
            # self.play_snippet()
        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")
        
    def next(self):
        self.textbox_sentence.delete("1.0",tk.END)
        self.stop()
        if(self.current_snippet < self.snippet_count):
            self.current_snippet += 1
            self.text_current_snippet.set("Selected snippet number " + str(self.current_snippet))
            self.button_previous.configure(state=NORMAL)
            if(self.current_snippet == self.snippet_count):
                self.button_next.configure(state=DISABLED)
        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")

    def previous(self):
        self.textbox_sentence.delete("1.0",tk.END)
        self.stop()
        if(self.current_snippet > 1):
            self.current_snippet -= 1
            self.text_current_snippet.set("Selected snippet number " + str(self.current_snippet))
            self.button_next.configure(state=NORMAL)
            if(self.current_snippet == 1):
                self.button_previous.configure(state=DISABLED)
        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")

    def goto(self):
        self.textbox_sentence.delete("1.0",tk.END)
        self.goto_snippet = self.textbox_goto.get("1.0",tk.END)
        self.goto_snippet = int(self.goto_snippet)
        self.stop()
        if(self.goto_snippet <= self.snippet_count):
            self.current_snippet = self.goto_snippet
            self.text_current_snippet.set("Selected snippet number " + str(self.current_snippet))
            if(self.current_snippet == self.snippet_count):
                self.button_next.configure(state=DISABLED)
            else:
                self.button_next.configure(state=NORMAL)
            if(self.current_snippet == 1):
                self.button_previous.configure(state=DISABLED)
            else:
                self.button_previous.configure(state=NORMAL)
        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")
        self.textbox_goto.delete("1.0",tk.END)

    def check():
        d = ""
        for i in range(len(OPTIONS)):
            for j in range(len(OPTIONS[i])):
                if all_bool_var[i][j].get():
                    d += OPTIONS[i][j] + " "
        text_current_snippet.set(d)

    def browse(self):
        self.video_file_location = askopenfilename()
        self.video_file_name_with_location = self.video_file_location.split('.')[0]
        self.video_file_name = self.video_file_name_with_location.split('/')[-1]
        self.output_dict = {}
        self.output_dict['video_name'] = self.video_file_name

        self.video_file_extension = self.video_file_location.split('.')[1]
        if(self.video_file_extension != 'mp4' and self.video_file_extension != 'avi'):
            self.text_current_snippet.set("Chosen file is not a video file")
            return    
        self.text_video_file_location.set(self.video_file_location)
        self.snippet_count()
        self.text_snippet_count.set("Total number of snippets are " + str(self.snippet_count))
        self.split_command = "python3 splitter/ffmpeg-split.py -f " + self.video_file_location + " -s " + str(self.snippet_length) + " >/dev/null 2>&1"
        os.system(self.split_command)
        self.current_snippet = 1
        self.text_current_snippet.set("Selected snippet number " + str(self.current_snippet))
        self.button_play.configure(state=NORMAL)
        self.button_next.configure(state=NORMAL)
        self.button_goto.configure(state=NORMAL)
        # self.button_previous.configure(state=NORMAL)

# category_keyword_dictionary = {'nouns': ['ram', 'rahim'], 'verbs': ['go', 'come']}
config_file_location = sys.argv[1]
with open(config_file_location) as json_file:  
    category_keyword_dictionary = json.load(json_file)

snippet_length = sys.argv[2]
# Create a window and pass it to the Application object
w = App(tk.Tk(), snippet_length, category_keyword_dictionary)