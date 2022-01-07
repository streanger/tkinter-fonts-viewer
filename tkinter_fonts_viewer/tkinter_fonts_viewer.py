"""tkinter_fonts_viewer
version: 0.1.1
date: 31.05.2020
author: streanger
"""
import os
import time
import json
import string
import ctypes
from threading import Thread
from tkinter import (
    Tk,
    Frame,
    Label,
    Listbox,
    Entry,
    Button,
    StringVar,
    Scrollbar,
    Toplevel,
    messagebox,
    font,
    YES,
    NO,
    BOTH,
    TOP,
    BOTTOM,
    LEFT,
    RIGHT,
    X,
    Y,
    END,
    IntVar,
    Checkbutton,
)
import pkg_resources
from tkinter.messagebox import showinfo
from itertools import cycle



def static_file_path(directory, file):
    """ get path of the specified file from specified directory"""
    resource_path = "/".join((directory, file))  # Do not use os.path.join()
    try:
        template = pkg_resources.resource_filename(__name__, resource_path)
    except KeyError:
        return (
            "none"  # empty string cause AttributeError, and non empty FileNotFoundError
        )
    return template


def fonts_type():
    """get known fonst status"""
    fonts_file_path = static_file_path("fonts", "fonts_status.json")

    # read known fonts from json
    try:
        with open(fonts_file_path) as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {}
    return data


def viewer():
    """main application gui"""
    app = TkinterFontsViewer(master=Tk())
    app.mainloop()


class FontsMonoCheck(Frame): # pylint: disable=too-many-ancestors
    """class for testing fonts mono status
    https://stackoverflow.com/questions/4481880/minimizing-a-tk-window
    """

    def __init__(self, master, fonts):
        super().__init__(master)
        self.master.geometry("30x30")
        self.master.iconify()  # minimized window

        self.test_label = Label(self.master)
        self.test_label.pack(expand=NO, fill=Y, side=BOTTOM)

        # fonts = font.families()
        self.fonts = fonts
        self.fonts_mono_status = {}
        self.test_thread = Thread(target=self.check_fonts_thread, args=(self.fonts,))
        self.test_thread.start()

    def cleanup(self):
        """join thread and destroy window"""
        self.test_thread.join()
        self.master.destroy()

    def check_fonts_thread(self, fonts):
        """check fonts in thread"""
        default_color = self.master.cget("bg")

        for checked_font in fonts:
            # set proper font
            test_font = font.Font(family=checked_font, size=11)
            self.test_label.config(font=test_font, fg=default_color)  # invisible color

            # set '.' as text
            self.test_label.config(text=".")
            self.master.update()  # this is needed for true width value
            dot_width = self.test_label.winfo_width()

            # set 'm' as text
            self.test_label.config(text="m")
            self.master.update()  # this is needed for true width value
            m_width = self.test_label.winfo_width()

            # show & compare sizes
            status = bool(m_width == dot_width)
            # out[checked_font] = status
            self.fonts_mono_status[checked_font] = status

        self.test_label.pack_forget()
        self.master.update()
        # print('inside')
        time.sleep(0.01)
        self.master.quit()
        self.master.update()


