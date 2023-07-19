import tkinter as tk
from tkinter import ttk
import json
from ntu_daq_gui import procedure as prc
from functools import partial


class GUI(tk.Tk):
    def __init__(self, config_params, config_file_path):
        super().__init__()
        # Initialize the data structures
        self.title("MAC Module Tests")
        self.config_params = config_params
        self.config_file_path = config_file_path
        print(self.config_params)
        self.procedures = list(
                map(lambda p: prc.Procedure(
                    p.get("name"),
                    p.get("executed_file", ""),
                    p.get("options", {}),
                    p.get("initial_dut_config", "")),
                    self.config_params.get("procedures", [])))

        # Create a notebook (tabs container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Create the two tabs
        self.run_control_tab = ttk.Frame(self.notebook)
        self.procedure_config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.run_control_tab, text='Run Control')
        self.notebook.add(self.procedure_config_tab, text='Configuration')

        # Run Control Tab

        self.procedure_var = tk.StringVar()
        self.procedure_var.set(self.procedures[0].name)

        # Create left and right frames in the run control tab
        left_frame = ttk.Frame(self.run_control_tab)
        left_frame.grid(row=0, column=0, sticky='nsew')

        right_frame = ttk.Frame(self.run_control_tab)
        right_frame.grid(row=0, column=1, sticky='nsew')

        # Create widgets in the left frame
        procedure_label = ttk.Label(left_frame, text="Select Procedure:")
        procedure_label.pack()

        procedure_dropdown = ttk.OptionMenu(
                left_frame,
                self.procedure_var,
                *list(map(lambda p: p.name, self.procedures)))
        procedure_dropdown.pack(fill='x')

        run_button = ttk.Button(left_frame,
                                text="Run",
                                command=self.run_procedure)
        run_button.pack()

        close_button = ttk.Button(left_frame,
                                  text="Close",
                                  command=self.close_window)
        close_button.pack()

        # Create log text widget in the right frame
        procedure_label = ttk.Label(right_frame, text="Procedure Log")
        procedure_label.pack()
        self.log_text = tk.Text(right_frame)
        self.log_text.pack(fill='both', expand=True)

        # Config Parameters Tab
        self.config_params.pop("procedures", None)

        self.setup_procedure_widgets(self.procedure_config_tab)

        # Configure grid weights
        self.run_control_tab.columnconfigure(1, weight=1)
        self.run_control_tab.rowconfigure(0, weight=0)
        self.run_control_tab.rowconfigure(1, weight=1)

    def save_config(self):
        """
        Write the config parameters to the config file
        """
        with open(self.config_file_path, 'w') as f:
            json.dump(self.config_params, f)

    def setup_procedure_widgets(self, frame):
        frame.grid_forget()

        add_button = ttk.Button(frame,
                                text="Add Procedure",
                                command=partial(self.add_procedure, frame))
        add_button.grid()
        for i, procedure in enumerate(self.procedures):
            self.draw_procedure(frame, procedure, i)

    def draw_procedure(self, frame, procedure, i):
        proc_frame = ttk.Frame(frame, borderwidth=2, relief="groove")
        proc_frame.grid(padx=5, pady=5)
        prc.ProcedureConfigUI(proc_frame, procedure)
        ttk.Button(proc_frame, text="Remove Procedure",
                   command=partial(self.remove_procedure, i, frame))

    def add_procedure(self, parent):
        pcui = prc.ProcedureCreationUI(parent)
        self.procedures.append(pcui.result)
        self.draw_procedure(parent, pcui.result, len(self.procedures) - 1)

    def remove_procedure(self, proc_idx, parent):
        parent.pack_forget()  # Remove the procedure frame from the GUI
        self.procedures.pop(proc_idx)
        self.setup_procedure_widgets(parent)

    def run_procedure(self):
        procedure = self.procedure_var.get()
        self.log_text.insert('end', f"Running {procedure}...\n")
        self.log_text.update_idletasks()

        # Simulating a long-running procedure
        for i in range(5):
            self.log_text.insert('end', f"Step {i + 1}\n")
            self.log_text.see('end')
            self.log_text.update_idletasks()
            self.after(1000)  # Delay of 1 second

        self.log_text.insert('end', f"{procedure} completed.\n")

    def close_window(self):
        self.destroy()


if __name__ == '__main__':
    with open('./config_template.json', 'r') as cf:
        config = json.load(cf)
    gui = GUI(config, './config_template.json')
    gui.mainloop()
