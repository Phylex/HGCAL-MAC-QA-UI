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
        # self.runcontroller = rctrl.RunController()
        self.hexactrls = list(
                map(hx.Hexacontroller.load_from_config,
                    config_params.get("hexacontrollers", [])))

        if len(self.procedures) > 0:
            self.running_procedure_config = deepcopy(self.procedures[0])
        else:
            self.running_procedure_config = None
        if len(self.hexactrls) > 0:
            self.running_hexactrl_config = deepcopy(self.hexactrls[0])
        else:
            self.running_procedure_config = None

    def set_run_hexactrl(self, hexactrl: hx.Hexacontroller):
        self.running_hexactrl_config = deepcopy(hexactrl)

    def set_run_procedure(self, procedure: prc.Procedure):
        self.running_procedure_config = deepcopy(procedure)


class GUI(tk.Tk):
    def __init__(self, config_params, config_file_path):
        super().__init__()
        # Initialize the data structures
        self.title("MAC Module Tests")
        self.app_state = AppState(config_params, config_file_path)
        self.config_file_path = config_file_path

        # Create a notebook (tabs container)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(sticky="nsew")

        # Create the two tabs
        self.run_control_tab = rctrl.RunControlUI(self.notebook, self.app_state)
        self.procedure_config_tab = ttk.Frame(self.notebook)
        self.hexactrl_config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.run_control_tab, text='Run Control')
        self.notebook.add(self.procedure_config_tab,
                          text='Procedure Configuration')
        self.notebook.add(self.hexactrl_config_tab,
                          text='Hexacontroller Configuration')

        # Procedure configuration tab setup
        self.setup_procedure_widgets(self.procedure_config_tab)

        # Hexacontroller configuration setup
        self.setup_hexactrl_widgets(self.hexactrl_config_tab)

        # Configure grid weights
        self.run_control_tab.columnconfigure(1, weight=1)
        self.run_control_tab.rowconfigure(0, weight=0)
        self.run_control_tab.rowconfigure(1, weight=1)
        close_button = ttk.Button(self,
                                  text="Close",
                                  command=self.close_window)
        close_button.grid()

    def setup_run_control_widgets(self, frame):
        ...

    def setup_procedure_widgets(self, frame):
        for child in frame.winfo_children():
            child.destroy()
        frame.grid_forget()
        for i, _ in enumerate(self.app_state.procedures):
            self.draw_procedure(frame, i)
        add_button = ttk.Button(frame,
                                text="Add Procedure",
                                command=lambda: self.add_procedure(frame))
        add_button.grid()
        save_button = ttk.Button(frame,
                                 text="Save",
                                 command=self.save)
        save_button.grid()

    def setup_hexactrl_widgets(self, frame):
        for child in frame.winfo_children():
            child.destroy()
        frame.grid_forget()
        for i, hexctrl in enumerate(self.app_state.hexactrls):
            hxui = hx.HexactrlConfigUI(
                self.app_state.hexactrls[i], frame, relief="groove")
            hxui.grid(padx=5, pady=5)
            rmv_hex_btn = ttk.Button(hxui, text="Remove Hexacontroller",
                                     command=lambda: self.remove_hexacontroller(hexctrl.name, frame))
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
        prc.ProcedureConfigUI(proc_frame, self.app_state.procedures[i])
        ttk.Button(proc_frame, text="Remove Procedure",
                   command=lambda: self.remove_procedure(self.app_state.procedures[i].name, proc_frame)
                   ).grid(column=2, pady=3, padx=3)

    def add_procedure(self, frame):
        pcui = prc.ProcedureCreationUI(frame)
        self.app_state.procedures.append(pcui.result)
        self.setup_procedure_widgets(frame)

    def remove_procedure(self, name, parent):
        print(name)
        proc_with_name = list(filter(lambda p: p[1].name == name, enumerate(self.app_state.procedures)))
        print(proc_with_name)
        if len(proc_with_name) > 0:
            self.app_state.procedures.pop(proc_with_name[0][0])
        self.setup_procedure_widgets(parent)

    def remove_hexacontroller(self, name, parent):
        hectrl_with_name = list(filter(lambda h: h[1].name == name, enumerate(self.app_state.hexactrls)))
        if len(hectrl_with_name) > 0:
            self.app_state.hexactrls.pop(hectrl_with_name[0][0])
        self.setup_hexactrl_widgets(parent)

    def add_hexacontroller(self, frame):
        hxui = hx.HexacontrollerCreationUI(frame)
        self.app_state.hexactrls.append(hxui.result)
        self.setup_hexactrl_widgets(frame)

    def save(self):
        self.run_control_tab.refresh_available_procs_and_hexacontrollers()
        proc_config = [p.serialize() for p in self.app_state.procedures]
        hexa_config = [h.serialize() for h in self.app_state.hexactrls]
        config = {'procedures': proc_config, 'hexacontrollers': hexa_config}
        with open(self.config_file_path, 'w') as f:
            json.dump(config, f)

    def close_window(self):
        self.destroy()


if __name__ == '__main__':
    with open('./config_template.json', 'r') as cf:
        config = json.load(cf)
    gui = GUI(config, './config_template.json')
    gui.mainloop()
