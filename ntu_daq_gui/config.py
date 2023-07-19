import json
import os
import shutil

config_file = ""

def get_config_path():
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        config_dir = xdg_config_home
    else:
        config_dir = os.path.join(os.path.expanduser('~'), '.config')
    if not os.path.exists(config_dir):
        print("Directory \"~/.config\" not found. Unable to retrieve config")
        exit(-1)
    return os.path.join(config_dir, 'mac-daq-config.conf')


def create_default_config():
    template_path = os.path.join(os.path.dirname(__file__), 'config_template.conf')
    config_path = get_config_path()
    shutil.copy(template_path, config_path)
    print(f"Default configuration file created at {config_path}")


def load_config(path):
    with open(path, 'r') as cfile:
        try:
            config = json.load(cfile)
            return config
        except json.JSONDecodeError:
            print("Unable to decode JSON, there is something wrong with "
                  "the configuration file format")
            exit(-1)


def get_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        print(f"Configuration file found at {config_path}")
        # Load and use the existing configuration
    else:
        print("Configuration file not found. Creating default configuration...")
        create_default_config()
    return load_config(config_path), config_path

