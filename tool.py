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
import os.path as path
import threading
from tkinter import *
from PIL import Image, ImageTk
import time

row_id = 0

def ceildiv(a, b):
    return int(math.ceil(a / float(b)))

class App:
    def __init__(self, window, snippet_length, category_keyword_dict):
        self.window = window
        self.window.resizable(False, False)
        #self.window_width = self.window.winfo_screenwidth()
        #self.window_height = self.window.winfo_screenheight()
        self.window_width = 1368
        self.window_height = 768
        self.window.geometry(str(self.window_width) + "x" + str(self.window_height))
        self.window.title('Video Annotation')
        self.category_keyword_dictionary = category_keyword_dictionary

        self.flag_to_stop_video = False
        self.flag_to_pause_video = 0
        # self.video_size = (512, 512)
        self.snippet_length = snippet_length
        # self.video_capture = 0
        # self.no_of_categories = no_of_categories

        ##################################################################
        ## GUI design

        self.container_video = tk.Frame(self.window)
        self.container_video.grid_columnconfigure(0, weight=1, uniform="group1")
        self.container_video.grid_columnconfigure(1, weight=1, uniform="group1")
        self.container_video.grid_columnconfigure(2, weight=1, uniform="group1")
        
        self.text_snippet_count = tk.StringVar()
        self.text_current_snippet = tk.StringVar()
        self.text_video_file_location = tk.StringVar()
        
        self.label_video = tk.Label(self.window)

        self.textbox_snippet_count = tk.Label(self.window, textvariable=self.text_snippet_count)
        self.textbox_file_location = tk.Label(self.window, textvariable=self.text_video_file_location)
        self.textbox_current_snippet = tk.Label(self.window, textvariable=self.text_current_snippet)
        self.textbox_goto = tk.Text(self.window, height=2)

        self.textbox_json = tk.Text(self.window)

        self.button_browse = tk.Button(self.window, text='BROWSE', command=self.browse)
        self.button_play = tk.Button(self.window, text='START', command=self.play)
        self.button_previous = tk.Button(self.window, text='PREVIOUS', command=self.previous) 
        self.button_next = tk.Button(self.window, text='NEXT', command=self.next) #change to next 
        self.button_pause = tk.Button(self.window, text='PLAY/PAUSE', command=self.pause) #change to next 
        self.button_goto = tk.Button(self.window, text='GOTO N', command=self.goto) 
        self.button_same_as_previous = tk.Button(self.window, text='SAME AS PREVIOUS', command=self.same_as_previous)
        self.button_browse_json = tk.Button(self.window, text='BROWSE JSON', command=self.browse_json) 
        
        self.label_video.grid(in_= self.container_video, row=0 , column=0, columnspan=3, sticky="nsew")


        self.textbox_snippet_count.grid(in_= self.container_video, row=1 , column=0, columnspan=3,sticky="nsew")
        self.textbox_current_snippet.grid(in_= self.container_video, row=2 , column=0, columnspan=3,sticky="nsew")
        self.textbox_file_location.grid(in_= self.container_video, row=3 , column=0, columnspan=3,sticky="nsew")

        self.button_browse.grid(in_= self.container_video, row=4 , column=0,sticky="nsew") #button 1
        self.button_play.grid(in_= self.container_video, row=4 , column=1,sticky="nsew") #button 2
        self.button_previous.grid(in_= self.container_video, row=4 , column=2,sticky="nsew") #button 3
        
        self.button_next.grid(in_= self.container_video, row=5 , column=0,sticky="nsew") #button 4
        self.button_pause.grid(in_= self.container_video, row=5 , column=1,sticky="nsew") #button 5
        self.button_same_as_previous.grid(in_= self.container_video, row=5 , column=2, sticky="nsew") #button 6

        self.textbox_goto.grid(in_= self.container_video, row=6 , column=0, sticky="nsew") #button 5
        self.button_goto.grid(in_= self.container_video, row=6 , column=1, columnspan=2, sticky="nsew") #button 5
        self.button_browse_json.grid(in_= self.container_video, row=7 , column=0, columnspan=3, sticky="nsew", pady=20)  
        
        self.container_video.grid(row=0, column=0, sticky="nsew")

        self.create_checklist()
        self.textbox_json.grid(row=0, column=2, sticky="nsew")

        self.window.grid_columnconfigure(0, weight=4, uniform="group1")
        self.window.grid_columnconfigure(1, weight=3, uniform="group1")
        self.window.grid_columnconfigure(2, weight=2, uniform="group1")
        self.window.grid_rowconfigure(0, weight=1)
        ## GUI design
        ##################################################################
        self.window.mainloop()

    def create_checklist(self):
        global row_id
        self.container_categories = tk.Frame(self.window)
        self.container_categories.grid(row=0, column=1, sticky="nsew")
        self.container_categories.grid_columnconfigure(0, weight=1, uniform="group1")
        self.container_categories.grid_columnconfigure(1, weight=1, uniform="group1")
        self.container_categories.grid_columnconfigure(2, weight=1, uniform="group1")
        self.container_categories.grid_columnconfigure(3, weight=1, uniform="group1")

        self.keyword_state_dict = {}
        self.new_keyword_dict = {}
        for self.category in self.category_keyword_dictionary:
            self.keyword_state_per_category = {}
            self.textbox_category_label = tk.Label(self.window, text=self.category)
            self.textbox_category_label.grid(in_= self.container_categories, row=row_id, column=0, sticky="nsew")

            var = tk.StringVar()
            var.set("Check")
            menu = OptionMenu(self.window, variable = var, value="options:")
            menu.grid(in_= self.container_categories, row=row_id, column=1, sticky="nsew")

            for self.keyword in self.category_keyword_dictionary[self.category]:
                self.keyword_variable = tk.BooleanVar()
                menu['menu'].add_checkbutton(label=self.keyword, onvalue=True, 
                          offvalue=False, variable=self.keyword_variable)
                self.keyword_state_per_category[self.keyword] = self.keyword_variable
                
            self.textbox_new_keyword = tk.Text(self.window, height=2)
            self.new_keyword_dict[self.category] = self.textbox_new_keyword
            self.textbox_new_keyword.grid(in_= self.container_categories, row=row_id, column=2, sticky="nsew")
            
            self.button_add_keyword = tk.Button(self.window, text='ADD KEY', command=self.add_keyword)
            self.button_add_keyword.grid(in_=self.container_categories, row=row_id, column=3, sticky="nsew") 
            
            
            self.keyword_state_dict[self.category] = self.keyword_state_per_category
            row_id += 1

        self.textbox_new_category = tk.Text(self.window, height=2)
        self.textbox_new_category.grid(in_= self.container_categories, row=row_id, column=0, columnspan=2 , sticky="nsew")
        
        self.button_add_category = tk.Button(self.window, text='ADD CATEGORY', command=self.add_category)
        self.button_add_category.grid(in_= self.container_categories, row=row_id, column=2, columnspan=2, sticky="nsew")
            
        self.text_sentence_label = tk.StringVar()
        self.textbox_sentence_label = tk.Label(self.window, textvariable=self.text_sentence_label)
        self.textbox_sentence_label.grid(in_= self.container_categories, row=row_id+1, column=0, columnspan=4, sticky="nsew")
        self.text_sentence_label.set("Sentence for snippet:")

        self.textbox_sentence= tk.Text(self.window, height=2)
        self.textbox_sentence.grid(in_= self.container_categories, row=row_id+2, column=0, columnspan=4 , sticky="nsew")

        self.button_submit = tk.Button(self.window, text='SUBMIT', command=self.submit)
        self.button_submit.grid(in_= self.container_categories, row=row_id+3, column=0, columnspan=4, sticky="nsew")

        self.display_selected_keys = tk.StringVar()
        self.textbox_display = tk.Message(self.window, textvariable=self.display_selected_keys, anchor="c")
        self.textbox_display.grid(in_= self.container_categories, row=row_id+4, column=0, columnspan=4, sticky="nsew", pady=20)
        #self.display_selected_keys.set("")


    def add_category(self):
        global row_id
        new_category = self.textbox_new_category.get("1.0", tk.END)
        new_category = new_category.strip()
        if(len(new_category) > 0):
            if(new_category not in self.category_keyword_dictionary):
                self.category_keyword_dictionary[new_category] = [] 
        with open(config_file_location, 'w') as fp:
            json.dump(self.category_keyword_dictionary, fp)
        self.container_categories.destroy()
        row_id = 0
        self.create_checklist()

    def add_keyword(self):
        global row_id
        for k in self.new_keyword_dict:
            new_keyword = self.new_keyword_dict[k].get("1.0", tk.END)
            new_keyword = new_keyword.strip()
            if(len(new_keyword) > 0):
                if(new_keyword not in self.category_keyword_dictionary[k]):
                    self.category_keyword_dictionary[k].append(new_keyword)
        with open(config_file_location, 'w') as fp:
            json.dump(self.category_keyword_dictionary, fp)
        self.container_categories.destroy()
        row_id = 0
        self.create_checklist()
        
    def browse_json(self):
        json_load = askopenfilename()
        self.output_dict = {}
        with open(json_load) as json_file:  
            self.output_dict = json.load(json_file)
        self.textbox_json.insert(tk.END, str(self.output_dict))

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
        category_caption_dict['caption'] = self.textbox_sentence.get("1.0",tk.END).rstrip('\n')
        
        self.output_dict[str(self.current_snippet)] = category_caption_dict
        with open(self.video_file_name_with_location + '.json', 'w') as fp:
            json.dump(self.output_dict, fp)
        self.textbox_json.insert(tk.END, str(self.output_dict))
        if str(self.current_snippet) in self.output_dict.keys():
            self.display_message()
        else:
            self.display_selected_keys.set("")

    def same_as_previous(self):
        if(str(self.current_snippet - 1) in self.output_dict):
            self.textbox_json.delete("1.0",tk.END)
            self.output_dict[str(self.current_snippet)] = self.output_dict[str(self.current_snippet - 1)]
            message = ""
            for cat, listt in self.output_dict[str(self.current_snippet - 1)]['categories'].items():
                message += cat.upper() + ': '
                for keys_in_list, checker in self.output_dict[str(self.current_snippet -1)]['categories'][cat].items():
                    if checker:
                        message += keys_in_list + ', '
            self.display_selected_keys.set(message)
            with open(self.video_file_name_with_location + '.json', 'w') as fp:
                json.dump(self.output_dict, fp)
            self.textbox_json.insert(tk.END, str(self.output_dict))
        else:
            self.display_selected_keys.set("")

    def resize(image):
        im = image
        new_siz = siz
        im.thumbnail(new_siz, Image.ANTIALIAS)
        return im

    def pause(self):
        if(self.flag_to_pause_video):
            self.flag_to_pause_video = False
        else:
            self.flag_to_pause_video = True

    def play_snippet(self):
        # self.button_play.configure(state=DISABLED)
        # self.button_submit.configure(state=NORMAL)
        self.snippet_location = '.tmp/' + str(self.current_snippet) + '.' + str(self.video_file_extension)
        self.snippet_capture = cv2.VideoCapture(self.snippet_location)
        while(self.snippet_capture.isOpened()):
            if(self.flag_to_pause_video):
                continue
            ret, frame = self.snippet_capture.read()
            if(ret == True and not self.flag_to_stop_video):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                height, width, layers =  frame.shape

                container_video_width = (1368 * 4) / 9
                
                if(width > container_video_width):
                    new_width = int(container_video_width)
                    new_height = int((new_width * height) / width)
                    frame = cv2.resize(frame, (new_width, new_height))

                img =Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(img)
                self.label_video.config(image=imgtk)
                self.label_video.img = imgtk
                # cv2.waitKey(0)
                time.sleep(1/40)
            else:
                break
        self.snippet_capture.release()
        # self.button_play.configure(state=NORMAL)
        # if(self.current_snippet > 1):
        #     self.button_same_as_previous.configure(state=NORMAL)

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
            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")
            self.thread.start()
            
        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")
        
    def next(self):
        self.textbox_sentence.delete("1.0",tk.END)
        self.stop()
        if(self.current_snippet < self.snippet_count):
            self.current_snippet += 1
            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")
            self.text_current_snippet.set("Selected snippet number " + str(self.current_snippet))
            # self.button_previous.configure(state=NORMAL)
            # if(self.current_snippet == self.snippet_count):
            #     self.button_next.configure(state=DISABLED)
        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")

    def display_message(self):
        message = ""
        for cat, listt in self.output_dict[str(self.current_snippet)]['categories'].items():
            message += cat.upper() + ': '
            for keys_in_list, checker in self.output_dict[str(self.current_snippet)]['categories'][cat].items():
                if checker:
                    message += keys_in_list.rstrip('\n') + ', '
            message += '\n'
        self.display_selected_keys.set(message)

    def previous(self):
        self.textbox_sentence.delete("1.0",tk.END)
        self.stop()
        if(self.current_snippet > 1):
            self.current_snippet -= 1
            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")                
            self.text_current_snippet.set("Selected snippet number " + str(self.current_snippet))
            # self.button_next.configure(state=NORMAL)
            # if(self.current_snippet == 1):
            #     self.button_previous.configure(state=DISABLED)
        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")

    def goto(self):
        self.textbox_sentence.delete("1.0",tk.END)
        self.goto_snippet = self.textbox_goto.get("1.0",tk.END)
        self.goto_snippet = int(self.goto_snippet)
        self.stop()
        if(self.goto_snippet <= self.snippet_count):
            self.current_snippet = self.goto_snippet
            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")
            self.text_current_snippet.set("Selected snippet number " + str(self.current_snippet))
            # if(self.current_snippet == self.snippet_count):
            #     self.button_next.configure(state=DISABLED)
            # else:
            #     self.button_next.configure(state=NORMAL)
            # if(self.current_snippet == 1):
            #     self.button_previous.configure(state=DISABLED)
            # else:
            #     self.button_previous.configure(state=NORMAL)
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
        self.json_file_name_with_location = self.video_file_name_with_location + '.json'
        self.output_dict = {}
        self.current_snippet = 1
        self.dict_keys = ["video_name", "video_category", "snippet_size", "duration", "num_snippets"]
        if path.exists(self.json_file_name_with_location):
            with open(self.json_file_name_with_location) as json_file:  
                self.output_dict = json.load(json_file)
            self.textbox_json.insert(tk.END, str(self.output_dict))
            for each_key in self.output_dict.keys():
                if each_key not in self.dict_keys and int(each_key) > self.current_snippet:
                    self.current_snippet = int(each_key)
        self.video_file_name = self.video_file_name_with_location.split('/')[-1]
        
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
        
        self.text_current_snippet.set("Selected snippet number " + str(self.current_snippet))
        self.window.title(self.video_file_name)
        
        # self.button_play.configure(state=NORMAL)
        # self.button_next.configure(state=NORMAL)
        # self.button_goto.configure(state=NORMAL)
        # self.button_browse_json.configure(state=NORMAL)

# category_keyword_dictionary = {'nouns': ['ram', 'rahim'], 'verbs': ['go', 'come']}
config_file_location = sys.argv[1]
with open(config_file_location) as json_file:  
    category_keyword_dictionary = json.load(json_file)

snippet_length = sys.argv[2]
# Create a window and pass it to the Application object
w = App(tk.Tk(), snippet_length, category_keyword_dictionary)