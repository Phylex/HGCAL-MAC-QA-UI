from tkinter import ttk
import tkinter as tk
from typing import Dict
from ping3 import ping
import paramiko
from tkinter import simpledialog


class ConnectionError(Exception):
    def __init__(self, message="An error occured while setting up the SSH connection"):
        super().__init__(message)


class TransmissionError(Exception):
    def __init__(self, message="An error occured during the execution of a coomand"):
        super().__init__(message)


class Hexacontroller:
    def __init__(self, username, password, hostname, port=22,
                 startup_commands=[],
                 daq_server_start_cmd="",
                 sc_server_start_cmd="",
                 shutdown_commands=[],
                 available_images=[], name=None):
        if name is not None:
            self.name = name
        else:
            self.name = hostname
        self.username = username
        self.port = port
        self.password = password
        self.hostname = hostname
        self.startup_commands = startup_commands
        self.daq_server_start_cmd = daq_server_start_cmd
        self.sc_server_start_cmd = sc_server_start_cmd
        self.shutdown_commands = shutdown_commands
        self.available_images = available_images
        self.command_running = False
        self.connected = False

    def connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh_client.connect(self.hostname, self.port,
                                    self.username, self.password)
            self.ssh_transport = self.ssh_client.get_transport()
            self.connected = True
        except paramiko.SSHException as e:
            raise ConnectionError from e

    def disconnect(self):
        self.ssh_client.close()
        self.connected = False

    def host_up(self) -> bool:
        pres = ping(self.hostname)
        return True if pres is not None else pres

    def ssh_execute_command(self, command):
        try:
            self.channel = self.ssh_transport.open_session()
            self.channel.exec_command(command)
            self.command_running = True
        except paramiko.SSHException as e:
            raise ConnectionError from e

    def get_command_output(self):
        if self.channel is None:
            return None
        try:
            if self.channel.recv_ready():
                return self.channel.recv(4096).decode('utf-8')
            return ""
        except paramiko.SSHException as e:
            raise TransmissionError from e

    def command_completed(self):
        try:
            if self.channel.exit_status_ready() is True:
                return self.channel.exit_status
        except paramiko.SSHException as e:
            raise TransmissionError from e
        return False

    def serialize(self):
        return {"hostname": self.hostname,
                "port": self.port,
                "username": self.username,
                "password": self.password,
                "init_commands": self.startup_commands,
                "shutdown_commands": self.shutdown_commands,
                "daq_server_start_cmd": self.daq_server_start_cmd,
                "sc_server_start_cmd": self.sc_server_start_cmd,
                }

    @classmethod
    def load_from_config(cls, config: Dict):
        """
        given a config entry that matches the entry for a Hexacontroller load it
        """
        return cls(
            username=config.get('username', ""),
            password=config.get('password', ""),
            hostname=config.get('hostname', ""),
            port=config.get('port', 22),
            startup_commands=config.get('init_commands', []),
            shutdown_commands=config.get('shutdown_commands', []),
            daq_server_start_cmd=config.get('daq_server_start_cmd', ""),
            sc_server_start_cmd=config.get('sc_server_start_cmd', ""),
        )


class HexacontrollerCreationUI(simpledialog.Dialog):
    def body(self, master):
        self.title("Create Hexacontroller Configuration")
        self.__mas = master
        self.options = {}

        tk.Label(master, text="Hostname:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="Port:").grid(row=1, sticky=tk.W)
        tk.Label(master, text="Username:").grid(row=2, sticky=tk.W)
        tk.Label(master, text="Password:").grid(row=3, sticky=tk.W)

        self.hostname_entry = tk.Entry(master)
        self.hostname_entry.grid(row=0, column=1)

        self.port_entry = tk.Entry(master)
        self.port_entry.grid(row=1, column=1)

        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=2, column=1)

        self.password_entry = tk.Entry(master)
        self.password_entry.grid(row=3, column=1)

    def apply(self):
        hostname = self.hostname_entry.get()
        port = self.port_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.result = Hexacontroller(username, password, hostname, port)


