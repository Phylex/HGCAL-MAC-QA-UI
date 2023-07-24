import tkinter as tk
from tkinter import ttk
import json
from copy import deepcopy
from functools import partial

from ntu_daq_gui import procedure as prc
from ntu_daq_gui import hexacontroller as hx
from ntu_daq_gui import runcontrol as rctrl


class AppState():
    def __init__(self, config_params, config_file_path):
        self.config_file_path = config_file_path
        self.procedures = list(
            map(lambda p: prc.Procedure(
                p.get("name"),
                p.get("executed_file", ""),
                p.get("options", {}),
                p.get("initial_dut_config", "")),
                config_params.get("procedures", [])))
        self.runcontroller = rctrl.RunController()
        # self.remotes = list(map(lambda p:


class GUI(tk.Tk):
    def __init__(self, config_params, config_file_path):
        super().__init__()
        # Initialize the data structures
        self.title("MAC Module Tests")
        self.state = config_params
        self.config_file_path = config_file_path
        self.procedures = list(
            map(lambda p: prc.Procedure(
                p.get("name"),
                p.get("executed_file", ""),
                p.get("options", {}),
                p.get("initial_dut_config", "")),
                config_params.get("procedures", [])))
        self.hexactrls = list(
            map(hx.Hexacontroller.load_from_config, config_params.get("hexacontrollers", [])))

        # Create a notebook (tabs container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Create the two tabs
        self.run_control_tab = rctrl.RunControlUI(deepcopy(self.procedures),
                                                  lambda: deepcopy(
                                                      self.procedures),
                                                  self.notebook)
        self.procedure_config_tab = ttk.Frame(self.notebook)
        self.hexactrl_config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.run_control_tab, text='Run Control')
        self.notebook.add(self.procedure_config_tab,
                          text='Procedure Configuration')
        self.notebook.add(self.hexactrl_config_tab,
                          text='Hexacontroller Configuration')

        # Config Parameters Tab
        self.setup_procedure_widgets(self.procedure_config_tab)

        self.setup_hexactrl_widgets(self.hexactrl_config_tab)

        # Configure grid weights
        self.run_control_tab.columnconfigure(1, weight=1)
        self.run_control_tab.rowconfigure(0, weight=0)
        self.run_control_tab.rowconfigure(1, weight=1)
        close_button = ttk.Button(self,
                                  text="Close",
                                  command=self.close_window)
        close_button.pack()

    def setup_procedure_widgets(self, frame):
        for child in frame.winfo_children():
            child.destroy()
        for i, _ in enumerate(self.procedures):
            self.draw_procedure(frame, i)
        add_button = ttk.Button(frame,
                                text="Add Procedure",
                                command=partial(self.add_procedure, frame))
        add_button.grid()
        save_button = ttk.Button(frame,
                                 text="Save",
                                 command=self.save)
        save_button.grid()

    def setup_hexactrl_widgets(self, frame):
        for child in frame.winfo_children():
            child.destroy()
        for i, _ in enumerate(self.hexactrls):
            hxui = hx.HexactrlConfigUI(
                self.hexactrls[i], frame, relief="groove")
            hxui.grid(padx=5, pady=5)
            rmv_hex_btn = ttk.Button(hxui, text="Remove Hexacontroller",
                                     command=lambda: self.remove_hexacontroller(i, frame))
            rmv_hex_btn.grid()
        add_button = ttk.Button(frame, text="Add Hexacontroller Config",
                                command=lambda: self.add_hexacontroller(frame))
        add_button.grid()
        save_button = ttk.Button(frame,
                                 text="Save",
                                 command=self.save)
        save_button.grid()

    def draw_procedure(self, frame, i):
        proc_frame = ttk.Frame(frame, borderwidth=2, relief="groove")
        proc_frame.grid(padx=5, pady=5)
        prc.ProcedureConfigUI(proc_frame, self.procedures[i])
        ttk.Button(proc_frame, text="Remove Procedure",
                   command=partial(self.remove_procedure, i, proc_frame)).grid(column=2, pady=3, padx=3)

    def add_procedure(self, frame):
        pcui = prc.ProcedureCreationUI(frame)
        self.procedures.append(pcui.result)
        self.setup_procedure_widgets(frame)

    def remove_procedure(self, proc_idx, parent):
        self.procedures.pop(proc_idx)
        self.setup_procedure_widgets(parent)

    def remove_hexacontroller(self, idx, parent):
        self.hexactrls.pop(idx)
        self.setup_hexactrl_widgets(parent)

    def add_hexacontroller(self, frame):
        hxui = hx.HexacontrollerCreationUI(frame)
        self.hexactrls.append(hxui.result)
        self.setup_hexactrl_widgets(frame)

    def save(self):
        proc_config = [p.serialize() for p in self.procedures]
        config = {'procedures': proc_config}
        with open(self.config_file_path, 'w') as f:
            json.dump(config, f)

    def close_window(self):
        self.destroy()


if __name__ == '__main__':
    with open('./config_template.json', 'r') as cf:
        config = json.load(cf)
    gui = GUI(config, './config_template.json')
    gui.mainloop()
