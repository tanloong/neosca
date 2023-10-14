#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import logging
import os
import os.path as os_path
import queue
import subprocess
import sys
import threading
from tkinter import *
from tkinter import ttk, filedialog, messagebox, font
from tkinter.scrolledtext import ScrolledText
from typing import Iterable
from tksheet import Sheet

from neosca.scaio import SCAIO
from neosca.structure_counter import StructureCounter


class SCAGUI:
    def __init__(self, *, with_restart_button: bool = False) -> None:
        self.root = Tk()
        self.root.title("NeoSCA")
        self.root.option_add("*tearOff", FALSE)  # disable tear-off menus
        self.default_font = font.nametofont("TkTextFont").actual()
        # https://github.com/ragardner/tksheet/wiki/Version-6#text-font-and-alignment
        self.tksheet_font = tuple(
            self.default_font[attr] for attr in ("family", "size", "weight")
        )

        # menubar
        menubar = Menu(self.root)
        self.root["menu"] = menubar
        file_menu = Menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File", command=self.open_file)
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        if with_restart_button:
            file_menu.add_command(label="Restart", command=self.restart)

        self.mainframe = ttk.Frame(self.root, padding=3, borderwidth=5, relief="ridge")
        self.mainframe.grid(column=0, row=0)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        p = ttk.Panedwindow(self.mainframe, orient="vertical")
        p.grid(column=0, row=0, sticky="nswe")
        self.mainframe.grid_rowconfigure(0, weight=1)
        self.mainframe.grid_columnconfigure(0, weight=1)

        self.upper_pane = ttk.Frame(p, borderwidth=1, relief="solid", width=300, height=300)
        self.upper_pane.grid(column=0, row=0, sticky="nswe")
        self.upper_pane.grid_rowconfigure(0, weight=1)
        self.upper_pane.grid_columnconfigure(0, weight=1)
        p.add(self.upper_pane, weight=3)

        self.bottom_pane = ttk.Frame(p, borderwidth=1, relief="solid", width=300, height=300)
        self.bottom_pane.grid(column=0, row=1, sticky="nswe")
        self.bottom_pane.grid_rowconfigure(0, weight=1)
        self.bottom_pane.grid_columnconfigure(0, weight=1)
        p.add(self.bottom_pane, weight=1)

        p.grid_rowconfigure(0, weight=1)
        p.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.upper_pane)
        self.notebook.grid(column=0, row=0, sticky="nswe")

        self.scaframe = ttk.Frame(self.notebook, borderwidth=1, relief="solid")
        self.scaframe.grid(column=0, row=0, sticky="nswe")
        self.notebook.add(self.scaframe, text="SCA")

        self.lcaframe = ttk.Frame(self.notebook)
        self.lcaframe.grid(column=0, row=0, sticky="nswe")
        self.notebook.add(self.lcaframe, text="LCA")

        self.notebook.grid_rowconfigure(0, weight=1)
        self.notebook.grid_columnconfigure(0, weight=1)

        ttk.Style().theme_use("alt")
        self.initialize_bottom_pane()

        self.initialize_scaframe()

        self.lcaframe.grid_rowconfigure(0, weight=1)
        self.lcaframe.grid_columnconfigure(0, weight=1)

        rowno = 0

        # rowno += 1
        # log_console = ScrolledText(scaframe, state="disabled", width=80, height=24, wrap="char")
        # log_console.grid(column=1, row=rowno, columnspan=5, sticky="nswe")

        # rowno += 1
        # self.logging_frame = ttk.Frame(self.scaframe)
        # self.logging_frame.grid(column=1, row=rowno, columnspan=10)
        # self.log_console = LogUI(self.logging_frame)

        # for child in self.scaframe.winfo_children():
        #     child.grid_configure(padx=1, pady=1)

        neosca_gui_home = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
        libs_dir = os_path.join(neosca_gui_home, "libs")
        self.java_home = os_path.join(libs_dir, "jdk8u372")
        self.stanford_parser_home = os_path.join(libs_dir, "stanford-parser-full-2020-11-17")
        self.stanford_tregex_home = os_path.join(libs_dir, "stanford-tregex-2020-11-17")
        os.environ["JAVA_HOME"] = self.java_home
        os.environ["STANFORD_PARSER_HOME"] = self.stanford_parser_home
        os.environ["STANFORD_TREGEX_HOME"] = self.stanford_tregex_home
        self.env = os.environ.copy()

        self.desktop = os_path.normpath(os_path.expanduser("~/Desktop"))
        self.input_files = []
        self.scaio = SCAIO()
        # self.logger = logging.getLogger()
        # self.logger.setLevel(logging.DEBUG)
        # handler = QueueHandler(self.log_console.log_queue)
        # formatter = logging.Formatter("%(levelname)s: %(message)s")
        # handler.setFormatter(formatter)
        # self.logger.addHandler(handler)

        self.root.bind("<Control-r>", self.restart)
        self.root.mainloop()

    def initialize_scaframe(self):
        # preview frame
        self.sca_preview_frame = ttk.Frame(self.scaframe)
        self.sca_preview_frame.grid(column=0, row=0, sticky="nswe")
        self.scaframe.grid_rowconfigure(0, weight=1)
        self.scaframe.grid_columnconfigure(0, weight=1)

        rowno = 0
        colno = 0
        self.preview_sheet = Sheet(
            self.sca_preview_frame,
            header=StructureCounter.DEFAULT_MEASURES,
            data=[""],
            font=self.tksheet_font,
            header_font=self.tksheet_font,
            index_font=self.tksheet_font,
        )
        self.preview_sheet.edit_bindings(enable=False)
        self.preview_sheet.set_all_cell_sizes_to_text(redraw=True)
        self.preview_sheet.grid(column=colno, row=rowno, sticky="nswe")
        self.sca_preview_frame.grid_rowconfigure(0, weight=1)
        self.sca_preview_frame.grid_columnconfigure(0, weight=1)

        rowno += 1
        ttk.Button(self.sca_preview_frame, text="Generate Table", command=self.run_sca).grid(
            column=colno, row=rowno, sticky="sw"
        )

        # setting frame
        self.sca_setting_frame = ttk.Frame(self.scaframe)
        self.sca_setting_frame.grid(column=1, row=0, sticky="nswe")

        rowno = 0
        colno = 0
        self.is_reserve_parsed_trees = BooleanVar(value=True)
        self.reserve_parsed_trees_checkbox = ttk.Checkbutton(
            self.sca_setting_frame,
            text="Reserve parsed trees",
            variable=self.is_reserve_parsed_trees,
            onvalue=True,
            offvalue=False,
        )
        self.reserve_parsed_trees_checkbox.grid(column=colno, row=rowno, sticky="nswe")

        rowno += 1
        self.is_reserve_matched_subtrees = BooleanVar(value=True)
        self.reserve_parsed_trees_checkbox = ttk.Checkbutton(
            self.sca_setting_frame,
            text="Reserve matched subtrees",
            variable=self.is_reserve_matched_subtrees,
            onvalue=True,
            offvalue=False,
        )
        self.reserve_parsed_trees_checkbox.grid(column=colno, row=rowno, sticky="nswe")

    def initialize_bottom_pane(self):
        self.file_sheet = Sheet(
            self.bottom_pane,
            header=["Filename"],
            data=[""],
            font=self.tksheet_font,
            header_font=self.tksheet_font,
            index_font=self.tksheet_font,
        )

        self.file_sheet.set_all_cell_sizes_to_text(redraw=True)
        self.file_sheet.enable_bindings(
            "single_select",  # single left click to select a cell
            "drag_select",  # drag mouse to select an area of cells
            "select_all",  # click upper left corner button to select all
            # "column_select",  # click a column name
            "row_select",  # click a row name
            "column_width_resize",  # hover cursor in between two column names
            "arrowkeys",  # use arrowkeys to navigate across cells
            "row_height_resize",  # hover cursor in between two row names
            "right_click_popup_menu",
            "rc_select",
            # "rc_delete_row",  # show "Delete rows" option in the pop-up menu when right clicking a row name
        )
        self.file_sheet.popup_menu_add_command("Remove File", self.remove_from_filesheet)
        self.file_sheet.grid(column=0, row=0, sticky="nswe")
        self.bottom_pane.grid_rowconfigure(0, weight=1)
        self.bottom_pane.grid_columnconfigure(0, weight=1)

        # Bind right-click event
        # self.file_listbox.bind("<Button-3>", self.show_context_menu)

        # Context menu for right-click
        # self.context_menu = Menu(self.file_listbox)
        # self.context_menu.add_command(label="Delete", command=self.delete_file)

    # def show_context_menu(self, event):
    #     self.context_menu.post(event.x_root, event.y_root)

    # def delete_file(self):
    #     selected_index = self.file_listbox.curselection()
    #     if selected_index:
    #         index = selected_index[0]
    #         del self.input_files[index]
    #         self.update_file_listbox()

    def add_to_filesheet(self):
        self.file_sheet.set_sheet_data([(file_path,) for file_path in self.input_files])
        self.file_sheet.set_all_cell_sizes_to_text(redraw=True)

    def remove_from_filesheet(self, event=None):
        rownos = self.file_sheet.get_selected_rows(return_tuple=False)
        if not rownos:
            rownos = set(cell[0] for cell in self.file_sheet.get_selected_cells())
        rows_to_remove = len(rownos)
        rows_existing = self.file_sheet.get_total_rows(include_index=False)
        if rows_to_remove == rows_existing:
            self.file_sheet.set_sheet_data([""])
            self.input_files.clear()
        else:
            self.file_sheet.delete_rows(rownos)  # type:ignore
            filepath_indice = 0
            self.input_files = self.file_sheet.get_column_data(filepath_indice)

    def open_file(self):
        file_paths = filedialog.askopenfilenames(
            filetypes=(
                ("txt files", "*.txt"),
                ("docx files", "*.docx"),
                ("all files", "*"),
            )
        )
        if file_paths:
            verified_input_files = self.scaio.get_verified_ifile_list(list(file_paths))
            self.input_files.extend(verified_input_files)
            self.add_to_filesheet()

            logging.debug("[SCAGUI] Chosen files:\n {}".format("\n".join(verified_input_files)))

    def open_folder(self):
        folder_path = filedialog.askdirectory(mustexist=True)
        if folder_path:
            verified_input_files = self.scaio.get_verified_ifile_list([folder_path])
            self.input_files.extend(verified_input_files)
            self.add_to_filesheet()

            logging.debug("[SCAGUI] Chosen files:\n {}".format("\n".join(verified_input_files)))

    def run_sca(self) -> None:
        from neosca.neosca import NeoSCA

        output_dir = os_path.join(self.desktop, "neosca-results")
        os.makedirs(output_dir, exist_ok=True)
        ofile_freq = os_path.join(output_dir, "sca-result.csv")
        odir_matched = os_path.splitext(ofile_freq)[0] + "_matches"

        sca_kwargs = {
            "ofile_freq": ofile_freq,
            "stanford_parser_home": self.stanford_parser_home,
            "stanford_tregex_home": self.stanford_tregex_home,
            "odir_matched": odir_matched,
            "newline_break": "never",
            "max_length": None,
            "selected_measures": None,
            "is_reserve_parsed": self.is_reserve_parsed_trees,
            "is_reserve_matched": self.is_reserve_matched_subtrees,
            "is_skip_querying": False,
            "is_skip_parsing": False,
            "is_pretokenized": False,
            "config": None,
        }
        verified_input_files = self.scaio.get_verified_ifile_list(self.input_files)

        messagebox.showinfo(
            message="NeoSCA is running. It may take a few minutes to finit the job. Please wait."
        )
        sca_analyzer = NeoSCA(**sca_kwargs)
        thread = threading.Thread(
            target=sca_analyzer.run_on_ifiles, args=(verified_input_files,)
        )
        thread.start()
        self.show_message_afterwards(thread, "Done. The result has been saved to your Desktop.")
        # sca_analyzer.run_on_ifiles(verified_input_files)

    def show_message_afterwards(self, thread, msg: str):
        if thread.is_alive():
            # Thread is still running, keep checking every second (1000 milliseconds)
            self.root.after(1000, self.show_message_afterwards, thread, msg)
        else:
            # Thread has finished
            messagebox.showinfo(message=msg)

    # def write_to_log(self, msg: str) -> None:
    #     self.log_console["state"] = "normal"
    #     # if self.log_console.index("end-1c") != "1.0":
    #     #     self.log_console.insert("end", "\n")
    #     self.log_console.insert("end", msg)
    #     self.log_console["state"] = "disabled"

    def restart(self, *args) -> None:
        self.root.destroy()

        args = [sys.executable] + sys.argv
        # If close_fds is true, all file descriptors except 0, 1 and 2 will be
        #  closed before the child process is executed. Otherwise when close_fds
        #  is false, file descriptors obey their inheritable flag as described
        #  in Inheritance of File Descriptors
        subprocess.call(args, env=self.env, close_fds=False)


