import os
from calm.dsl.config import get_config, get_config_file


def set_config(section, **kwargs):

    # Creating config file if not present
    config_file = get_config_file()
    if not os.path.exists(config_file):
        os.makedirs(os.path.dirname(config_file))
        open(config_file, "w+").close()

    section_field_mapping = {
        "SERVER": {
            "ip": "pc_ip",
            "port": "pc_port",
            "username": "pc_username",
            "password": "pc_password",
        },
        "PROJECT": {"name": "name", "uuid": "uuid"},
        "DATABASE": {"location": "location"},
    }

    config_parser = get_config()

    field_map = section_field_mapping[section]

    for key, value in kwargs.items():
        if value:
            config_parser.set(section, field_map[key], value)

    with open(config_file, "w") as configfile:
        config_parser.write(configfile)


def print_config():

    config_parser = get_config()
    for section_name in config_parser.sections():
        print("\n{}".format(section_name))
        if not config_parser[section_name]:
            print("  configuration not found")

        for key, value in config_parser.items(section_name):
            print("  {} = {}".format(key, value))
