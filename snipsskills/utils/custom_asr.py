# -*-: coding utf-8 -*-
""" Custom ASR installer """

import getpass
import os
import subprocess


from .os_helpers import execute_command, execute_root_command, get_command_output, cmd_exists, which, get_default_user
from systemd import Systemd, SNIPS_SERVICE_NAME


class CustomASR:
    """ CustomASR utilities. """

    def __init__(self, asr_archive_path):
        self.ASR_ARGUMENTS = "-v /opt/snips/asr:/usr/share/snips/asr "
        self.separation_string = "snipsdocker/platform"
        self.asr_archive_path = asr_archive_path
        self.snips_command_path = self.get_snips_command_path()
        self.default_user = get_default_user()

    def setup(self):
        """
        To setup the ASR, we go through the following steps.
        - Download the archive that contains the custom ASR model (optional)
        - Extract the archive
        - Move the ASR model to an appropriate location
        - Change the `snips` script to add ASR tags
        """

        self.extract_asr_archive()
        self.update_snips_command()

    def get_snips_command_path(self):
        snips_command_path = which("snips")

        if snips_command_path is None or len(snips_command_path.strip()) == 0:
            snips_command_path = raw_input("Path to the snips binary: ")

        return snips_command_path

    def generate_asr_archive_extraction_command(self):
        return "sudo mkdir -p /opt/snips/asr && sudo tar xf " \
            + self.asr_archive_path \
            + " -C /opt/snips/asr --strip-components 1"

    def extract_asr_archive(self):
        extract_asr_archive_cmd = self.generate_asr_archive_extraction_command()
        execute_root_command(extract_asr_archive_cmd)

    def update_snips_command(self):
        if not cmd_exists("snips"):
            return
        else:
            self.write_snips_unit_file()
            return

    def get_current_snips_command(self): # Deprecated
        return get_command_output(['tail','-n','1',self.snips_command_path]).strip()

    def write_snips_unit_file(self):
        updated_snips_command = self.generate_updated_snips_command()
        contents = Systemd.get_template(SNIPS_SERVICE_NAME)
        if contents is None:
            return
        contents = contents.replace("{{SNIPS_PATH}}", updated_snips_command)
        Systemd.write_systemd_file(
            SNIPS_SERVICE_NAME, self.default_user, contents)

    def generate_updated_snips_command(self):
        return "snips -a"

    def get_template(self):
        if cmd_exists('snips'):
            return get_command_output(['head', '-n', '-1', self.snips_command_path]).rstrip()
        else:
            return None