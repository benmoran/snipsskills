# -*-: coding utf-8 -*-
""" Systemd utilities. """

import getpass
import os
import subprocess
import time

from .os_helpers import execute_command, ask_yes_no, which

SNIPS_SERVICE_NAME = "snips"
SNIPSSKILLS_SERVICE_NAME = "snipsskills"


class Systemd:
    """ Systemd utilities. """

    @staticmethod
    def setup(use_default_values=None):
        if ask_yes_no("Would you like Snips to start on boot (using systemd)?", use_default_values) == False:
            return

        (username, snips_home_path, snipsskills_path,
         snips_path) = Systemd.get_snipsskills_params(use_default_values=use_default_values)
        Systemd.write_snips_file(username, snips_path)
        Systemd.write_snipsskills_file(
            username, snips_home_path, snipsskills_path)
        Systemd.enable_service(username, SNIPS_SERVICE_NAME)
        Systemd.enable_service(username, SNIPSSKILLS_SERVICE_NAME)

    @staticmethod
    def get_snipsskills_params(use_default_values=None):
        current_username = getpass.getuser()
        if use_default_values == True:
            username = current_username
        else:
            username = raw_input(
                "Run as user [default: {}]: ".format(current_username))
        if username is None or username.strip() == "":
            username = current_username

        snips_home_path = os.getcwd()

        snipsskills_path = which('snipsskills')
        if snipsskills_path is None or len(snipsskills_path.strip()) == 0:
            if use_default_values != True:
                snipsskills_path = raw_input("Path to the snipsskills binary: ")

        snips_path = which('snips')
        if snips_path is None or len(snips_path.strip()) == 0:
            if use_default_values != True:
                snips_path = raw_input("Path to the snips binary: ")

        return (username, snips_home_path, snipsskills_path, snips_path)

    @staticmethod
    def write_snipsskills_file(username, snips_home_path, snipsskills_path):
        contents = Systemd.get_template(SNIPSSKILLS_SERVICE_NAME)
        if contents is None:
            return
        contents = contents.replace("{{SNIPS_HOME_PATH}}", snips_home_path) \
            .replace("{{SNIPSSKILLS_PATH}}", snipsskills_path)
        Systemd.write_systemd_file(
            SNIPSSKILLS_SERVICE_NAME, username, contents)

    @staticmethod
    def write_snips_file(username, snips_path):
        contents = Systemd.get_template(SNIPS_SERVICE_NAME)
        if contents is None:
            return
        contents = contents.replace("{{SNIPS_PATH}}", snips_path)
        Systemd.write_systemd_file(SNIPS_SERVICE_NAME, username, contents)

    @staticmethod
    def get_template(service_name):
        this_dir, this_filename = os.path.split(__file__)
        template_filename = os.path.join(
            this_dir, "../config/systemd/{}.service".format(service_name))
        with open(template_filename, 'r') as template_file:
            return template_file.read()
        return None

    @staticmethod
    def write_systemd_file(service_name, username, contents):
        if username is None:
            # Run as root
            output_filename = "/etc/systemd/system/{}.service".format(
                service_name)
        else:
            output_filename = "/etc/systemd/system/{}@{}.service".format(
                service_name, username)
        tmp_filename = "tmp_{}".format(service_name)
        os.system("sudo echo \"{}\" > {}".format(contents, tmp_filename))
        os.system("sudo mv {} {}".format(tmp_filename, output_filename))
        os.system("sudo chmod a+rwx {}".format(output_filename))

    @staticmethod
    def enable_service(username, service_name):
        os.system("sudo systemctl --system daemon-reload")
        if username is None:
            # Run as root
            os.system("sudo systemctl enable {}".format(service_name))
        else:
            os.system("sudo systemctl enable {}@{}".format(service_name, username))
