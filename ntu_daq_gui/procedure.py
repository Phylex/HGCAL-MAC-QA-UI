import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
import json
import os


class ProcedureConfiguration:
    def __init__(self, name, executed_file, options, initial_dut_config):
        self.name = name
        self.executed_file = executed_file
        self.options = options
        self.initial_dut_config = initial_dut_config

    def serialize(self):
        return json.dumps({
            'name': self.name,
            'executed_file': self.executed_file,
            'options': self.options,
            'initial_dut_config': self.initial_dut_config
        })

    @classmethod
    def deserialize(cls, json_string):
        data = json.loads(json_string)
        return cls(data['name'], data['executed_file'], data['options'], data['initial_dut_config'])


class ProcedureConfigEditor:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config

        self.name_label = tk.Label(parent, text="Name:")
        self.name_label.pack()
        self.name_entry = tk.Entry(parent)
        self.name_entry.pack()

        self.executed_file_label = tk.Label(parent, text="Executed File:")
        self.executed_file_label.pack()
        self.executed_file_entry = tk.Entry(parent)
        self.executed_file_entry.pack()
        self.executed_file_button = tk.Button(parent, text="Browse", command=self.browse_executed_file)
        self.executed_file_button.pack()

        self.initial_dut_config_label = tk.Label(parent, text="Initial DUT Config:")
        self.initial_dut_config_label.pack()
        self.initial_dut_config_entry = tk.Entry(parent)
        self.initial_dut_config_entry.pack()
        self.initial_dut_config_button = tk.Button(parent, text="Browse", command=self.browse_initial_dut_config)
        self.initial_dut_config_button.pack()

        self.options_label = tk.Label(parent, text="Options:")
        self.options_label.pack()

        self.options_frame = tk.Frame(parent)
        self.options_frame.pack()

        self.add_option_button = tk.Button(parent, text="Add Option", command=self.add_option)
        self.add_option_button.pack()

        self.serialize_button = tk.Button(parent, text="Serialize", command=self.serialize)
        self.serialize_button.pack()

        self.load_config()

    def load_config(self):
        self.name_entry.insert(tk.END, self.config.name)
        self.executed_file_entry.insert(tk.END, self.config.executed_file)
        self.initial_dut_config_entry.insert(tk.END, self.config.initial_dut_config)

        for option_name, (flag, value) in self.config.options.items():
            self.create_option_entry(option_name, flag, value)

    def add_option(self):
        option_name = simpledialog.askstring("Add Option", "Enter option name:")
        if option_name:
            flag = simpledialog.askstring("Add Option", f"Enter command flag for option '{option_name}':")
            if flag:
                value = simpledialog.askstring("Add Option", f"Enter value for option '{option_name}':")
                if value:
                    self.config.options[option_name] = (flag, value)
                    self.create_option_entry(option_name, flag, value)

    def create_option_entry(self, option_name, flag, value):
        option_frame = tk.Frame(self.options_frame)
        option_frame.pack(pady=5)

        option_label = tk.Label(option_frame, text=f"Option: {option_name}")
        option_label.pack(side=tk.LEFT)

        flag_label = tk.Label(option_frame, text=f"Flag: {flag}")
        flag_label.pack(side=tk.LEFT, padx=5)

        value_label = tk.Label(option_frame, text=f"Value: {value}")
        value_label.pack(side=tk.LEFT)
        
        remove_button = tk.Button(option_frame, text="Remove", command=lambda: self.remove_option(option_name))
        remove_button.pack(side=tk.LEFT, padx=5)

    def remove_option(self, option_name):
        if option_name in self.config.options:
            del self.config.options[option_name]
            self.refresh_option_entries()

    def refresh_option_entries(self):
        for child in self.options_frame.winfo_children():
            child.destroy()

        for option_name, (flag, value) in self.config.options.items():
            self.create_option_entry(option_name, flag, value)

    def serialize(self):
        self.config.name = self.name_entry.get()
        self.config.executed_file = self.executed_file_entry.get()
        self.config.initial_dut_config = self.initial_dut_config_entry.get()

        if not self.check_file_exists(self.config.executed_file):
            messagebox.showerror("File Not Found", f"The executed file '{self.config.executed_file}' does not exist. Please reenter path")
            return None

        if not self.check_file_exists(self.config.initial_dut_config):
            messagebox.showerror("File Not Found", f"The initial module config file '{self.config.initial_dut_config}' does not exist, Please reenter path")
            return None

        return self.config.serialize()

    def check_file_exists(self, filepath):
        return os.path.isfile(filepath)

    def browse_executed_file(self):
        file_path = filedialog.askopenfilename(title="Select Executed File")
        if file_path:
            self.config.executed_file = file_path
            self.executed_file_entry.delete(0, tk.END)
            self.executed_file_entry.insert(tk.END, file_path)

    def browse_initial_dut_config(self):
        file_path = filedialog.askopenfilename(title="Select Initial DUT Config")
        if file_path:
            self.config.initial_dut_config = file_path
            self.initial_dut_config_entry.delete(0, tk.END)
            self.initial_dut_config_entry.insert(tk.END, file_path)

# Usage example:
name = "Procedure 1"
executed_file = "script.py"
initial_dut_config = "dut_config.json"
options = {
    'option1': ('-o1', 'value1'),
    'option2': ('-o2', 'value2'),
    'option3': ('-o3', 'value3'),
}

config = ProcedureConfiguration(name, executed_file, options, initial_dut_config)

root = tk.Tk()
editor = ProcedureConfigEditor(root, config)
root.mainloop()