class TkinterFontsViewer(Frame): # pylint: disable=too-many-ancestors
    """gui viewer for tkinter fonts"""

    def __init__(self, master, resizable=True, hide_console=False):
        # *********** INIT, HIDE, CLOSING ***********
        if hide_console:
            self.hide_console()
        super().__init__(master)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.geometry("{}x{}+333+50".format(800, 500))
        # self.master.geometry("{}x{}+333+50".format(1000, 500))
        if resizable:
            self.master.resizable(width=True, height=True)
        else:
            self.master.resizable(width=False, height=False)
        self.master.wm_title("tkinter fonts viewer")
        self.pack()

        # *********** APP GUI, CONST, VARIABLES ***********
        if os.name == 'nt':
            app_font = "Lucida console"
        else:
            app_font = "FreeMono"
        # raised, sunken, flat, ridge, solid, groove
        self.RELIEF_TYPE = "groove"
        self.MONO_FONT_INFO = font.Font(
            family=app_font, size=10, weight="normal"
        )
        self.MONO_BUTTON = font.Font(family=app_font, size=25, weight="normal")
        self.MONO_FONT_INFO_UPPER = font.Font(
            family=app_font, size=12, weight="normal"
        )
        self.user_text = ''
        self.test_examples = cycle([
            '\n'.join([string.digits, string.ascii_lowercase, string.ascii_uppercase, string.punctuation]),
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam...',
            'I know I can do it, Todd Downey said, helping himself to another ear of corn from the steaming bowl. I’m sure that in time, every bit of her will be gone, and her death will be a mystery. Even to me.',
            "If you haven't found something strange during the day, it hasn't been much of a day",
            '\n'.join(['❄', '❄❄❄', '☃☃☃☃☃', '❄❄❄', '❄']),
            '¯\_( ͡❛ ͜ʖ ͡❛)_/¯',
            '',
        ])
        
        # *********** FONTS MONO STATUS ***********
        self.FONTS_MODE = 0
        self.FONTS_MODES_DICT = {
            0: "all",
            1: "normal",
            2: "mono",
        }

        self.ALL_FONTS = font.families()
        self.ALL_FONTS = sorted(list(set(self.ALL_FONTS)))  # remove duplicates
        self.FONTS_MONOSPACE_STATUS = self.check_if_mono(self.ALL_FONTS)
        self.INDEX = 0

        self.MONO_FONTS = []
        self.NORMAL_FONTS = []

        for key, value in self.FONTS_MONOSPACE_STATUS.items():
            if value:
                self.MONO_FONTS.append(key)
            else:
                self.NORMAL_FONTS.append(key)

        self.FONTS_TO_SHOW = self.ALL_FONTS  # current fonts to show
        self.FILTER = ""
        self.FONTS_FILTERED = self.filter_fonts(
            self.FONTS_TO_SHOW, self.FILTER  # at start show all fonts
        )
        self.NUMBER_OF_FONTS = len(self.FONTS_FILTERED)
        self.current_font = self.FONTS_FILTERED[0]
        
        
        # *********** CREATE WIDGETS ***********
        self.default_color = self.master.cget("bg")
        self.BG_COLOR_MONO = "#ADD8E6"
        self.BG_COLOR_NORMAL = self.default_color
        self.create_widgets()

        # *********** LIFT, GET FOCUS ***********
        self.master.lift()  # move window to the top
        self.master.focus_force()

    @staticmethod
    def hide_console():
        """hide console window"""
        if os.name == "nt":
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )

    @staticmethod
    def read_json(file):
        """read json file, to dict"""
        try:
            with open(file) as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {}
        return data

    @staticmethod
    def write_json(file, data):
        """write dict, to json file"""
        with open(file, "w") as json_file:
            # ensure_ascii -> False/True -> characters/u'type'
            json.dump(data, json_file, sort_keys=True, indent=4, ensure_ascii=False)

    def check_if_mono(self, fonts):
        """check fonts mono status with new window
        https://stackoverflow.com/questions/16115378/tkinter-example-code-for-multiple-windows-why-wont-buttons-load-correctly
        """
        # get paths
        fonts_file_path = static_file_path("fonts", "fonts_status.json")
        fonts_dir_path = static_file_path("fonts", "")

        # read known fonts from json
        known_fonts_status = self.read_json(fonts_file_path)
        known_fonts_keys = list(known_fonts_status.keys())

        # compare specified with known, and separate not checked
        not_checked_fonts = []
        specified_fonts_status = {}

        for font_to_check in fonts:
            if not font_to_check in known_fonts_keys:
                not_checked_fonts.append(font_to_check)
            else:
                specified_fonts_status[font_to_check] = known_fonts_status[
                    font_to_check
                ]

        if not_checked_fonts:
            # iter through not checked
            self.new_window = Toplevel(self.master)
            test_app = FontsMonoCheck(self.new_window, not_checked_fonts)
            test_app.mainloop()
            test_app.cleanup()

            # append checked fonts to current known
            checked_fonts = test_app.fonts_mono_status
            specified_fonts_status = {**specified_fonts_status, **checked_fonts}

            # store updated dict to json
            updated_json = {**known_fonts_status, **checked_fonts}

            if not os.path.exists(fonts_dir_path):
                os.makedirs(fonts_dir_path)

            self.write_json(fonts_file_path, updated_json)

        return specified_fonts_status

    def on_closing(self):
        """handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.master.destroy()  # destroy main app
            self.master.quit()
            
    def bg_color(self, status):
        """get bg color depend on status"""
        if status:
            return self.BG_COLOR_MONO
        return self.BG_COLOR_NORMAL
        
    def perform_center_text(self, text):
        """perform text(font name), to fit main label"""
        # no wrap for not; dynamic in main label
        return text
        
        # wrap_status = self.wrap_text_var.get()
        # if not wrap_status:
            # return text
        if len(text.split()) > 2:
            text = "\n".join(text.split())
        elif len(text.split()) == 2 and len(text) > 14:
            text = "\n".join(text.split())
        else:
            if len(text) > 16:
                text = "\n".join(text.split())
        return text
        
        
    def entry_callback(self, event):
        """entries callback"""
        self.user_text = self.main_text_entry.get().strip()
        
        # ********* update main label *********
        if self.user_text:
            main_text = self.user_text
        else:
            main_text = self.current_font
        center_text = self.perform_center_text(main_text)
        main_font = font.Font(family=self.current_font, size=50, weight="normal")
        self.main_label.config(font=main_font, text=center_text)
        
        # set focus on other item
        self.left_listbox.focus()
        
        
    def filter_callback(self, event):
        """filter callback"""

        # ******** perform value ********
        value = self.filter_entry.get()
        self.FILTER = str(value.strip().lower())
        new_entry_text = self.FILTER

        # ******** update filtered list ********
        self.FONTS_FILTERED = self.filter_fonts(self.FONTS_TO_SHOW, self.FILTER)
        self.NUMBER_OF_FONTS = len(self.FONTS_FILTERED)
        
        
        # ******** update widgets ********
        # update total fonts label
        self.top_info_left_down.config(text=self.NUMBER_OF_FONTS)
        self.INDEX = 0
        
        
        # ******** update listbox ********
        self.clear_listbox()
        self.fill_listbox(self.FONTS_FILTERED)
        
        self.left_listbox.focus()
        
        

    @staticmethod
    def filter_fonts(fonts, filter_str):
        """filter list of fonts"""
        return [font for font in fonts if filter_str.lower() in font.lower()]

    def switch_font_mode(self):
        """switch sound mode"""
        self.FONTS_MODE = (self.FONTS_MODE + 1) % 3

        if self.FONTS_MODE == 0:
            self.FONTS_TO_SHOW = self.ALL_FONTS
        elif self.FONTS_MODE == 1:
            self.FONTS_TO_SHOW = self.NORMAL_FONTS
        elif self.FONTS_MODE == 2:
            self.FONTS_TO_SHOW = self.MONO_FONTS

        # ******** update filtered list ********
        self.FONTS_FILTERED = self.filter_fonts(self.FONTS_TO_SHOW, self.FILTER)
        self.NUMBER_OF_FONTS = len(self.FONTS_FILTERED)
        
        
        # ******** update widgets ********
        self.top_info_left_down.config(text=self.NUMBER_OF_FONTS)
        self.INDEX = 0

        # update mode label
        button_text = "{}\n{}".format(
            # " mode ", self.FONTS_MODES_DICT[self.FONTS_MODE].upper()
            " mode ", self.FONTS_MODES_DICT[self.FONTS_MODE].lower()
        )
        self.mode_button.config(text=button_text)


        # ******** update listbox ********
        self.clear_listbox()
        self.fill_listbox(self.FONTS_FILTERED)
        
        
    def items_selected(self, event):
        """handle item selected event
        https://www.pythontutorial.net/tkinter/tkinter-listbox/
        """
        # ********* get selected item *********
        selected_index = self.left_listbox.curselection()
        if not selected_index:
            return None
        selected_item = self.left_listbox.get(selected_index)
        self.current_font = selected_item
        print('[*] {}: {}'.format(selected_index, selected_item))
        
        
        # ********* update main label *********
        if self.user_text:
            main_text = self.user_text
        else:
            main_text = selected_item
        center_text = self.perform_center_text(main_text)
        main_font = font.Font(family=self.current_font, size=50, weight="normal")
        self.main_label.config(font=main_font, text=center_text)
        return None
        
        
    def clear_listbox(self):
        self.left_listbox.delete(0, END)
        return None
        
        
    def fill_listbox(self, values):
        for index, value in enumerate(values):
            self.left_listbox.insert(END, value)
            # check mono status
            if self.FONTS_MONOSPACE_STATUS[value]:
                self.left_listbox.itemconfig(index, bg="#9ae9f5")
        return None
        
        
    def switch_example_text(self):
        print('[*] example text')
        self.main_text_entry.delete(0, END)
        self.user_text = next(self.test_examples)
        self.main_text_entry.insert(0, self.user_text)
        
        center_text = self.perform_center_text(self.user_text)
        main_font = font.Font(family=self.current_font, size=50, weight="normal")
        self.main_label.config(font=main_font, text=center_text)
        return None
        
        
    def create_widgets(self):
        """create widgets from dict object"""

        # ********* bind key event for master widget *********
        self.main_frame = Frame(self.master)
        self.main_frame.pack(expand=YES, fill=BOTH, side=BOTTOM)
        
        
        # ********* listbox *********
        self.left_listbox = Listbox(self.main_frame)
        self.left_listbox.pack(expand=NO, fill=BOTH, side=LEFT)
        self.left_scrollbar = Scrollbar(self.main_frame)
        self.left_scrollbar.pack(expand=NO, fill=BOTH, side=LEFT)
        self.fill_listbox(self.FONTS_TO_SHOW)
        self.left_listbox.config(yscrollcommand=self.left_scrollbar.set, width=0)
        self.left_scrollbar.config(command=self.left_listbox.yview)
        self.left_listbox.bind('<<ListboxSelect>>', self.items_selected)
        self.left_listbox.focus()
        
        
        # ********* RIGHT FRAME *********
        self.right_frame = Frame(self.main_frame)
        self.right_frame.pack(expand=YES, fill=BOTH, side=RIGHT)

        # right top info
        self.top_info = Frame(self.right_frame)
        self.top_info.pack(expand=NO, fill=X, side=TOP)


        # ********* checkboxes *********
        # self.checkboxes_frame = Frame(self.top_info)
        # self.checkboxes_frame.pack(expand=YES, fill=BOTH, side=LEFT)
        
        
        # self.wrap_text_var = IntVar(value=1)
        # self.wrap_text_checkbox = Checkbutton(self.checkboxes_frame, text='wrap text', font=self.MONO_FONT_INFO_UPPER, variable=self.wrap_text_var)
        # self.wrap_text_checkbox.pack(expand=YES, fill=BOTH, side=TOP)
        
        # self.bold_font_var = IntVar(value=1)
        # self.bold_font_checkbox = Checkbutton(self.checkboxes_frame, text='bold', font=self.MONO_FONT_INFO_UPPER, variable=self.bold_font_var)
        # self.bold_font_checkbox.pack(expand=YES, fill=BOTH, side=TOP)
        
        # self.curved_font_var = IntVar(value=1)
        # self.curved_font_checkbox = Checkbutton(self.checkboxes_frame, text='curved', font=self.MONO_FONT_INFO_UPPER, variable=self.curved_font_var)
        # self.curved_font_checkbox.pack(expand=YES, fill=BOTH, side=TOP)
        
        
        # ********* mono-normal switch button *********
        button_text = "{}\n{}".format(
            " mode ", self.FONTS_MODES_DICT[self.FONTS_MODE].lower()
        )
        self.top_button_frame = Frame(self.top_info, relief=self.RELIEF_TYPE)
        self.top_button_frame.pack(expand=YES, fill=BOTH, side=LEFT)
        self.mode_button = Button(
            self.top_button_frame,
            font=self.MONO_FONT_INFO_UPPER,
            text=button_text,
            command=self.switch_font_mode,
        )
        self.mode_button.pack(expand=YES, fill=X, side=TOP)
        
        
        # ********* example button *********
        self.example_button = Button(
            self.top_info,
            font=self.MONO_FONT_INFO_UPPER,
            text='example',
            command=self.switch_example_text,
        )
        self.example_button.pack(expand=YES, fill=BOTH, side=LEFT)
        
        
        # ********* number of fonts *********
        self.top_info_left = Frame(self.top_info, relief=self.RELIEF_TYPE)
        self.top_info_left.pack(expand=YES, fill=BOTH, side=LEFT)
        self.top_info_left_up = Label(
            self.top_info_left,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO_UPPER,
            text="total fonts",
        )
        self.top_info_left_up.pack(expand=YES, fill=X, side=TOP)
        self.top_info_left_down = Label(
            self.top_info_left,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO_UPPER,
            text="{}".format(self.NUMBER_OF_FONTS),
        )
        self.top_info_left_down.pack(expand=YES, fill=X, side=BOTTOM)


        # ********* text entry *********
        entries_size = 13
        top_center_val = 15
        self.top_info_center_left = Frame(self.top_info, relief=self.RELIEF_TYPE)
        self.top_info_center_left.pack(expand=YES, fill=BOTH, side=LEFT)
        self.top_info_center_left_up = Label(
            self.top_info_center_left,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO_UPPER,
            text="text",
        )
        self.top_info_center_left_up.pack(expand=YES, fill=X, side=TOP)
        self.top_info_center_left_entry_sv = StringVar()
        self.main_text_entry = Entry(
            self.top_info_center_left,
            width=entries_size,
            font=self.MONO_FONT_INFO_UPPER,
            textvariable=self.top_info_center_left_entry_sv,
            justify="center",
        )
        self.main_text_entry.bind("<Return>", self.entry_callback)
        self.main_text_entry.pack(expand=YES, fill=X, side=BOTTOM)


        # ********* search entry *********
        self.top_filter_frame = Frame(self.top_info, relief=self.RELIEF_TYPE)
        self.top_filter_frame.pack(expand=YES, fill=BOTH, side=LEFT)

        self.top_filter_label = Label(
            self.top_filter_frame,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO_UPPER,
            text="search",
        )
        self.top_filter_label.pack(expand=YES, fill=X, side=TOP)
        self.top_filter_sv = StringVar()
        self.filter_entry = Entry(
            self.top_filter_frame,
            width=entries_size,
            font=self.MONO_FONT_INFO_UPPER,
            textvariable=self.top_filter_sv,
            justify="center"
        )
        self.filter_entry.bind("<Return>", self.filter_callback)
        self.filter_entry.pack(expand=YES, fill=X, side=BOTTOM)





        # ********* MAIN LABEL CONTENT *********
        starting_font = self.FONTS_FILTERED[self.INDEX]
        start_text = self.perform_center_text(starting_font)
        main_font = font.Font(family=starting_font, size=50, weight="normal")      # think of chaning font weight
        self.main_label = Label(
            # self.right_frame, relief=self.RELIEF_TYPE, font=main_font, text=start_text, wraplength=400,       # think of dynamic wraplength
            self.right_frame, relief=self.RELIEF_TYPE, font=main_font, text=start_text,
        )
        self.main_label.pack(expand=YES, fill=BOTH, side=BOTTOM)

        # dynamically wrap text in label
        self.main_label.bind('<Configure>', lambda x: self.main_label.config(wraplength=self.main_label.winfo_width()))
        return True


if __name__ == "__main__":
    viewer()


'''
https://stackoverflow.com/questions/5286093/display-listbox-with-columns-using-tkinter
https://fsymbols.com/emoticons/

build font into exe
https://stackoverflow.com/questions/70538010/distributing-python-programs-with-a-tkinter-gui-using-pysintaller
'''


