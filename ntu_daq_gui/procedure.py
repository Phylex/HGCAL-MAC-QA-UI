import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
import json
import os
from typing import Tuple, Dict


class Procedure:
    def __init__(self, name, executed_file,
                 options: Dict[str, Tuple[str, str]],
                 initial_dut_config,
                 hostname_flag: str = "-i", port_flag: str = "-p"):
        self.name = name
        self.executed_file = executed_file
        self.options = options
        self.initial_dut_config = initial_dut_config
        self.hostname_flag = hostname_flag
        self.port_flag = port_flag
        self.running = False

    def serialize(self):
        return {
            'name': self.name,
            'executed_file': self.executed_file,
            'options': self.options,
            'initial_dut_config': self.initial_dut_config
        }

    @classmethod
    def deserialize(cls, json_string):
        data = json.loads(json_string)
        return cls(data['name'],
                   data['executed_file'],
                   data['options'],
                   data['initial_dut_config'])

    def add_option(self, name, flag, value):
        self.options[name] = (flag, value)

    def get_options(self):
        return self.options.items()

    def gen_run_command(self, hexctrl_hostname: str, hexctrl_port: str):
        run_command_args = []
        run_command_args.append(self.executed_file)
        run_command_args.append(self.hostname_flag)
        run_command_args.append(hexctrl_hostname)
        run_command_args.append(self.port_flag)
        run_command_args.append(hexctrl_port)
        run_command_args.append("-f")
        run_command_args.append(self.initial_dut_config)
        for option in self.options:
            run_command_args.append(str(option[0]))
            run_command_args.append(str(option[1]))

class OptionDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Add Option")

        tk.Label(master, text="Name:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="Flag:").grid(row=1, sticky=tk.W)
        tk.Label(master, text="Value:").grid(row=2, sticky=tk.W)

        self.name_entry = tk.Entry(master)
        self.name_entry.grid(row=0, column=1)

        self.flag_entry = tk.Entry(master)
        self.flag_entry.grid(row=1, column=1)

        self.val_entry = tk.Entry(master)
        self.val_entry.grid(row=2, column=1)

    def apply(self):
        name = self.name_entry.get()
        flag = self.flag_entry.get()
        value = self.val_entry.get()
        self.result = (name, flag, value)


class ProcedureCreationUI(simpledialog.Dialog):
    def body(self, master):
        self.title("Create DataClass")
        self.__mas = master
        self.options = {}

        tk.Label(master, text="Name:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="Script File:").grid(row=1, sticky=tk.W)
        tk.Label(master, text="Initial Config:").grid(row=2, sticky=tk.W)

        self.name_entry = tk.Entry(master)
        self.name_entry.grid(row=0, column=1)

        self.exec_file_entry = tk.Entry(master)
        self.exec_file_entry.grid(row=1, column=1)
        self.exec_file_button = tk.Button(
            master,
            text="Browse",
            command=self.browse_executed_file).grid(row=1, column=2)

        self.init_conf_entry = tk.Entry(master)
        self.init_conf_entry.grid(row=2, column=1)
        self.init_conf_button = tk.Button(
            master,
            text="Browse",
            command=self.browse_init_config).grid(row=2, column=2)

        self.add_option_button = tk.Button(
            master,
            text="Add Command Option",
            command=self.add_option).grid(row=3, column=1)

        tk.Label(master, text="Options")
        self.tree = ttk.Treeview(master,
                                 columns=("Description", "flag", "Value"),
                                 show="headings")
        self.tree.heading("Description", text="Description")
        self.tree.heading("flag", text="Cmd Flag")
        self.tree.heading("Value", text="Value")
        self.tree.grid(columnspan=3, padx=3)
        master.columnconfigure(1, weight=1)

    def browse_executed_file(self):
        file_path = filedialog.askopenfilename(title="Select Executed File")
        if file_path:
            self.exec_file_entry.delete(0, tk.END)
            self.exec_file_entry.insert(tk.END, file_path)

    def browse_init_config(self):
        file_path = filedialog.askopenfilename(
            title="Select Initial DUT Config")
        if file_path:
            self.init_conf_entry.delete(0, tk.END)
            self.init_conf_entry.insert(tk.END, file_path)

    def add_option(self):
        od = OptionDialog(self.__mas)
        self.options[od.result[0]] = (od.result[1], od.result[2])
        self.tree.insert("", "end", values=od.result)

    def apply(self):
        name = self.name_entry.get()
        script = self.exec_file_entry.get()
        init_conf = self.init_conf_entry.get()
        self.result = Procedure(name,
                                executed_file=script,
                                initial_dut_config=init_conf,
                                options=self.options)


class ProcedureConfigUI:
    def __init__(self, parent, procedure: Procedure):
        self.parent = parent
        self.procedure = procedure

        self.name_label = ttk.Label(parent, text="Description:")
        self.name_label.grid(row=0, column=0)
        self.name_entry = ttk.Entry(parent)
        self.name_entry.grid(row=0, column=1)
        self.name_entry.insert(tk.END, self.procedure.name)

        self.executed_file_label = ttk.Label(parent, text="Executed File:")
        self.executed_file_label.grid(row=1, column=0)
        self.executed_file_entry = ttk.Entry(parent)
        self.executed_file_entry.grid(row=1, column=1)
        self.executed_file_entry.insert(tk.END, self.procedure.executed_file)
        self.executed_file_button = ttk.Button(
            parent, text="Browse", command=self.browse_executed_file)
        self.executed_file_button.grid(row=1, column=2)

        self.init_config_label = ttk.Label(
            parent, text="Initial DUT Config:")
        self.init_config_label.grid(row=2, column=0)
        self.init_config_entry = ttk.Entry(parent)
        self.init_config_entry.grid(row=2, column=1)
        self.init_config_entry.insert(
            tk.END, self.procedure.initial_dut_config)
        self.init_config_button = ttk.Button(
            parent, text="Browse", command=self.browse_initial_dut_config)
        self.init_config_button.grid(row=2, column=2)

        self.options_label = ttk.Label(parent, text="Options")
        self.options_label.grid(row=3, column=0)
        self.add_option_button = ttk.Button(parent,
                                            text="Add Option",
                                            command=self.add_option)
        self.add_option_button.grid(row=3, column=2)
        self.options_frame = ttk.Frame(parent, relief="solid", padding=5)
        self.options_frame.grid(columnspan=3)
        self.options_frame.grid_rowconfigure(0, weight=1)
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.refresh_option_entries()

    def add_option(self):
        od = OptionDialog(self.parent)
        self.procedure.add_option(*od.result)
        self.refresh_option_entries()

    def create_option_entry(self, option_name, flag, value, idx):
        option_label = ttk.Label(self.options_frame, text=f"{option_name}")
        option_label.grid(row=idx, column=0)
        flag_label = ttk.Label(self.options_frame, text=f"{flag}")
        flag_label.grid(row=idx, column=1)
        value_label = ttk.Label(self.options_frame, text=f"{value}")
        value_label.grid(row=idx, column=2)
        remove_button = ttk.Button(self.options_frame, text="Remove",
                                   command=lambda: self.remove_option(option_name))
        remove_button.grid(row=idx, column=3)

    def remove_option(self, option_name):
        if option_name in self.procedure.options:
            del self.procedure.options[option_name]
            self.refresh_option_entries()

    def refresh_option_entries(self):
        for child in self.options_frame.winfo_children():
            child.destroy()
        if len(self.procedure.options) > 0:
            ttk.Label(self.options_frame, text="Description").grid(
                row=0, column=0)
            ttk.Label(self.options_frame, text="Cmd Flag").grid(
                row=0, column=1)
            ttk.Label(self.options_frame, text="Value").grid(row=0, column=2)
        for i, (option_name, (flag, value)) in enumerate(self.procedure.options.items()):
            self.create_option_entry(option_name, flag, value, i+1)

    def check_file_exists(self, filepath):
        return os.path.isfile(filepath)

    def browse_executed_file(self):
        file_path = filedialog.askopenfilename(title="Select Executed File")
        if file_path:
            self.procedure.executed_file = file_path
            self.executed_file_entry.delete(0, tk.END)
            self.executed_file_entry.insert(tk.END, file_path)

    def browse_initial_dut_config(self):
        file_path = filedialog.askopenfilename(
            title="Select Initial DUT Config")
        if file_path:
            self.procedure.initial_dut_config = file_path
            self.init_config_entry.delete(0, tk.END)
            self.init_config_entry.insert(tk.END, file_path)


# Usage example:
if __name__ == "__main__":
    name = "Procedure 1"
    executed_file = "script.py"
    initial_dut_config = "dut_config.json"
    options = {
        'option1': ('-o1', 'value1'),
        'option2': ('-o2', 'value2'),
        'option3': ('-o3', 'value3'),
    }

    config = Procedure(name, executed_file, options, initial_dut_config)

    root = tk.Tk()
    editor = ProcedureConfigUI(root, config)
    root.mainloop()
