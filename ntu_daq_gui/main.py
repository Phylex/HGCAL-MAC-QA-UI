from ntu_daq_gui import config
from ntu_daq_gui import gui


def main():
    print("Hello")
    app_configuration, config_file_path = config.get_config()
    ui = gui.GUI(app_configuration, config_file_path)
    ui.mainloop()
