import tkinter
import tkinter as tk
from tkinter import ttk
import cv2
import PIL.Image, PIL.ImageTk
import time
from tkinter.filedialog import askopenfilename
import json
from functools import partial
from tkinter import messagebox
import sys
import subprocess
import math
import os
import os.path as path
import threading
from tkinter import *
from PIL import Image, ImageTk
import time
import copy

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
        self.snippet_length = snippet_length

        self.keyword_state_dict = {}

        self.current_event_id = 0
        self.current_event_name = "_"
        self.current_snippet = 1
        self.output_dict = {}
        

        ##################################################################
        ## GUI design
        #self.style = ttk.Style()
        #print(self.style.theme_names())
        #self.style.theme_use('classic')
        self.container_video = tk.Frame(self.window)
        self.container_video.grid_columnconfigure(0, weight=1, uniform="group1")
        self.container_video.grid_columnconfigure(1, weight=1, uniform="group1")
        self.container_video.grid_columnconfigure(2, weight=1, uniform="group1")
        self.container_video.grid_columnconfigure(3, weight=1, uniform="group1")
        
        self.text_snippet_count = tk.StringVar()
        self.text_current_snippet = tk.StringVar()
        self.text_video_file_location = tk.StringVar()
        
        self.label_video = tk.Label(self.window)

        self.textbox_snippet_count = tk.Label(self.window, textvariable=self.text_snippet_count)
        self.textbox_file_location = tk.Label(self.window, textvariable=self.text_video_file_location)
        self.textbox_current_snippet = tk.Label(self.window, textvariable=self.text_current_snippet)
        self.textbox_goto = tk.Text(self.window, height=2)
        self.text_play_button = tk.StringVar()

        self.button_browse = tk.Button(self.window, text='LOAD VIDEO', command=self.browse)

        self.button_play = tk.Button(self.window, textvariable=self.text_play_button, state=DISABLED, command=self.play)
        self.text_play_button.set("PLAY")
        self.button_previous = tk.Button(self.window, text='PLAY PREVIOUS', state=DISABLED, command=self.previous) 
        self.button_next = tk.Button(self.window, text='PLAY NEXT', state=DISABLED, command=self.next)
        self.text_pause_button = tk.StringVar()
        self.text_pause_button.set("PAUSE")
        self.button_pause = tk.Button(self.window, textvariable=self.text_pause_button, state=DISABLED, command=self.pause)
        self.button_goto = tk.Button(self.window, text='GOTO N', state=DISABLED, command=self.goto)
        
        self.label_video.grid(in_= self.container_video, row=0 , column=0, columnspan=4, sticky="nsew")


        self.textbox_snippet_count.grid(in_= self.container_video, row=1 , column=0, columnspan=4,sticky="nsew")
        self.textbox_current_snippet.grid(in_= self.container_video, row=2 , column=0, columnspan=4,sticky="nsew")
        self.textbox_file_location.grid(in_= self.container_video, row=3 , column=0, columnspan=4,sticky="nsew")

        self.button_browse.grid(in_= self.container_video, row=4 , column=0, columnspan=4, sticky="nsew")
        self.button_play.grid(in_= self.container_video, row=5 , column=0,columnspan=2,sticky="nsew")
        self.button_pause.grid(in_= self.container_video, row=5 , column=2, columnspan=2,sticky="nsew")

        self.button_previous.grid(in_= self.container_video, row=6 , column=0, columnspan=2,sticky="nsew")
        self.button_next.grid(in_= self.container_video, row=6 , column=2, columnspan=2,sticky="nsew")
        
        self.textbox_goto.grid(in_= self.container_video, row=7 , column=0, sticky="nsew")
        self.textbox_goto.configure(state="disabled")
        self.button_goto.grid(in_= self.container_video, row=7 , column=1, columnspan=3, sticky="nsew")
        
        
        
        self.container_video.grid(row=0, column=0, sticky="nsew")

        ############################################

        self.container_middle = tk.Frame(self.window)
        self.container_middle.grid(row=0, column=1, sticky="nsew")
        self.container_middle.grid_columnconfigure(0, weight=1, uniform="group1")
        self.container_middle.grid_columnconfigure(1, weight=1, uniform="group1")
        self.container_middle.grid_columnconfigure(2, weight=1, uniform="group1")
        self.container_middle.grid_columnconfigure(3, weight=1, uniform="group1")

        self.create_checklist()

        self.text_sentence_label = tk.StringVar()
        self.textbox_sentence_label = tk.Label(self.window, textvariable=self.text_sentence_label)
        self.textbox_sentence_label.grid(in_= self.container_middle, row=1, column=0,sticky="nsew")
        self.text_sentence_label.set("Caption:")

        self.textbox_sentence= tk.Text(self.window, height=2)

        self.textbox_sentence.grid(in_= self.container_middle, row=1, column=1, columnspan=3 , sticky="nsew")
        self.button_same_as_previous = tk.Button(self.window, text='LOAD KEYWORDS AND CAPTION FROM PREVIOUS SNIPPET', state=DISABLED, command=self.same_as_previous)
        self.button_same_as_previous.grid(in_= self.container_middle, row=2, column=0, columnspan=4, sticky="nsew")        

        self.is_snippet_transition_var = tk.BooleanVar()
        self.is_snippet_transition = tk.Checkbutton(self.window, text="This snippet is a transition snippet", 
                                                        variable=self.is_snippet_transition_var, anchor="w",onvalue=True, offvalue=False,command=self.transitionbutton_click)
        self.is_snippet_transition.grid(in_= self.container_middle, row=3, column=0, columnspan=4, sticky="nsew")

        self.is_event_checkbutton_var = tk.BooleanVar()
        self.is_event_checkbutton = tk.Checkbutton(self.window, text="This snippet is a part of an event",onvalue=True, offvalue=False,
                                                        command=self.checked_checkbutton, anchor="w", variable=self.is_event_checkbutton_var)
        self.is_event_checkbutton.grid(in_= self.container_middle, row=4, column=0, columnspan=4, sticky="nsew")

        self.radio_button_var = IntVar()
        self.button_generate_new_id = Radiobutton(self.window, text='GENERATE NEW EVENT ID', variable=self.radio_button_var, value=1,
                                                        anchor="w",state=DISABLED,command=self.radiobutton_click)
        self.button_generate_new_id.grid(in_= self.container_middle, row=5, column=0, columnspan=4, sticky="nsew") 

        self.button_previous_id_var = tk.StringVar()
        self.button_previous_id_var.set("USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
        self.button_previous_id = Radiobutton(self.window, textvariable=self.button_previous_id_var, variable=self.radio_button_var, value=2,
                                                    anchor="w",state=DISABLED,command=self.radiobutton_click)
        self.button_previous_id.grid(in_= self.container_middle, row=6, column=0, columnspan=4, sticky="nsew")
        
        self.caption_label = tk.Label(self.window, text="Event Name:")
        self.caption_label.grid(in_= self.container_middle, row=7, column=0, sticky="nsew")
        
        self.textbox_new_id = tk.Text(self.window, height=2)
        self.textbox_new_id.grid(in_= self.container_middle, row=7, column=1, columnspan=3 , sticky="nsew")
        self.textbox_new_id.configure(state="disabled")

        self.button_submit = tk.Button(self.window, text='SAVE TO JSON', command=self.submit, state=DISABLED)
        self.button_submit.grid(in_= self.container_middle, row=8, column=0, columnspan=4, sticky="nsew", pady=20)

        ######################################################
        #self.display_selected_keys.set("")

        self.json_container = tk.Frame(self.window)
        self.textbox_json = tk.Text(self.window)
        self.json_container.grid(row=0, column=2, sticky="nsew")
        self.json_container.grid_rowconfigure(0, weight=1)
        self.json_container.grid_rowconfigure(1, weight=1)
        self.json_container.grid_columnconfigure(0, weight=1)
        self.display_selected_keys = tk.StringVar()
        self.textbox_display = tk.Message(self.window, textvariable=self.display_selected_keys, anchor="c")
        self.textbox_display.grid(in_= self.json_container, row=0, column=0, sticky="nsew")
        self.textbox_json.grid(in_= self.json_container,row=1, column=0, sticky="nsew")
        self.scroll_bar = tk.Scrollbar(self.window, command=self.textbox_json.yview)
        self.scroll_bar.grid(in_= self.json_container,row=1, column=1, sticky='nsew')
        self.textbox_json['yscrollcommand'] = self.scroll_bar.set

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

        self.new_keyword_dict = {}
        self.all_menu_buttons = []
        self.all_button_add_keyword = []
        self.all_textbox_new_keyword = []
        for self.category in self.category_keyword_dictionary:
            self.keyword_state_per_category = {}
            self.textbox_category_label = tk.Label(self.window, text=self.category)
            self.textbox_category_label.grid(in_= self.container_categories, row=row_id, column=0, sticky="nsew")

            menu = Menubutton(self.window, text='SELECT', relief=RAISED)
            self.all_button_add_keyword.append(menu)

            menu.grid(in_= self.container_categories, row=row_id, column=1, sticky="nsew")
            menu.menu  =  Menu ( menu, tearoff = 0 )
            menu["menu"]  =  menu.menu

            for self.keyword in self.category_keyword_dictionary[self.category]:
                self.keyword_variable = tk.BooleanVar()
                checkbutton = menu.menu.add_checkbutton(label=self.keyword, onvalue=True, offvalue=False, variable=self.keyword_variable)

                self.keyword_state_per_category[self.keyword] = self.keyword_variable
                
            self.textbox_new_keyword = tk.Text(self.window, height=2)
            self.all_textbox_new_keyword.append(self.textbox_new_keyword)
            self.new_keyword_dict[self.category] = self.textbox_new_keyword
            self.textbox_new_keyword.grid(in_= self.container_categories, row=row_id, column=2, sticky="nsew")
            

            self.button_add_keyword = tk.Button(self.window, text='ADD KEYWORD', command=partial(self.add_keyword,self.category))
            self.all_button_add_keyword.append(self.button_add_keyword)

            self.button_add_keyword.grid(in_=self.container_categories, row=row_id, column=3, sticky="nsew") 
            
            
            self.keyword_state_dict[self.category] = self.keyword_state_per_category
            row_id += 1

            self.container_categories.grid(in_= self.container_middle, row=0, column=0, columnspan=4, sticky="nsew")

    def add_keyword(self, category):
        global row_id
        new_keyword = self.new_keyword_dict[category].get("1.0", tk.END)
        new_keyword = new_keyword.strip()
        if(len(new_keyword) > 0):
            if(new_keyword not in self.category_keyword_dictionary[category]):
                self.category_keyword_dictionary[category].append(new_keyword)
                config_file_dictionary["category_keywords"] = self.category_keyword_dictionary
                with open(config_file_location, 'w') as fp:
                    json.dump(config_file_dictionary, fp)
                self.container_categories.destroy()
                row_id = 0
                keyword_state_dict_copy = {}
                for category in self.keyword_state_dict:
                    keyword_state_per_category_copy = {}
                    for keyword in self.keyword_state_dict[category]:
                        keyword_state_per_category_copy[keyword] = self.keyword_state_dict[category][keyword].get()
                    keyword_state_dict_copy[category] = keyword_state_per_category_copy
                self.create_checklist()
                for category in keyword_state_dict_copy:
                    for keyword in keyword_state_dict_copy[category]:
                        self.keyword_state_dict[category][keyword].set(keyword_state_dict_copy[category][keyword])
                
            else:
                messagebox.showwarning("Error", "Keyword already exists!")
        else:
            messagebox.showwarning("Error", "Enter a keyword first")
        
    def radiobutton_click(self):
        if self.radio_button_var.get()==1:
            self.textbox_new_id.configure(state="normal")
        else:
            self.textbox_new_id.configure(state="disabled")

    def transitionbutton_click(self):
        if self.is_snippet_transition_var.get()==1:
            self.textbox_sentence.delete("1.0",tk.END)
            self.textbox_new_id.delete("1.0",tk.END)
            self.block_annotation_buttons()
            self.is_snippet_transition.configure(state=NORMAL)
            self.button_submit.configure(state=NORMAL)
        else:
            self.unblock_annotation_buttons()

    def checked_checkbutton(self):
        if(self.is_event_checkbutton_var.get()):
            self.button_generate_new_id.configure(state=NORMAL)
            if self.radio_button_var.get()==1:
                self.textbox_new_id.configure(state="normal")
            if(self.current_event_id > 0):
                self.button_previous_id.configure(state=NORMAL)
        else:
            self.button_previous_id.configure(state=DISABLED)
            self.button_generate_new_id.configure(state=DISABLED)
            self.textbox_new_id.configure(state="disabled")

    def submit(self):
        category_caption_dict = {}

        if(self.is_snippet_transition_var.get()):
            self.textbox_json.delete("1.0",tk.END)
            category_caption_dict['transition'] = True
        else:
            if(self.is_event_checkbutton_var.get()):
                
                if(self.radio_button_var.get()==0 and str(self.current_snippet) not in self.output_dict):
                    messagebox.showwarning("Error", "Either generate new event id or select the previous event id!")
                    return
                elif(self.radio_button_var.get()==1 and self.textbox_new_id.get("1.0",tk.END).strip() == ""):
                    messagebox.showwarning("Error", "Give some event name!")
                    return
            category_dict = {}
            category_caption_dict['transition'] = False
            for category in self.keyword_state_dict:
                keyword_dict = []
                for keyword in self.keyword_state_dict[category]:
                    if self.keyword_state_dict[category][keyword].get():
                        keyword_dict.append(keyword)
                if len(keyword_dict)>0:
                    category_dict[category] = keyword_dict
            category_caption_dict['categories'] = category_dict
            if(len(category_caption_dict['categories'])==0):
                messagebox.showwarning("Error", "You must add some keywords to non-transition snippets!")
                return
            self.textbox_json.delete("1.0",tk.END)
            if(self.textbox_sentence.get("1.0",tk.END).rstrip('\n') != ""):
                category_caption_dict['caption'] = self.textbox_sentence.get("1.0",tk.END).rstrip('\n')
            if(self.is_event_checkbutton_var.get()):
                self.mega_event_dic = {}
                if(self.radio_button_var.get()==1):
                    if str(self.current_snippet) in self.output_dict and 'mega_event' in self.output_dict[str(self.current_snippet)]:
                        temp_event_id =  self.output_dict[str(self.current_snippet)]['mega_event']['id']
                        temp_event_name =  self.output_dict[str(self.current_snippet)]['mega_event']['name']
                        prompt_message = "In current snippet, event id is " + str(temp_event_id) + ", do you want to update ?"
                        answer = messagebox.askyesno("Question",prompt_message)
                        if answer:
                            self.current_event_id += 1
                            self.current_event_name = self.textbox_new_id.get("1.0",tk.END).rstrip('\n')
                            self.button_previous_id_var.set("USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
                            self.mega_event_dic["id"] = self.current_event_id
                            self.mega_event_dic["name"] = self.current_event_name
                        else:
                            prompt_message_en = "In current snippet, event name is '" + str(temp_event_name) + "', do you want to update ?"
                            answer_en = messagebox.askyesno("Question",prompt_message_en)
                            if answer_en:
                                self.current_event_name = self.textbox_new_id.get("1.0",tk.END).rstrip('\n')
                                self.mega_event_dic["id"] = self.current_event_id
                                self.mega_event_dic["name"] = self.current_event_name
                            else:
                                self.mega_event_dic["id"] = temp_event_id
                                self.mega_event_dic["name"] = temp_event_name   
                    else:
                        self.current_event_id += 1
                        self.current_event_name = self.textbox_new_id.get("1.0",tk.END).rstrip('\n')
                        self.button_previous_id_var.set("USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
                        self.mega_event_dic["id"] = self.current_event_id
                        self.mega_event_dic["name"] = self.current_event_name
                else:
                    self.mega_event_dic["id"] = self.current_event_id
                    self.mega_event_dic["name"] = self.current_event_name
                category_caption_dict['mega_event'] = self.mega_event_dic

        
        self.output_dict[str(self.current_snippet)] = category_caption_dict

        if(str(self.current_snippet) in self.output_dict):
            currect_snippet_dict = self.output_dict[str(self.current_snippet)]
            if("mega_event" in currect_snippet_dict):
                previous_event_name = currect_snippet_dict["mega_event"]["name"].rstrip('\n')
                # print("previous_event_name = "+previous_event_name)
                new_event_name = self.textbox_new_id.get("1.0",tk.END).strip()
                # print("new_event_name = "+new_event_name)
                if(previous_event_name != new_event_name):
                    event_id = currect_snippet_dict["mega_event"]["id"]
                    for each_key in self.output_dict.keys():
                        if each_key not in self.dict_keys and 'mega_event' in self.output_dict[each_key]:
                            if(self.output_dict[each_key]["mega_event"]["id"] == event_id):
                                self.output_dict[each_key]["mega_event"]["name"] = new_event_name
                                # print("Done")

        with open(self.video_file_name_with_location + '.json', 'w') as fp:
            json.dump(self.output_dict, fp)

        if str(self.current_snippet) in self.output_dict.keys():
            self.display_message()
        else:
            self.display_selected_keys.set("")

        self.textbox_json.configure(state=NORMAL)
        self.textbox_json.delete("1.0",tk.END)
        self.textbox_json.insert(tk.END, json.dumps(self.output_dict, indent=4))
        self.textbox_json.configure(state=DISABLED)
        if 'mega_event' in self.output_dict[str(self.current_snippet)]:
            if(self.output_dict[str(self.current_snippet)]["mega_event"]["id"] == self.current_event_id):
                self.current_event_name = self.output_dict[str(self.current_snippet)]["mega_event"]["name"]
        self.button_previous_id_var.set("USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
        self.set_window_name()

    def same_as_previous(self):
        if(str(self.current_snippet-1) in self.output_dict):
            for category in self.keyword_state_dict:
                for keyword in self.keyword_state_dict[category]:
                    self.keyword_state_dict[category][keyword].set(False)
            message = ""
            if('categories' in self.output_dict[str(self.current_snippet-1)]):
                currect_snippet_dict = self.output_dict[str(self.current_snippet-1)]['categories']
                for category in currect_snippet_dict:
                    message += category.upper() + ': '
                    for keyword in currect_snippet_dict[category]:
                        message += keyword + ', '
                        self.keyword_state_dict[category][keyword].set(True)
                    message += '\n'
            self.textbox_sentence.delete("1.0",tk.END)
            if('caption' in self.output_dict[str(self.current_snippet-1)]):
                self.textbox_sentence.insert(tk.END, self.output_dict[str(self.current_snippet-1)]['caption'])
            self.display_selected_keys.set(message)
        
    def block_video_buttons(self):
        self.button_next.configure(state=DISABLED)
        self.button_browse.configure(state=DISABLED)
        self.button_previous.configure(state=DISABLED)
        self.button_play.configure(state=DISABLED)
        self.textbox_goto.configure(state="disabled")
        self.button_goto.configure(state=DISABLED)

    def unblock_video_buttons(self):
        self.button_next.configure(state=NORMAL)
        self.button_browse.configure(state=NORMAL)
        self.button_previous.configure(state=NORMAL)
        self.button_play.configure(state=NORMAL)
        self.textbox_goto.configure(state="normal")
        self.button_goto.configure(state=NORMAL)

    def block_annotation_buttons(self):
        for btns in self.all_button_add_keyword:
            btns.configure(state=DISABLED)
        for txtbx in self.all_textbox_new_keyword:
            txtbx.configure(state="disabled")      
        for btns in self.all_menu_buttons:
            btns.configure(state=DISABLED)
        self.button_same_as_previous.configure(state=DISABLED)
        self.textbox_sentence.configure(state="disabled")      
        self.is_snippet_transition.configure(state=DISABLED)
        self.is_event_checkbutton.configure(state=DISABLED)
        self.button_submit.configure(state=DISABLED)
        self.button_generate_new_id.configure(state=DISABLED)
        self.button_previous_id.configure(state=DISABLED)
        self.textbox_new_id.configure(state=DISABLED)
        
    def unblock_annotation_buttons(self):
        for btns in self.all_button_add_keyword:
            btns.configure(state=NORMAL)
        for txtbx in self.all_textbox_new_keyword:
            txtbx.configure(state="normal")      
        for btns in self.all_menu_buttons:
            btns.configure(state=NORMAL)
        if(self.current_snippet>1):
            self.button_same_as_previous.configure(state=NORMAL)
        self.textbox_sentence.configure(state="normal")      
        self.is_snippet_transition.configure(state=NORMAL)
        self.is_event_checkbutton.configure(state=NORMAL)
        self.is_event_checkbutton_var.set(False)
        self.checked_checkbutton()
        self.button_submit.configure(state=NORMAL)
        if(str(self.current_snippet) in self.output_dict):
            self.is_event_checkbutton.configure(state=DISABLED)

    def resize(image):
        im = image
        new_siz = siz
        im.thumbnail(new_siz, Image.ANTIALIAS)
        return im

    def pause(self):
        if(self.flag_to_pause_video):
            self.text_pause_button.set("PAUSE")
            self.flag_to_pause_video = False
        else:
            self.text_pause_button.set("RESUME")
            self.flag_to_pause_video = True

    def restore_checklist(self):
        for category in self.keyword_state_dict:
            for keyword in self.keyword_state_dict[category]:
                self.keyword_state_dict[category][keyword].set(False)
        #self.textbox_sentence.configure(state=NORMAL)
        self.textbox_sentence.delete("1.0",tk.END)
        #self.textbox_sentence.configure(state=DISABLED)
        self.is_snippet_transition_var.set(False)
        self.is_event_checkbutton_var.set(False)
        self.radio_button_var.set(0)
        self.textbox_new_id.configure(state=NORMAL)
        self.textbox_new_id.delete("1.0",tk.END)
        self.textbox_new_id.configure(state=DISABLED)

        if(str(self.current_snippet) in self.output_dict):
            currect_snippet_dict = self.output_dict[str(self.current_snippet)]
            if(currect_snippet_dict["transition"]):
                self.is_snippet_transition_var.set(True)
                self.transitionbutton_click()
            else:
                if("categories" in currect_snippet_dict):
                    currect_snippet_categories_dict = currect_snippet_dict["categories"]
                    for category in currect_snippet_categories_dict:
                        for keyword in currect_snippet_categories_dict[category]:
                            self.keyword_state_dict[category][keyword].set(True)
                if("caption" in currect_snippet_dict):

                    self.textbox_sentence.insert(tk.END, currect_snippet_dict["caption"])
                if("mega_event" in currect_snippet_dict):
                    self.is_event_checkbutton_var.set(True)
                    self.checked_checkbutton()
                    if("name" in currect_snippet_dict["mega_event"]):
                        self.textbox_new_id.configure(state="normal")
                        self.textbox_new_id.insert(tk.END, currect_snippet_dict["mega_event"]["name"])
                self.is_snippet_transition.configure(state="disabled")
                self.is_event_checkbutton.configure(state="disabled")
                self.button_generate_new_id.configure(state="disabled")
                self.button_previous_id.configure(state="disabled")

    def play_snippet(self):
        self.snippet_location = '.tmp/' + str(self.current_snippet) + '.' + str(self.video_file_extension)
        self.snippet_capture = cv2.VideoCapture(self.snippet_location)
        while(self.snippet_capture.isOpened()):
            if(self.flag_to_pause_video):
                continue
            ret, frame = self.snippet_capture.read()
            #if(ret == True and not self.flag_to_stop_video):
            if ret:
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
                self.unblock_video_buttons()
                self.text_pause_button.set("PAUSE")
                self.button_pause.configure(state=DISABLED)
                if(self.current_snippet == self.snippet_count):
                    self.button_next.configure(state=DISABLED)
                if(self.current_snippet == 1):
                    self.button_previous.configure(state=DISABLED)
                self.flag_to_pause_video = False
                break
        self.snippet_capture.release()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if(ret and not(self.flag_to_stop_video)):
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
        self.window.after(self.delay, self.update)

    def get_snippet_count(self):
        self.video_length = subprocess.check_output(("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", self.video_file_location)).strip()
        self.video_length = int(float(self.video_length))
        # print("Video length in seconds: "+ str(self.video_length)) 
        self.snippet_count = ceildiv(self.video_length, self.snippet_length)

    def stop(self):
        self.flag_to_stop_video = True
        time.sleep(1/20)

    def play(self):
        self.flag_to_stop_video = False
        if(self.current_snippet <= self.snippet_count):
            self.text_current_snippet.set("Playing snippet number " + str(self.current_snippet))
            self.block_video_buttons()
            self.button_pause.configure(state=NORMAL)
            self.text_play_button.set("REPLAY")

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
            if (self.current_snippet == self.snippet_count):
                self.button_next.configure(state=DISABLED) 
            if str(self.current_snippet-1) not in self.output_dict.keys():
                self.block_annotation_buttons()
            else:
                self.unblock_annotation_buttons()
            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")

            self.text_current_snippet.set("Playing snippet number " + str(self.current_snippet))
            #self.button_previous.configure(state=NORMAL)
            if(self.current_snippet == self.snippet_count):
                self.button_next.configure(state=DISABLED)
            self.stop()    
            self.play()
            self.restore_checklist()

        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")
        self.set_window_name()

    def display_message(self):
        message = ""
        if 'categories' in self.output_dict[str(self.current_snippet)]: 
            for cat, listt in self.output_dict[str(self.current_snippet)]['categories'].items():
                message += cat.upper() + ': '
                for checked_keys in self.output_dict[str(self.current_snippet)]['categories'][cat]:
                    message += checked_keys.rstrip('\n') + ', '
                message += '\n'
        if 'mega_event' in self.output_dict[str(self.current_snippet)]: 
            message += 'EVENT ID: ' + str(self.output_dict[str(self.current_snippet)]['mega_event']['id']) + ', '
            message += '\n'
            message += 'EVENT NAME: ' + str(self.output_dict[str(self.current_snippet)]['mega_event']['name']) + ', '
            message += '\n'
        self.display_selected_keys.set(message)

    def previous(self):
        self.textbox_sentence.delete("1.0",tk.END)
        self.stop()
        if(self.current_snippet > 1):
            self.current_snippet -= 1
            if(self.current_snippet==1):
                self.unblock_annotation_buttons()
            elif str(self.current_snippet-1) not in self.output_dict.keys():
                self.block_annotation_buttons()
            else:
                self.unblock_annotation_buttons()

            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")                

            self.text_current_snippet.set("Playing " + str(self.current_snippet))
            self.button_next.configure(state=NORMAL)
            self.stop()
            self.play()
            if(self.current_snippet == 1):
                self.button_previous.configure(state=DISABLED)
            self.restore_checklist()

        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")
        self.set_window_name()

    def goto(self):
        self.textbox_sentence.delete("1.0",tk.END)
        self.goto_snippet = self.textbox_goto.get("1.0",tk.END)
        self.goto_snippet = int(self.goto_snippet)
        self.stop()
        if(self.goto_snippet <= self.snippet_count):
            self.current_snippet = self.goto_snippet
            if (self.current_snippet == self.snippet_count):
                self.button_next.configure(state=DISABLED) 
            if self.current_snippet == 1:
                self.unblock_annotation_buttons()
            elif str(self.current_snippet-1) not in self.output_dict.keys():
                self.block_annotation_buttons()
            else:
                self.unblock_annotation_buttons()
            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")
            self.text_current_snippet.set("Playing snippet number " + str(self.current_snippet))
            self.restore_checklist()
            self.stop()
            self.play()
        else:
            self.text_current_snippet.set("Selected snippet number is greater than total number of snippets")
        self.textbox_goto.delete("1.0",tk.END)
        self.set_window_name()

    def check():
        d = ""
        for i in range(len(OPTIONS)):
            for j in range(len(OPTIONS[i])):
                if all_bool_var[i][j].get():
                    d += OPTIONS[i][j] + " "
        text_current_snippet.set(d)

    def browse(self):
        self.stop()
        
        ## Resetting Things
        self.display_selected_keys.set("")

        self.current_event_id = 0
        self.current_event_name = "_"

        self.button_previous_id_var.set("USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
        self.textbox_json.configure(state=NORMAL)
        self.textbox_json.delete("1.0",tk.END)
        self.textbox_json.configure(state=DISABLED)
        self.restore_checklist()
        self.text_snippet_count.set("")
        self.text_current_snippet.set("")
        self.textbox_new_id.delete("1.0",tk.END)
        self.textbox_new_id.configure(state=DISABLED)
        self.text_video_file_location.set("")
        ##################

        self.video_file_location = askopenfilename()
        if(isinstance(self.video_file_location, tuple)):
            return

        self.video_file_extension = self.video_file_location.split('.')[1]
        if(self.video_file_extension != 'mp4' and self.video_file_extension != 'avi'):
            self.text_current_snippet.set("Chosen file is not a video file")
            return    

        self.video_file_name_with_location = self.video_file_location.split('.')[0]
        self.json_file_name_with_location = self.video_file_name_with_location + '.json'
        self.output_dict = {}
        self.current_snippet = 1
        self.text_play_button.set("PLAY")
        self.dict_keys = ["video_name", "video_category", "snippet_size", "duration", "num_snippets"]
        if path.exists(self.json_file_name_with_location):
            with open(self.json_file_name_with_location) as json_file:  
                self.output_dict = json.load(json_file)
            
            self.textbox_json.configure(state=NORMAL)
            self.textbox_json.delete("1.0",tk.END)
            self.textbox_json.insert(tk.END, json.dumps(self.output_dict, indent=4))
            self.textbox_json.configure(state=DISABLED)

            for each_key in self.output_dict.keys():
                if each_key not in self.dict_keys and 'mega_event' in self.output_dict[str(each_key)]:
                    if int(self.output_dict[str(each_key)]['mega_event']['id']) > self.current_event_id:
                        self.current_event_id = int(self.output_dict[str(each_key)]['mega_event']['id'])
                        self.current_event_name = self.output_dict[str(each_key)]['mega_event']['name']
                if each_key not in self.dict_keys and int(each_key) > self.current_snippet: 
                    self.current_snippet = int(each_key)
            # print(self.current_event_id,self.current_event_name)
            self.button_previous_id_var.set("USE PREVIOUS ID: " + str(self.current_event_id) + ": " + self.current_event_name)
            if str(self.current_snippet) in self.output_dict.keys():
                self.display_message()
            else:
                self.display_selected_keys.set("")
        self.video_file_name = self.video_file_name_with_location.split('/')[-1]
        self.window.title(self.video_file_name)
        self.get_snippet_count()
        self.output_dict['video_name'] = self.video_file_location.split('/')[-1]
        self.output_dict['video_category'] = self.video_file_name.split('_')[0]
        self.output_dict['snippet_size'] = self.snippet_length
        self.output_dict['num_snippets'] = self.snippet_count
        self.output_dict['duration'] = self.video_length
        
        self.get_snippet_count()
        self.text_snippet_count.set("Total number of snippets are " + str(self.snippet_count))
        self.split_command = "python3 splitter/ffmpeg-split.py -f " + self.video_file_location + " -s " + str(self.snippet_length) + " >/dev/null 2>&1"
        
        self.text_video_file_location.set(self.video_file_location)
        self.text_current_snippet.set("Selected snippet number " + str(self.current_snippet))
        os.system(self.split_command)
        self.unblock_video_buttons()
        if(self.current_snippet > 1):
            self.button_same_as_previous.configure(state=NORMAL) 
            if(self.current_snippet == self.snippet_count):
                self.button_next.configure(state=DISABLED)     
        else:
            self.button_previous.configure(state=DISABLED) 

        self.set_window_name()
        self.restore_checklist()
        self.button_submit.configure(state=NORMAL)

    def get_max_done_snippet_id(self):
        max_key = 0
        for each_key in self.output_dict.keys():
            if each_key not in self.dict_keys and int(each_key) > max_key:
                max_key = int(each_key)
        return max_key

    def set_window_name(self):
        max_done_snippet_id = self.get_max_done_snippet_id()
        self.window.title(self.video_file_name +"."+ self.video_file_extension +" (# Annotated Snippets: "+ str(max_done_snippet_id) + " / " + str(self.snippet_count) + ")")

config_file_location = sys.argv[1]
with open(config_file_location) as json_file:  
    config_file_dictionary = json.load(json_file)

snippet_length = config_file_dictionary["snippet_size"]
category_keyword_dictionary = config_file_dictionary["category_keywords"]

# Create a window and pass it to the Application object
w = App(tk.Tk(), snippet_length, category_keyword_dictionary)