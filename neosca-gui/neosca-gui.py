#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import glob
import logging
import os
import os.path as os_path
import queue
import subprocess
import sys
import threading
from tkinter import *
from tkinter import filedialog, font, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Dict, Iterable, List, Set

from neosca.structure_counter import StructureCounter
from tksheet import Sheet


class SCAGUI:
    def __init__(self, *, with_restart_button: bool = False) -> None:
        self.desktop = os_path.normpath(os_path.expanduser("~/Desktop"))
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

        self.sca_frame = ttk.Frame(self.notebook, borderwidth=1, relief="solid")
        self.sca_frame.grid(column=0, row=0, sticky="nswe")
        self.notebook.add(self.sca_frame, text="SCA")

        self.lcaframe = ttk.Frame(self.notebook)
        self.lcaframe.grid(column=0, row=0, sticky="nswe")
        self.notebook.add(self.lcaframe, text="LCA")

        self.notebook.grid_rowconfigure(0, weight=1)
        self.notebook.grid_columnconfigure(0, weight=1)

        ttk.Style().theme_use("alt")
        self.initialize_bottom_pane()

        self.generate_table_buttons = []
        self.export_table_buttons = []
        self.initialize_scaframe()

        self.lcaframe.grid_rowconfigure(0, weight=1)
        self.lcaframe.grid_columnconfigure(0, weight=1)

        rowno = 0

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
        self.input_files: Set[str] = set()

        self.root.bind("<Control-r>", self.restart)
        self.root.bind("<Control-q>", lambda event: self.root.quit())
        self.root.mainloop()

    def disable_generate_table_buttons(self):
        for bt in self.generate_table_buttons:
            bt.config(state="disable")

    def enable_generate_table_buttons(self):
        for bt in self.generate_table_buttons:
            bt.config(state="normal")

    def initialize_scaframe(self):
        # preview frame
        self.sca_preview_frame = ttk.Frame(self.sca_frame)
        self.sca_preview_frame.grid(column=0, row=0, sticky="nswe")
        self.sca_button_frame = ttk.Frame(self.sca_frame)
        self.sca_button_frame.grid(column=0, row=1, sticky="nswe")
        self.sca_frame.grid_rowconfigure(0, weight=1)
        self.sca_frame.grid_columnconfigure(0, weight=1)

        rowno = 0
        colno = 0
        self.sca_preview_sheet = Sheet(
            self.sca_preview_frame,
            header=["Path"] + StructureCounter.DEFAULT_MEASURES,
            data=[""],
            align="e",  # right-align numbers
            font=self.tksheet_font,
            header_font=self.tksheet_font,
            index_font=self.tksheet_font,
        )
        self.sca_preview_sheet.enable_bindings(
            "single_select",  # single left click to select a cell
            "drag_select",  # drag mouse to select an area of cells
            "select_all",  # click upper left corner button to select all
            "ctrl_select",
            "column_select",  # click a column name
            "row_select",  # click a row name
            "column_width_resize",  # hover cursor in between two column names
            "arrowkeys",  # use arrowkeys to navigate across cells
            "row_height_resize",  # hover cursor in between two row names
            "right_click_popup_menu",
            "rc_select",
        )
        self.sca_preview_sheet.edit_bindings(enable=False)
        self.sca_preview_sheet.set_all_cell_sizes_to_text(redraw=True)
        self.sca_preview_sheet.align_columns(columns=[0], align="w")
        self.sca_preview_sheet.grid(column=colno, row=rowno, sticky="nswe")
        self.sca_preview_frame.grid_rowconfigure(0, weight=1)
        self.sca_preview_frame.grid_columnconfigure(0, weight=1)

        colno = 0
        rowno = 0
        self.sca_generate_table_button = ttk.Button(
            self.sca_button_frame,
            text="Generate table",
            # Here use lambda to avoid RuntimeError("threads can only be started once")
            # Daemon thread keeps running even after the main program exists,
            #  normal thread prevents the main program from existing
            command=lambda: threading.Thread(
                target=self.sca_generate_table, daemon=True
            ).start(),
            state="disable",
        )
        self.sca_generate_table_button.grid(column=colno, row=rowno, sticky="sw")
        self.generate_table_buttons.append(self.sca_generate_table_button)

        colno += 1
        self.sca_export_table_button = ttk.Button(
            self.sca_button_frame,
            text="Export all cells...",
            command=self.sca_export_table,
            state="disable",
        )
        self.sca_export_table_button.grid(column=colno, row=rowno, sticky="sw")
        self.export_table_buttons.append(self.sca_export_table_button)

        # setting frame
        self.sca_setting_frame = ttk.Frame(self.sca_frame)
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
            header=["Path"],
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
            "ctrl_select",
            "column_select",  # click a column name
            "row_select",  # click a row name
            "column_width_resize",  # hover cursor in between two column names
            "arrowkeys",  # use arrowkeys to navigate across cells
            "row_height_resize",  # hover cursor in between two row names
            "right_click_popup_menu",
            "rc_select",
        )
        self.file_sheet.popup_menu_add_command("Remove File", self.remove_from_filesheet)
        self.file_sheet.grid(column=0, row=0, sticky="nswe")
        self.bottom_pane.grid_rowconfigure(0, weight=1)
        self.bottom_pane.grid_columnconfigure(0, weight=1)

    def add_to_filesheet(self):
        self.file_sheet.set_sheet_data([(file_path,) for file_path in self.input_files])
        self.file_sheet.set_all_cell_sizes_to_text(redraw=True)

    def remove_from_filesheet(self):
        rownos = self.file_sheet.get_selected_rows(return_tuple=False)
        if not rownos:
            rownos = set(cell[0] for cell in self.file_sheet.get_selected_cells())
        rows_to_remove = len(rownos)
        rows_existing = self.file_sheet.get_total_rows(include_index=False)
        if rows_to_remove == rows_existing:
            self.file_sheet.set_sheet_data([""])
            self.input_files.clear()
            self.disable_generate_table_buttons()
        else:
            self.file_sheet.delete_rows(rownos)  # type:ignore
            filepath_indice = 0
            self.input_files = set(self.file_sheet.get_column_data(filepath_indice))
        self.file_sheet.set_all_cell_sizes_to_text(redraw=True)

    def open_file(self):
        file_paths = filedialog.askopenfilenames(
            filetypes=(
                ("txt files", "*.txt"),
                ("docx files", "*.docx"),
            )
        )
        if file_paths:
            self.input_files.update(file_paths)
            self.add_to_filesheet()
            self.enable_generate_table_buttons()

    def open_folder(self):
        folder_path = filedialog.askdirectory(mustexist=True)
        if folder_path:
            for ext in ("*.txt", "*.docx"):
                self.input_files.update(glob.glob(f"{folder_path}{os_path.sep}{ext}"))
            self.add_to_filesheet()
            self.enable_generate_table_buttons()

    def put_window_on_center(self, window, width, height):
        # Get the screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate x and y coordinates to center the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the window dimensions and position
        window.geometry(f"{width}x{height}+{x}+{y}")

    def start_logging_to_frame(self, frame):
        self.log_console = LogUI(frame)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        handler = QueueHandler(self.log_console.log_queue)
        self.logger.addHandler(handler)

    def sca_export_table(self) -> None:
        # https://github.com/ragardner/tksheet/wiki/Version-6#example-saving-tksheet-as-a-csv-file
        file_path = filedialog.asksaveasfilename(
            title="Export Table",
            filetypes=[("Excel Workbook", ".xlsx"), ("CSV File", ".csv"), ("TSV File", ".tsv")],
            defaultextension=".xlsx",
            confirmoverwrite=True,
            initialdir=self.desktop,
            initialfile="neosca-gui_sca_result.xlsx",
        )
        if not file_path:
            return
        ext = os_path.splitext(file_path)[-1]
        data = self.sca_preview_sheet.get_sheet_data(get_header=True, get_index=False)
        if data is None:
            return
        try:
            if ext == ".xlsx":
                import openpyxl

                workbook = openpyxl.Workbook()
                worksheet = workbook.active

                for row in data:
                    worksheet.append(row)
                workbook.save(file_path)
            elif ext in (".csv", ".tsv"):
                import csv

                dialect = csv.excel if ext == ".csv" else csv.excel_tab
                with open(os_path.normpath(file_path), "w", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh, dialect=dialect, lineterminator="\n")
                    writer.writerows(data)  # type:ignore
            messagebox.showinfo(message=f"The table has been successfully exported to {file_path}.")
        except Exception as e:
            messagebox.showerror(message=f"{e}")
            return

    def sca_generate_table(self) -> None:
        from neosca.neosca import NeoSCA

        self.sca_generate_table_button.config(state="disable")
        self.log_window = Toplevel(self.root)
        self.log_window.title("NeoSCA Logs")
        self.put_window_on_center(self.log_window, width=400, height=300)
        ttk.Label(
            self.log_window,
            text="NeoSCA is running. It may take a few minutes to finish the job. Please wait.",
        ).grid(column=0, row=0)
        log_frame = ttk.Frame(self.log_window)
        log_frame.grid(column=0, row=1)
        self.log_window.grid_rowconfigure(0, weight=1)
        self.log_window.grid_columnconfigure(0, weight=1)
        self.start_logging_to_frame(log_frame)

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
            "is_auto_save": False,
            "config": None,
        }

        attrname = "sca_analyzer"
        try:
            sca_analyzer = getattr(self, attrname)
        except AttributeError:
            sca_analyzer = NeoSCA(**sca_kwargs)
            setattr(self, attrname, sca_analyzer)
        else:
            sca_analyzer.update_options(sca_kwargs)

        sca_analyzer.run_on_ifiles(self.input_files)
        self.log_window.destroy()
        sname_value_maps: List[Dict[str, str]] = [
            counter.get_all_values() for counter in sca_analyzer.counters
        ]
        self.sca_preview_sheet.set_sheet_data([list(map_.values()) for map_ in sname_value_maps])
        self.sca_preview_sheet.set_all_cell_sizes_to_text(redraw=True)
        self.sca_export_table_button.config(state="normal")
        # don't have to enbale generate buttons here as they should only be
        # enabled when more input files are added

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
        self.scrolled_text = ScrolledText(frame, state="disabled")
        self.scrolled_text.grid(column=0, row=0, sticky="nswe")
        self.scrolled_text.configure(font="TkFixedFont")
        self.scrolled_text.tag_config("INFO", foreground="black")
        self.scrolled_text.tag_config("DEBUG", foreground="gray")
        self.scrolled_text.tag_config("WARNING", foreground="orange")
        self.scrolled_text.tag_config("ERROR", foreground="red")
        self.scrolled_text.tag_config("CRITICAL", foreground="red", underline=True)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter("%(message)s")
        self.queue_handler.setFormatter(formatter)

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
