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
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Iterable

from neosca.scaio import SCAIO


class SCAGUI:
    def __init__(self, *, with_restart_button: bool = False) -> None:
        root = Tk()
        root.title("NeoSCA")
        mainframe = ttk.Frame(root, padding=3, borderwidth=5, relief="ridge")
        mainframe.grid(column=0, row=0)

        ttk.Style().theme_use("alt")

        rowno = 0
        rowno += 1
        reserve_parsed_trees = BooleanVar(value=True)
        reserve_parsed_trees_checkbox = ttk.Checkbutton(
            mainframe,
            text="Reserve parsed trees",
            variable=reserve_parsed_trees,
            onvalue=True,
            offvalue=False,
        )
        reserve_parsed_trees_checkbox.grid(column=2, row=rowno, columnspan=2, sticky="sw")

        reserve_matched_subtrees = BooleanVar(value=True)
        reserve_parsed_trees_checkbox = ttk.Checkbutton(
            mainframe,
            text="Reserve matched subtrees",
            variable=reserve_matched_subtrees,
            onvalue=True,
            offvalue=False,
        )
        reserve_parsed_trees_checkbox.grid(column=4, row=rowno, columnspan=2, sticky="sw")

        rowno += 1
        choose_file_button = ttk.Button(
            mainframe,
            text="Choose File",
            command=lambda: self.append_input_file(
                filedialog.askopenfilenames(
                    filetypes=(
                        ("txt files", "*.txt"),
                        ("docx files", "*.docx"),
                        ("all files", "*"),
                    )
                )
            ),
        )
        choose_file_button.grid(column=2, row=rowno, sticky="w")

        choose_folder_button = ttk.Button(
            mainframe,
            text="Choose Folder",
            command=lambda: self.append_input_folder(filedialog.askdirectory(mustexist=True)),
        )
        choose_folder_button.grid(column=3, row=rowno, sticky="w")

        # rowno += 1
        # log_console = ScrolledText(mainframe, state="disabled", width=80, height=24, wrap="char")
        # log_console.grid(column=1, row=rowno, columnspan=5, sticky="nswe")

        rowno += 1
        # logging_pane = ttk.Panedwindow(mainframe, orient='vertical')
        # logging_pane.grid(column=0, row=rowno, sticky="nswe")
        logging_frame = ttk.Frame(mainframe)
        logging_frame.grid(column=1, row=rowno, columnspan=10)
        log_console = LogUI(logging_frame)

        rowno += 1
        ttk.Button(mainframe, text="Run SCA", command=self.run_sca).grid(column=3, row=rowno)
        if with_restart_button:
            # for tuning and debugging
            ttk.Button(mainframe, text="Restart", command=self.restart).grid(
                column=4, row=rowno, sticky="sw"
            )
            ttk.Button(mainframe, text="Quit", command=lambda: root.destroy()).grid(
                column=5, row=rowno, sticky="sw"
            )

        for child in mainframe.winfo_children():
            child.grid_configure(padx=1, pady=1)

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
        self.root = root
        self.mainframe = mainframe
        self.log_console = log_console
        self.is_reserve_parsed_trees = reserve_parsed_trees
        self.is_reserve_matched_subtrees = reserve_matched_subtrees
        self.input_files = []
        self.scaio = SCAIO()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        handler = QueueHandler(self.log_console.log_queue)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.root.mainloop()

    def append_input_file(self, paths: Iterable) -> None:
        if paths:
            verified_input_files = self.scaio.get_verified_ifile_list(list(paths))
            self.input_files.extend(verified_input_files)
            logging.debug("[SCAGUI] Chosen files:\n {}".format("\n".join(verified_input_files)))

    def append_input_folder(self, path: str) -> None:
        if path:
            verified_input_files = self.scaio.get_verified_ifile_list([path])
            self.input_files.extend(verified_input_files)
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
        thread = threading.Thread(target=sca_analyzer.run_on_ifiles, args=(verified_input_files,))
        thread.start()
        self.show_message_afterwards(thread, "Done. The result has been saved to your Desktop.")
        # sca_analyzer.run_on_ifiles(verified_input_files)

    def show_message_afterwards(self, thread, msg:str):
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
    """Class to send logging records to a queue. It can be used from different threads """
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