class HexactrlConfigUI(ttk.Frame):
    """
    UI for the Hexacontroller configuration
    """

    def __init__(self, hexactrl: Hexacontroller, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.hexactrl = hexactrl
        self.init_command_entries = []
        self.shutdown_command_entries = []
        self.grid(pady=5, padx=5)

        self.populate()

    def populate(self):
        """
        Set up the UI of the Hexactrl interface
        """
        ttk.Label(self, text="Name:").grid(row=0, column=0, padx=2, pady=2)
        self.name_var = tk.StringVar()
        self.name_var.set(self.hexactrl.name)
        self.name_var.trace_add("write", self.update_name)
        self.name_entry = ttk.Entry(self, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=2)
        
        ttk.Label(self, text="Hostname:").grid(row=1, column=0, padx=2, pady=2)
        self.host_var = tk.StringVar()
        self.host_var.set(self.hexactrl.hostname)
        self.host_var.trace_add("write", self.update_hostname)
        self.host_entry = ttk.Entry(self, textvariable=self.host_var)
        self.host_entry.grid(row=1, column=2)

        ttk.Label(self, text="Port:").grid(
                row=2, column=0, padx=2, pady=2)
        self.port_var = tk.IntVar()
        self.port_var.set(self.hexactrl.port)
        self.port_var.trace_add("write", self.update_port)
        self.port_entry = ttk.Entry(self, textvariable=self.port_var)
        self.port_entry.grid(row=2, column=2)

        ttk.Label(self, text="SSH Username:").grid(
            row=3, column=0, padx=2, pady=2)
        self.user_var = tk.StringVar()
        self.user_var.set(self.hexactrl.username)
        self.user_var.trace_add("write", self.update_username)
        self.user_entry = ttk.Entry(self, textvariable=self.user_var)
        self.user_entry.grid(row=3, column=2)

        ttk.Label(self, text="SSH Password:").grid(
            row=4, column=0, padx=2, pady=2)
        self.pswd_var = tk.StringVar()
        self.pswd_var.set(self.hexactrl.password)
        self.pswd_var.trace_add("write", self.update_password)
        self.pswd_entry = ttk.Entry(self, textvariable=self.pswd_var)
        self.pswd_entry.grid(row=4, column=2)


        # The startup commands are built using entries that
        # automatically update the state of the variables stored in
        # the hexacontroller
        init_cmd_label = ttk.Label(self, text="Initialization Commands")
        init_cmd_label.grid(row=5, column=0)
        self.add_init_cmd_button = ttk.Button(
            self, text="Add startup Command", command=self.add_startup_cmd)
        self.add_init_cmd_button.grid(row=5, column=2)
        self.init_cmd_frame = ttk.Frame(self, relief="groove", padding=5)
        self.init_cmd_frame.grid(row=6, columnspan=3)

        # The shutdown commands are built using entries that
        # automatically update the state of the variables stored in
        # the hexacontroller
        shutdown_cmd_label = ttk.Label(self, text="Shutdown Commands")
        shutdown_cmd_label.grid(row=7, column=0, pady=5)
        self.add_shutdown_cmd_button = ttk.Button(
            self, text="Add shutdown Command", command=self.add_shutdown_cmd)
        self.add_shutdown_cmd_button.grid(row=7, column=2, pady=5)
        self.shutdown_cmd_frame = ttk.Frame(self, relief="groove", padding=5)
        self.shutdown_cmd_frame.grid(row=8, columnspan=3)

        # Variable for storing the start command for the daq server
        self.daq_start_var = tk.StringVar()
        self.daq_start_var.set(self.hexactrl.daq_server_start_cmd)
        self.daq_start_var.trace_add("write", self.update_daq_start_command)
        daq_server_cmd_label = ttk.Label(self, text="DAQ Server Start Command")
        daq_server_cmd_label.grid(row=9, column=0)
        daq_server_cmd_entry = ttk.Entry(self, textvariable=self.daq_start_var)
        daq_server_cmd_entry.grid(row=9, column=1, columnspan=2)
        daq_server_cmd_entry.insert(tk.END, self.hexactrl.daq_server_start_cmd)

        # Variable for storing the start command for the slow control server
        self.sc_start_var = tk.StringVar()
        self.sc_start_var.set(self.hexactrl.sc_server_start_cmd)
        self.sc_start_var.trace_add("write", self.update_sc_start_command)
        sc_server_cmd_label = ttk.Label(
            self, text="Slow control Start Command")
        sc_server_cmd_label.grid(row=10, column=0)
        sc_server_cmd_entry = ttk.Entry(self, textvariable=self.sc_start_var)
        sc_server_cmd_entry.grid(row=10, column=1, columnspan=2)
        sc_server_cmd_entry.insert(tk.END, self.hexactrl.daq_server_start_cmd)

        self.refresh_init_cmds()
        self.refresh_shutdown_cmds()

    # These functions allow for the addition and removal of commands to the
    # startup procedure of the hexacontroller
    def add_startup_cmd(self):
        self.hexactrl.startup_commands.append("")
        self.refresh_init_cmds()

    def remove_startup_cmd(self, idx):
        del self.hexactrl.startup_commands[idx]
        self.refresh_init_cmds()

    def update_init_cmds(self, idx):
        print("updating startup commands")
        self.hexactrl.startup_commands[idx] = \
            self.init_command_entries[idx].get()

    def refresh_init_cmds(self):
        for child in self.init_cmd_frame.winfo_children():
            child.destroy()
        self.init_command_entries = []
        for i, cmd in enumerate(self.hexactrl.startup_commands):
            entry_var = tk.StringVar()
            entry_var.set(cmd)
            entry_var.trace_add(
                "write",
                lambda *args, idx=i: self.update_init_cmds(idx))
            self.init_command_entries.append(entry_var)
            entry = ttk.Entry(
                self.init_cmd_frame,
                textvariable=entry_var)
            entry.grid(row=i, column=0)
            rm_btn = ttk.Button(self.init_cmd_frame,
                                text="Remove",
                                command=lambda: self.remove_startup_cmd(i))
            rm_btn.grid(row=i, column=1)

    # These functions allow for the addition and removal of commands to the
    # startup procedure of the hexacontroller
    def update_shutdown_cmds(self, idx):
        print("updating shutdown commands")
        self.hexactrl.shutdown_commands[idx] = \
            self.shutdown_command_entries[idx].get()

    def remove_shutdown_cmd(self, idx):
        del self.hexactrl.shutdown_commands[idx]
        self.refresh_shutdown_cmds()

    def add_shutdown_cmd(self):
        self.hexactrl.shutdown_commands.append("")
        self.refresh_shutdown_cmds()

    def refresh_shutdown_cmds(self):
        for child in self.shutdown_cmd_frame.winfo_children():
            child.destroy()
        self.shutdown_command_entries = []
        for i, cmd in enumerate(self.hexactrl.shutdown_commands):
            entry_var = tk.StringVar()
            entry_var.set(cmd)
            entry_var.trace_add(
                "write",
                lambda *args, idx=i: self.update_shutdown_cmds(idx))
            self.shutdown_command_entries.append(entry_var)
            entry = ttk.Entry(
                self.shutdown_cmd_frame,
                textvariable=entry_var)
            entry.grid(row=i, column=0)
            rm_btn = ttk.Button(self.shutdown_cmd_frame,
                                text="Remove",
                                command=lambda: self.remove_shutdown_cmd(i))
            rm_btn.grid(row=i, column=1)

    def update_daq_start_command(self, *args):
        self.hexactrl.daq_server_start_cmd = self.daq_start_var.get()

    def update_sc_start_command(self, *args):
        self.hexactrl.sc_server_start_cmd = self.sc_start_var.get()

    def update_hostname(self, *args):
        self.hexactrl.hostname = self.host_var.get()

    def update_port(self, *args):
        self.hexactrl.port = self.port_var.get()

    def update_username(self, *args):
        self.hexactrl.username = self.user_var.get()

    def update_password(self, *args):
        self.hexactrl.password = self.pswd_var.get()

    def update_name(self, *args):
        self.hexactrl.name = self.name_var.get()
