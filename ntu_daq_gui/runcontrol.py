import tkinter as tk
from typing import Tuple
from ntu_daq_gui import procedure as prc
from ntu_daq_gui import hexacontroller as hx
from ntu_daq_gui.gui import AppState
from tkinter import ttk
from copy import deepcopy


class RunControlUI(ttk.Frame):
    """
    The UI for the Tab that runs the Execution of the commands after
    everything has been configured makes sure that the executing command
    is brought to completion
    """

    def __init__(self, parent: ttk.Widget, state: AppState, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_state = state
        self.procedure_var = tk.StringVar()
        self.hexa_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        """
        Do the layouting of the frame here
        """
        self.refresh_available_procs_and_hexacontrollers()

        # Create left and right frames in the run control tab
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky='nsew')
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky='nsew')

        # Create widgets in the left frame
        # first off we want to select the procedure we want to run
        procedure_label = ttk.Label(left_frame, text="Selected Procedure")
        procedure_label.grid(row=0, columnspan=1)
        self.procedure_selection = tk.Listbox(
            left_frame, height=5, listvariable=self.procedure_var,
            selectbackground="lightblue",
            exportselection=False)
        self.procedure_selection.grid(row=1, columnspan=1)
        self.procedure_selection.bind(
                "<<ListboxSelect>>",
                lambda s: self.update_procedure_selection(
                    self.procedure_selection.curselection()))
        if len(self.app_state.procedures) > 0:
            self.procedure_selection.selection_set(0)


        # Now we select the hexacontroller to run it on
        hexa_label = ttk.Label(left_frame, text="Selected Hexacontroller")
        hexa_label.grid(row=2, columnspan=1)
        self.hexa_selection = tk.Listbox(
            left_frame, height=5, listvariable=self.hexa_var,
            selectbackground="lightblue",
            exportselection=False)
        self.hexa_selection.grid(row=3, columnspan=1)
        self.hexa_selection.bind(
                "<<ListboxSelect>>",
                lambda s: self.update_hexacontroller_selection(
                    self.hexa_selection.curselection()))
        if len(self.app_state.hexactrls) > 0:
            self.hexa_selection.selection_set(0)

        # This section shows if the program is connected
        # to the remote host
        self.conn_frame = ttk.Frame(self)
        self.conn_frame.grid(row=4, columnspan=3, pady=5, padx=5)
        self.connect_button = ttk.Button(
            self.conn_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=0)
        self.discon_button = ttk.Button(
            self.conn_frame, text="Disconnect", command=self.disconnect)
        self.discon_button.grid(row=0, column=1)
        self.conn_indicator = tk.Label(
            self.conn_frame, width=5, height=1, bg="darkgray")
        self.conn_indicator.grid(row=0, column=2, padx=5, pady=5)

        # Buttons to connect the hexacontroller and start running the procedure
        run_button = ttk.Button(left_frame,
                                text="Run",
                                command=self.run_procedure)
        run_button.grid(row=5, columnspan=1)

        # Create log text widget in the right frame
        log_label = ttk.Label(right_frame, text="Procedure Log")
        log_label.pack(fill='x')
        self.log_text = tk.Text(right_frame)
        self.log_text.pack(fill='both', expand=True)

    def refresh_available_procs_and_hexacontrollers(self):
        self.procedure_var.set(
            list(map(lambda p: p.name, self.app_state.procedures)))
        self.hexa_var.set(
            list(map(lambda p: p.name, self.app_state.hexactrls)))

    def update_procedure_selection(self, proc_idx: Tuple[int]):
        print("updating procedure selection")
        self.app_state.running_procedure_config = deepcopy(
                self.app_state.procedures[proc_idx[0]])

    def update_hexacontroller_selection(self, hex_idx: Tuple[int]):
        print("updating hexacontroller selection")
        self.app_state.running_hexactrl_config = deepcopy(
                self.app_state.hexactrls[hex_idx[0]])

    def run_procedure(self):
        procedure = self.app_state.running_procedure_config
        self.hexa_selection['state'] = tk.DISABLED
        self.procedure_selection['state'] = tk.DISABLED

        self.log_text.insert('end', f"Running {procedure}...\n")
        self.log_text.update_idletasks()

        # Simulating a long-running procedure
        for i in range(5):
            self.log_text.insert('end', f"Step {i + 1}\n")
            self.log_text.see('end')
            self.log_text.update_idletasks()
            self.after(1000)  # Delay of 1 second

        self.log_text.insert('end', f"{procedure} completed.\n")
        self.hexa_selection['state'] = tk.NORMAL
        self.procedure_selection['state'] = tk.NORMAL

    def connect(self):
        self.app_state.running_hexactrl_config.connected = True
        self.update_connection_indication()

    def update_connection_indication(self):
        self.connect_button['state'] = tk.NORMAL if not self.app_state.running_hexactrl_config.connected else tk.DISABLED
        self.discon_button['state'] = tk.NORMAL if self.app_state.running_hexactrl_config.connected else tk.DISABLED
        self.conn_indicator.configure(
            bg="limegreen" if self.app_state.running_hexactrl_config.connected else "darkgray")

    def disconnect(self):
        self.app_state.running_hexactrl_config.connected = False
        self.update_connection_indication()
