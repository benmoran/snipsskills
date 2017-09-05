# -*-: coding utf-8 -*-
""" Helper methods for OS related tasks. """

from getpass import getpass
import os
import shlex
import subprocess
import urllib2
from getpass import getpass, getuser


def cmd_exists(cmd):
    """ Check if a command exists.

    :param cmd: the command to look for.
    :return: true if the command exists, false otherwise.
    """
    return subprocess.call("type " + cmd, shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


def is_raspi_os():
    """ Check if the current system is Raspberry.

    :return: true if the current system is Raspberry.
    """
    return 'arm' in " ".join(os.uname())


def execute_root_command(command):
    os.system(command)


def create_dir(dir_name):
    """ Create directory in the current working directory, if it does
        not exist already.

    :param dir_name: the name of the directory.
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def execute_command(command, silent=False):
    """ Execute a shell command.

    :param command: the command to execute.
    :param silent: if True, do not output anything to terminal.
    """
    if silent:
        stdout = open(os.devnull, 'w')
    else:
        stdout = subprocess.PIPE
    subprocess.Popen(command.split(), stdout=stdout).communicate()


def get_command_output(command_array):
    return subprocess.check_output(command_array)


def pipe_commands(first_command, second_command, silent):
    """ Execute piped commands: `first_command | second_command`.

    :param first_command: the first command to execute.
    :param second_command: the second command to execute.
    """
    process1 = subprocess.Popen(first_command.split(), stdout=subprocess.PIPE)
    if silent:
        FNULL = open(os.devnull, 'w')
        process2 = subprocess.Popen(
            second_command.split(), stdin=process1.stdout, stdout=FNULL)
    else:
        process2 = subprocess.Popen(
            second_command.split(), stdin=process1.stdout)
    process1.stdout.close()
    process2.communicate()


def remove_file(file_path):
    """ Delete a file.

    :param file_path: the path to the file.
    """
    try:
        os.remove(file_path)
    except OSError:
        pass


def download_file(url, output_file):
    """ Download a file.

    :param url: the remote location of the file.
    :param output_file: the file to write to.
    """
    downloaded_file = urllib2.urlopen(url)
    with open(output_file, 'wb') as output:
        output.write(downloaded_file.read())


def ask_yes_no(question):
    """ Ask a yes/no question in the prompt.

    :param question: the question to ask.
    :return: true if the user answered yes (or empty), false otherwise
    """
    answer = raw_input("{} [Y/n] ".format(question))
    if answer is not None and answer.strip() != "" and answer.lower() != "y":
        return False
    return True


def ask_for_input(question, default_value=None):
    if default_value and len(default_value) > 0:
        answer = raw_input("{} [{}]".format(question, default_value))
        if len(answer) == 0:
            answer = default_value
    else:
        answer = raw_input(question)

    if answer is not None and answer.strip() != "":
        return answer
    else:
        return None


def ask_for_password(question):
    answer = getpass("{} ".format(question))
    if answer is not None and answer.strip() != "":
        return answer
    else:
        return None


def which(command):
    """ Get full path for an executable.

    :param command: the executable command, e.g. 'node'.
    :return: the full path for the command, e.g. '/usr/local/bin/node'.
    """
    try:
        return subprocess.check_output(
            ['which', command]).strip()
    except subprocess.CalledProcessError:
        return None


def reboot():
    """ Reboot the device."""
    execute_command("sudo reboot")


def get_os_name():
    os_release = subprocess.check_output(['cat', '/etc/os-release'])
    for line in os_release.splitlines():
        if line.startswith("PRETTY_NAME="):
            split = line.split("=")
            if len(split) > 1:
                os_version = split[1]
                return os_version.replace("\"", "")
    return None


def get_revision():
    process1 = subprocess.Popen('cat /proc/cpuinfo'.split(), stdout=subprocess.PIPE)
    process2 = subprocess.Popen('grep Revision'.split(), stdin=process1.stdout, stdout=subprocess.PIPE)
    process3 = subprocess.Popen(['awk', '{print $3}'], stdin=process2.stdout)
    process1.stdout.close()
    process2.stdout.close()
    return process3.communicate()


def get_sysinfo():
    return {
        "os_name": get_os_name()
    }


def get_user_email_git():
    if cmd_exists("git"):
        command = "git config user.email"
        output = get_command_output(command.split())
        if output is not None and len(output) > 0:
            return output.strip()
        return None
    else:
        return None


def get_default_user():
    return getuser()
