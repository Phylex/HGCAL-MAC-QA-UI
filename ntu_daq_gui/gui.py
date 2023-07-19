import tkinter as tk
from tkinter import ttk
import json

class GUI(tk.Tk):
    def __init__(self, config_params, config_file_path):
        super().__init__()
        self.title("MAC Module Tests")
        self.config_params = config_params
        self.config_file_path = config_file_path

        # Create a notebook (tabs container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Create the two tabs
        self.run_control_tab = ttk.Frame(self.notebook)
        self.config_params_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.run_control_tab, text='Run Control')
        self.notebook.add(self.config_params_tab, text='Configuration')

        # Run Control Tab
        self.procedures = self.config_params.get("procedures", [])
        self.procedure_var = tk.StringVar()
        self.procedure_var.set(self.procedures[0])

        # Create left and right frames in the run control tab
        left_frame = ttk.Frame(self.run_control_tab)
        left_frame.grid(row=0, column=0, sticky='nsew')

        right_frame = ttk.Frame(self.run_control_tab)
        right_frame.grid(row=0, column=1, sticky='nsew')

        # Create widgets in the left frame
        procedure_label = ttk.Label(left_frame, text="Select Procedure:")
        procedure_label.pack()

        procedure_dropdown = ttk.OptionMenu(left_frame,
                                            self.procedure_var,
                                            *self.procedures)
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
        self.config_params.pop("procedures", None)  # Remove "procedures" from config

        self.create_config_widgets()

        # Configure grid weights
        self.run_control_tab.columnconfigure(1, weight=1)
        self.run_control_tab.rowconfigure(0, weight=0)
        self.run_control_tab.rowconfigure(1, weight=1)


    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config_params, f)

    def create_procedures_widgets(self):
        procedures_frame = ttk.Frame(self.config_params_tab)
        procedures_frame.pack()

        add_button = ttk.Button(procedures_frame, text="Add Procedure", command=self.add_procedure)
        add_button.pack()

        for procedure in self.procedures:
            procedure_frame = ttk.Frame(procedures_frame)
            procedure_frame.pack()

            name_label = ttk.Label(procedure_frame, text="Procedure Name:")
            name_label.pack(side='left')

            name_entry = ttk.Entry(procedure_frame)
            name_entry.insert(0, procedure.get("name", ""))
            name_entry.pack(side='left')

            file_label = ttk.Label(procedure_frame, text="Executed File:")
            file_label.pack(side='left')

            file_entry = ttk.Entry(procedure_frame)
            file_entry.insert(0, procedure.get("file", ""))
            file_entry.pack(side='left')

            remove_button = ttk.Button(procedure_frame, text="Remove", command=lambda frame=procedure_frame: self.remove_procedure(frame))
            remove_button.pack(side='left')

    def add_procedure(self):
        procedure = {"name": "", "file": ""}  # New procedure dictionary
        self.procedures.append(procedure)
        self.create_procedures_widgets()

    def remove_procedure(self, frame):
        frame.pack_forget()  # Remove the procedure frame from the GUI
        procedure = {"name": "", "file": ""}  # Find the corresponding procedure in the procedures list
        for index, item in enumerate(self.procedures):
            if item == procedure:
                self.procedures.pop(index)
                break

    def create_config_widgets(self):
        self.create_procedures_widgets()
        for param, value in self.config_params.items():
            label = ttk.Label(self.config_params_tab, text=param)
            label.pack()
            entry = ttk.Entry(self.config_params_tab)
            entry.insert(0, value)
            entry.pack(fill='x')
            entry.bind("<FocusOut>", self.update_config_param)

    def update_config_param(self, event):
        widget = event.widget
        param = widget.get()
        label = widget.master.winfo_children()[widget.grid_info()['row'] - 1]
        param_name = label.cget("text")
        self.config_params[param_name] = param
        self.save_config()

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
    gui = GUI()
    gui.mainloop()
