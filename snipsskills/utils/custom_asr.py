# -*-: coding utf-8 -*-
""" Custom ASR installer """

import getpass
import os
import subprocess


from .os_helpers import execute_command, execute_root_command, get_command_output, cmd_exists, which, get_default_user
from systemd import Systemd, SNIPS_SERVICE_NAME


class CustomASR:
    """ CustomASR utilities. """

    def __init__(self, asr_folder_path):
        self.ASR_ARGUMENTS = "-v /opt/snips/config/assistant/custom_asr:/usr/share/snips/asr"
        self.separation_string = "snipsdocker/platform"
        self.asr_folder_path = asr_folder_path
        self.snips_command_path = self.get_snips_command_path()
        self.default_user = get_default_user()

    def setup(self):
        """
        To setup the ASR, we go through the following steps.
        - Move the ASR model to an appropriate location (done by the `snips-install-assistant` program
        - Change the `snips` script to add ASR tags
        """
        self.update_snips_command()

    def get_snips_command_path(self):
        snips_command_path = which("snips")

        if snips_command_path is None or len(snips_command_path.strip()) == 0:
            snips_command_path = raw_input("Path to the snips binary: ")

        return snips_command_path


    def update_snips_command(self):
        if not cmd_exists("snips"):
            return
        else:
            updated_snips_cmd = self.generate_updated_snips_command()
            self.write_command_to_snips_command_file(updated_snips_cmd)
            return

    def write_command_to_snips_command_file(self, cmd):
        updated_snips_command_line = self.generate_updated_snips_command()

        full_command = self.get_snips_command_template() + "\n" + updated_snips_command_line

        execute_root_command("sudo cp {} {}.backup".format(self.snips_command_path, self.snips_command_path))
        execute_root_command("sudo echo \"{}\" > {}".format(full_command, self.snips_command_path))
        execute_root_command("sudo chmod a+rwx {}".format(self.snips_command_path))

    def generate_updated_snips_command(self):
        current_snips_command = self.get_current_snips_command()

        if 'asr' in current_snips_command.lower():  # This means, we already updated the snips command
            return current_snips_command
        else:
            index_of_separation = current_snips_command.find(self.separation_string)
            current_snips_command = current_snips_command[:index_of_separation] \
                                    + self.ASR_ARGUMENTS \
                                    + current_snips_command[index_of_separation:]

            return current_snips_command

    def get_template(self):
        if cmd_exists('snips'):
            return get_command_output(['head', '-n', '-1', self.snips_command_path]).rstrip()
        else:
            return None