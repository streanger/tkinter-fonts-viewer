"""tkinter_fonts_viewer
version: 0.1.1
date: 31.05.2020
author: streanger
"""
import os
import time
import json
import ctypes
from threading import Thread
from tkinter import (
    Tk,
    Frame,
    Label,
    Entry,
    Button,
    StringVar,
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
)
import pkg_resources


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

    def __init__(self, master, resizable=False, hide_console=False):
        # *********** INIT, HIDE, CLOSING ***********
        if hide_console:
            self.hide_console()
        super().__init__(master)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.geometry("{}x{}+333+50".format(800, 500))
        if resizable:
            self.master.resizable(width=True, height=True)
        else:
            self.master.resizable(width=False, height=False)
        self.master.wm_title("gui_app")
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

    def index_down(self):
        """decrease shown font index"""
        self.INDEX -= 1
        self.INDEX = self.INDEX % self.NUMBER_OF_FONTS
        self.config_widgets()

    def index_up(self):
        """increase shown font index"""
        self.INDEX += 1
        self.INDEX = self.INDEX % self.NUMBER_OF_FONTS
        self.config_widgets()

    def bg_color(self, status):
        """get bg color depend on status"""
        if status:
            return self.BG_COLOR_MONO
        return self.BG_COLOR_NORMAL

    @staticmethod
    def mono_status_text(status):
        """get mono text depend on status"""
        if status:
            return " MONO "
        return "NORMAL"

    @staticmethod
    def perform_center_text(text):
        """perform text(font name), to fit main label"""
        if len(text.split()) > 2:
            text = "\n".join(text.split())
        elif len(text.split()) == 2 and len(text) > 12:
            text = "\n".join(text.split())
        else:
            if len(text) > 14:
                text = "\n".join(text.split("_"))
        return text

    def config_widgets(self):
        """config widgets"""
        center_val = 20
        top_center_val = 15

        # ******** current index entry ********
        self.current_index_entry.delete(0, "end")
        self.current_index_entry.insert(0, str(self.INDEX).center(top_center_val))

        first_index = (self.INDEX + 2) % self.NUMBER_OF_FONTS
        second_index = (self.INDEX + 1) % self.NUMBER_OF_FONTS
        third_index = (self.INDEX) % self.NUMBER_OF_FONTS
        fourth_index = (self.INDEX - 1) % self.NUMBER_OF_FONTS
        fifth_index = (self.INDEX - 2) % self.NUMBER_OF_FONTS

        first_font = self.FONTS_FILTERED[first_index]
        second_font = self.FONTS_FILTERED[second_index]
        third_font = self.FONTS_FILTERED[third_index]
        fourth_font = self.FONTS_FILTERED[fourth_index]
        fifth_font = self.FONTS_FILTERED[fifth_index]

        # ******** indexes labels ********
        first_status = self.FONTS_MONOSPACE_STATUS[first_font]
        first_index_text = "{}\n{}".format(
            first_index, self.mono_status_text(first_status)
        )
        self.first_index.config(text=first_index_text, bg=self.bg_color(first_status))

        second_status = self.FONTS_MONOSPACE_STATUS[second_font]
        second_index_text = "{}\n{}".format(
            second_index, self.mono_status_text(second_status)
        )
        self.second_index.config(
            text=second_index_text, bg=self.bg_color(second_status)
        )

        third_status = self.FONTS_MONOSPACE_STATUS[third_font]
        third_index_text = "{}\n{}".format(
            third_index, self.mono_status_text(third_status)
        )
        self.third_index.config(text=third_index_text, bg=self.bg_color(third_status))

        fourth_status = self.FONTS_MONOSPACE_STATUS[fourth_font]
        fourth_index_text = "{}\n{}".format(
            fourth_index, self.mono_status_text(fourth_status)
        )
        self.fourth_index.config(
            text=fourth_index_text, bg=self.bg_color(fourth_status)
        )

        fifth_status = self.FONTS_MONOSPACE_STATUS[fifth_font]
        fifth_index_text = "{}\n{}".format(
            fifth_index, self.mono_status_text(fifth_status)
        )
        self.fifth_index.config(text=fifth_index_text, bg=self.bg_color(fifth_status))

        # remeber to delete entries
        self.first_text.delete(0, "end")
        self.first_text.insert(0, first_font.center(center_val))

        self.second_text.delete(0, "end")
        self.second_text.insert(0, second_font.center(center_val))

        self.third_text.delete(0, "end")
        self.third_text.insert(0, third_font.center(center_val))

        self.fourth_text.delete(0, "end")
        self.fourth_text.insert(0, fourth_font.center(center_val))

        self.fifth_text.delete(0, "end")
        self.fifth_text.insert(0, fifth_font.center(center_val))

        # update main label
        center_text = self.perform_center_text(third_font)
        main_font = font.Font(family=third_font, size=50, weight="normal")
        self.main_label.config(font=main_font, text=center_text)

    def entry_callback(self, event):
        """entries callback"""

        # ******** perform value ********
        value = self.current_index_entry.get()
        try:
            self.INDEX = (int(value.strip())) % self.NUMBER_OF_FONTS
        except ValueError:
            pass

        # ******** update entry ********
        self.current_index_entry.delete(0, "end")
        self.current_index_entry.insert(0, str(self.INDEX).center(15))

        # ******** update widgets ********
        self.config_widgets()

    def filter_callback(self, event):
        """filter callback"""

        # ******** perform value ********
        value = self.filter_entry.get()
        self.FILTER = str(value.strip().lower())
        new_entry_text = self.FILTER

        # ******** update filtered list ********
        self.FONTS_FILTERED = self.filter_fonts(self.FONTS_TO_SHOW, self.FILTER)
        self.NUMBER_OF_FONTS = len(self.FONTS_FILTERED)

        if not self.NUMBER_OF_FONTS:
            self.FONTS_FILTERED = self.FONTS_TO_SHOW
            self.NUMBER_OF_FONTS = len(self.FONTS_FILTERED)
            new_entry_text = "<not-found>"

        # ******** update entry ********
        self.filter_entry.delete(0, "end")
        self.filter_entry.insert(0, new_entry_text.center(15))

        # ******** update widgets ********
        # update total fonts label
        self.top_info_left_down.config(text=self.NUMBER_OF_FONTS)
        self.INDEX = 0

        # update rest of widgets
        self.config_widgets()

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

        if not self.NUMBER_OF_FONTS:
            self.FONTS_FILTERED = self.FONTS_TO_SHOW
            self.NUMBER_OF_FONTS = len(self.FONTS_FILTERED)

        # ******** update widgets ********
        # update total fonts label
        self.top_info_left_down.config(text=self.NUMBER_OF_FONTS)
        self.INDEX = 0

        # update mode label
        button_text = "{}\n{}".format(
            " MODE ", self.FONTS_MODES_DICT[self.FONTS_MODE].upper()
        )
        self.mode_button.config(text=button_text)

        # update rest of widgets
        self.config_widgets()

    def key_event(self, event):
        """key events callback
            arrow up - 38
            arrow down - 40
        """
        code = event.keycode

        if code in (38, 111):
            self.index_up()

        elif code in (40, 116):
            self.index_down()

    def create_widgets(self):
        """create widgets from dict object"""

        # ********* bind key event for master widget *********
        self.master.bind("<Key>", self.key_event)

        self.top_label = Label(
            self.master, font=self.MONO_FONT_INFO_UPPER, text="TKINTER FONTS VIEWER"
        )
        self.top_label.pack(expand=NO, fill=X, side=TOP)

        self.main_frame = Frame(self.master)
        self.main_frame.pack(expand=YES, fill=BOTH, side=BOTTOM)

        self.left_buttons = Frame(self.main_frame)
        self.left_buttons.pack(expand=NO, fill=BOTH, side=LEFT)

        # ********* up - down buttons *********
        self.button_up = Button(
            self.left_buttons, font=self.MONO_BUTTON, text="↑", command=self.index_up
        )
        self.button_up.pack(expand=YES, fill=BOTH, side=TOP)

        self.button_down = Button(
            self.left_buttons, font=self.MONO_BUTTON, text="↓", command=self.index_down
        )
        self.button_down.pack(expand=YES, fill=BOTH, side=BOTTOM)

        # ********* INDEXES & MONO INFO *********
        self.left_indexes = Frame(self.main_frame)
        self.left_indexes.pack(expand=NO, fill=BOTH, side=LEFT)

        # SETUP
        first_index = (self.INDEX + 2) % self.NUMBER_OF_FONTS
        second_index = (self.INDEX + 1) % self.NUMBER_OF_FONTS
        third_index = (self.INDEX) % self.NUMBER_OF_FONTS
        fourth_index = (self.INDEX - 1) % self.NUMBER_OF_FONTS
        fifth_index = (self.INDEX - 2) % self.NUMBER_OF_FONTS

        first_font = self.FONTS_FILTERED[first_index]
        second_font = self.FONTS_FILTERED[second_index]
        third_font = self.FONTS_FILTERED[third_index]
        fourth_font = self.FONTS_FILTERED[fourth_index]
        fifth_font = self.FONTS_FILTERED[fifth_index]

        first_status = self.FONTS_MONOSPACE_STATUS[first_font]
        second_status = self.FONTS_MONOSPACE_STATUS[second_font]
        third_status = self.FONTS_MONOSPACE_STATUS[third_font]
        fourth_status = self.FONTS_MONOSPACE_STATUS[fourth_font]
        fifth_status = self.FONTS_MONOSPACE_STATUS[fifth_font]

        first_index_text = "{}\n{}".format(
            first_index, self.mono_status_text(first_status)
        )
        second_index_text = "{}\n{}".format(
            second_index, self.mono_status_text(second_status)
        )
        third_index_text = "{}\n{}".format(
            third_index, self.mono_status_text(third_status)
        )
        fourth_index_text = "{}\n{}".format(
            fourth_index, self.mono_status_text(fourth_status)
        )
        fifth_index_text = "{}\n{}".format(
            fifth_index, self.mono_status_text(fifth_status)
        )

        # TEXT DATA NEED TO BE SET AUTOMATICALLY HERE
        self.first_index = Label(
            self.left_indexes,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO,
            text=first_index_text,
            bg=self.bg_color(first_status),
        )
        self.first_index.pack(expand=YES, fill=BOTH, side=TOP)
        self.second_index = Label(
            self.left_indexes,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO,
            text=second_index_text,
            bg=self.bg_color(second_status),
        )
        self.second_index.pack(expand=YES, fill=BOTH, side=TOP)
        self.third_index = Label(
            self.left_indexes,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO,
            text=third_index_text,
            bg=self.bg_color(third_status),
        )
        self.third_index.pack(expand=YES, fill=BOTH, side=TOP)
        self.fourth_index = Label(
            self.left_indexes,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO,
            text=fourth_index_text,
            bg=self.bg_color(fourth_status),
        )
        self.fourth_index.pack(expand=YES, fill=BOTH, side=TOP)
        self.fifth_index = Label(
            self.left_indexes,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO,
            text=fifth_index_text,
            bg=self.bg_color(fifth_status),
        )
        self.fifth_index.pack(expand=YES, fill=BOTH, side=TOP)

        # ********* LEFT FRAME *********
        self.left_frame = Frame(self.main_frame)
        self.left_frame.pack(expand=NO, fill=BOTH, side=LEFT)

        # ********* ENTRIES *********
        center_val = 20
        self.first_sv = StringVar()
        self.first_text = Entry(
            self.left_frame, font=self.MONO_FONT_INFO, textvariable=self.first_sv
        )
        self.first_text.insert(0, self.FONTS_FILTERED[first_index].center(center_val))
        self.first_text.pack(expand=YES, fill=BOTH, side=TOP)

        self.second_sv = StringVar()
        self.second_text = Entry(
            self.left_frame, font=self.MONO_FONT_INFO, textvariable=self.second_sv
        )
        self.second_text.insert(0, self.FONTS_FILTERED[second_index].center(center_val))
        self.second_text.pack(expand=YES, fill=BOTH, side=TOP)

        self.third_sv = StringVar()
        self.third_text = Entry(
            self.left_frame, font=self.MONO_FONT_INFO, textvariable=self.third_sv
        )
        self.third_text.insert(0, self.FONTS_FILTERED[third_index].center(center_val))
        self.third_text.pack(expand=YES, fill=BOTH, side=TOP)

        self.fourth_sv = StringVar()
        self.fourth_text = Entry(
            self.left_frame, font=self.MONO_FONT_INFO, textvariable=self.fourth_sv
        )
        self.fourth_text.insert(0, self.FONTS_FILTERED[fourth_index].center(center_val))
        self.fourth_text.pack(expand=YES, fill=BOTH, side=TOP)

        self.fifth_sv = StringVar()
        self.fifth_text = Entry(
            self.left_frame, font=self.MONO_FONT_INFO, textvariable=self.fifth_sv
        )
        self.fifth_text.insert(0, self.FONTS_FILTERED[fifth_index].center(center_val))
        self.fifth_text.pack(expand=YES, fill=BOTH, side=TOP)

        # ********* RIGHT FRAME *********
        self.right_frame = Frame(self.main_frame)
        self.right_frame.pack(expand=YES, fill=BOTH, side=RIGHT)

        # right top info
        self.top_info = Frame(self.right_frame)
        self.top_info.pack(expand=NO, fill=X, side=TOP)

        # number of fonts
        self.top_info_left = Frame(self.top_info, relief=self.RELIEF_TYPE)
        self.top_info_left.pack(expand=YES, fill=BOTH, side=LEFT)
        self.top_info_left_up = Label(
            self.top_info_left,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO_UPPER,
            text="TOTAL FONTS",
        )
        self.top_info_left_up.pack(expand=YES, fill=X, side=TOP)
        self.top_info_left_down = Label(
            self.top_info_left,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO_UPPER,
            text="{}".format(self.NUMBER_OF_FONTS),
        )
        self.top_info_left_down.pack(expand=YES, fill=X, side=BOTTOM)

        # index entry
        entries_size = 13
        top_center_val = 15

        self.top_info_center_left = Frame(self.top_info, relief=self.RELIEF_TYPE)
        self.top_info_center_left.pack(expand=YES, fill=BOTH, side=LEFT)
        self.top_info_center_left_up = Label(
            self.top_info_center_left,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO_UPPER,
            text="CURRENT FONT",
        )
        self.top_info_center_left_up.pack(expand=YES, fill=X, side=TOP)
        self.top_info_center_left_entry_sv = StringVar()
        self.current_index_entry = Entry(
            self.top_info_center_left,
            width=entries_size,
            font=self.MONO_FONT_INFO_UPPER,
            textvariable=self.top_info_center_left_entry_sv,
        )
        self.current_index_entry.insert(0, str(self.INDEX).center(top_center_val))
        self.current_index_entry.bind("<Return>", self.entry_callback)
        self.current_index_entry.pack(expand=YES, fill=X, side=BOTTOM)

        # filter entry
        self.top_filter_frame = Frame(self.top_info, relief=self.RELIEF_TYPE)
        self.top_filter_frame.pack(expand=YES, fill=BOTH, side=LEFT)

        self.top_filter_label = Label(
            self.top_filter_frame,
            relief=self.RELIEF_TYPE,
            font=self.MONO_FONT_INFO_UPPER,
            text="FILTER TEXT",
        )
        self.top_filter_label.pack(expand=YES, fill=X, side=TOP)
        self.top_filter_sv = StringVar()
        self.filter_entry = Entry(
            self.top_filter_frame,
            width=entries_size,
            font=self.MONO_FONT_INFO_UPPER,
            textvariable=self.top_filter_sv,
        )
        self.filter_entry.insert(0, str("<write-here>").center(top_center_val))
        self.filter_entry.bind("<Return>", self.filter_callback)
        self.filter_entry.pack(expand=YES, fill=X, side=BOTTOM)

        # mono-normal switch button
        button_text = "{}\n{}".format(
            " MODE ", self.FONTS_MODES_DICT[self.FONTS_MODE].upper()
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

        # ********* MAIN LABEL CONTENT *********
        third_font = self.FONTS_FILTERED[self.INDEX]
        start_text = self.perform_center_text(third_font)
        main_font = font.Font(family=third_font, size=50, weight="normal")
        self.main_label = Label(
            self.right_frame, relief=self.RELIEF_TYPE, font=main_font, text=start_text
        )
        self.main_label.pack(expand=YES, fill=BOTH, side=BOTTOM)

        return True


if __name__ == "__main__":
    viewer()