class QueueHandler(logging.Handler):
    """Class to send logging records to a queue. It can be used from different threads"""

    # https://beenje.github.io/blog/posts/logging-to-a-tkinter-scrolledtext-widget/

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class LogUI:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    # https://beenje.github.io/blog/posts/logging-to-a-tkinter-scrolledtext-widget/

    def __init__(self, frame):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state="disabled", width=120, height=24)
        self.scrolled_text.grid(row=0, column=0, sticky="nswe")
        self.scrolled_text.configure(font="TkFixedFont")
        self.scrolled_text.tag_config("INFO", foreground="black")
        self.scrolled_text.tag_config("DEBUG", foreground="gray")
        self.scrolled_text.tag_config("WARNING", foreground="orange")
        self.scrolled_text.tag_config("ERROR", foreground="red")
        self.scrolled_text.tag_config("CRITICAL", foreground="red", underline=True)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        self.queue_handler.setFormatter(logging.Formatter("%(message)s"))

        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state="normal")
        self.scrolled_text.insert(END, msg + "\n", record.levelname)
        self.scrolled_text.configure(state="disabled")
        # Autoscroll to the bottom
        self.scrolled_text.yview(END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display

        while not self.log_queue.empty():
            record = self.log_queue.get(block=False)
            self.display(record)
        self.frame.after(100, self.poll_log_queue)


gui = SCAGUI(with_restart_button=True)
