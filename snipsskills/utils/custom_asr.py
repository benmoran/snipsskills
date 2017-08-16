# -*-: coding utf-8 -*-
""" Custom ASR installer """

import getpass
import os
import subprocess


from .os_helpers import execute_command, cmd_exists


class CustomASR:
    """ Systemd utilities. """

    @staticmethod
    def setup(asr_archive_path):
        """
        To setup the ASR, we go through the following steps.
        - Download the archive that contains the custom ASR model (optional)
        - Extract the archive
        - Move the ASR model to an appropriate location
        - Change the `snips` script to add ASR tags
        """

        CustomASR.extract_asr_archive(asr_archive_path)
        CustomASR.update_snips_command()


    @staticmethod
    def get_snipsskills_params(asr_archive_path):
        try:
            snips_command_path = subprocess.check_output(
                ['which', 'snips']).strip()
        except subprocess.CalledProcessError:
            snips_command_path = None

        if snips_command_path is None or len(snips_command_path.strip()) == 0:
            snips_command_path = raw_input("Path to the snips binary: ")

        return snips_command_path

    @staticmethod
    def extract_asr_archive(asr_archive_path):
        os.system(
            "sudo mkdir -p /opt/snips/asr && sudo tar xf "
            + asr_archive_path
            + " -C /opt/snips/asr --strip-components 1")

    @staticmethod
    def update_snips_command():
        if not cmd_exists("snips"):
            return
        else:
            snips_command_file_path = "/usr/bin/snips"
            cmd = CustomASR.get_snips_command_for_custom_ASR(snips_command_file_path)
            CustomASR.write_command_to_snips_command_file(cmd, snips_command_file_path)
            return

    @staticmethod
    def write_command_to_snips_command_file(cmd, snips_command_file_path):
        updated_snips_command_line = CustomASR.get_snips_command(snips_command_file_path)

        full_command = CustomASR.get_template(snips_command_file_path) + "\n" + updated_snips_command_line

        os.system("sudo cp {} {}.backup").format(snips_command_file_path)
        os.system("sudo echo \"{}\" > {}".format(full_command, snips_command_file_path))
        os.system("sudo chmod a+rwx {}".format(snips_command_file_path))
    
    @staticmethod
    def get_snips_command(snips_command_path):
        ASR_ARGUMENTS = "-v /opt/snips/asr:/usr/share/snips/asr "

        current_snips_command = subprocess.call(['tail','-n','1',snips_command_path])
        if 'asr' in current_snips_command.lower():
            return current_snips_command
        else:
            cmd = current_snips_command
            separation_string = "snipsdocker/platform"
            index_of_separation = current_snips_command.find(separation_string)
            current_snips_command = cmd[:index_of_separation] + ASR_ARGUMENTS + cmd[index_of_separation:]
            return current_snips_command

    @staticmethod
    def get_template(snips_command_path):
        if cmd_exists('snips'):
            return subprocess.call(['head', '-n', '-1', snips_command_path])
        else:
            return None