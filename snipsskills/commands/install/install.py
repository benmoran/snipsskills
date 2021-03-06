# -*-: coding utf-8 -*-

import os

from ..base import Base
from ...utils.os_helpers import file_exists
from ...utils.os_helpers import is_raspi_os
from ...utils.snipsfile import Snipsfile

from ..assistant.fetch import AssistantFetcher
from ..assistant.load import AssistantLoader
from ..setup.microphone import MicrophoneInstaller
from ..setup.systemd.bluetooth import SystemdBluetooth
from ..setup.systemd.snips import SystemdSnips
from ..setup.systemd.snipsskills import SystemdSnipsSkills
from .skills import SkillsInstaller, SkillsInstallerWarning
from .bluetooth import BluetoothInstaller

from ... import DEFAULT_SNIPSFILE_PATH

from snipsskillscore import pretty_printer as pp

class GlobalInstallerException(Exception):
    pass

class GlobalInstallerWarning(Exception):
    pass


class GlobalInstaller(Base):
    
    def run(self):
        pp.silent = self.options['--silent']
        try:
            GlobalInstaller.install(self.options['--snipsfile'], skip_bluetooth=self.options['--skip-bluetooth'], skip_systemd=self.options['--skip-systemd'], email=self.options['--email'], password=self.options['--password'], force_download=self.options['--force-download'])
        except GlobalInstallerWarning as e:
            pp.pwarning(str(e))
        except Exception as e:
            pp.perror(str(e))


    @staticmethod
    def install(snipsfile_path=None, skip_bluetooth=False, skip_systemd=False, email=None, password=None, force_download=False):
        snipsfile_path = snipsfile_path or DEFAULT_SNIPSFILE_PATH
        if snipsfile_path is not None and not file_exists(snipsfile_path):
            raise GlobalInstallerException("Error running installer: Snipsfile not found")
        snipsfile = Snipsfile(snipsfile_path)
        GlobalInstaller.install_from_snipsfile(snipsfile, skip_bluetooth=skip_bluetooth, skip_systemd=skip_systemd, email=email, password=password, force_download=force_download)


    @staticmethod
    def install_from_snipsfile(snipsfile, skip_bluetooth=False, skip_systemd=False, email=None, password=None, force_download=False):
        pp.pheader("Running Snips Skills installer")

        if snipsfile is None:
            raise GlobalInstallerException("Error running installer: no Snipsfile provided")

        try:
            AssistantFetcher.fetch(email=email, password=password, force_download=force_download)
            AssistantLoader.load()
        except Exception as e:
            pp.pwarning(str(e))

        try:
            SkillsInstaller.install(force_download=force_download)
        except Exception as e:
            pp.pwarning(str(e))
        
        try:
            MicrophoneInstaller.install()
        except Exception as e:
            pp.pwarning(str(e))

        if not skip_bluetooth and is_raspi_os():
            try:
                BluetoothInstaller.install(force_download=force_download)
            except Exception as e:
                pp.pwarning(str(e))

        if not skip_systemd and is_raspi_os():
            try:
                SystemdBluetooth.setup()
            except Exception as e:
                pp.pwarning(str(e))
            try:
                SystemdSnips.setup()
            except Exception as e:
                pp.pwarning(str(e))
            try:
                SystemdSnipsSkills.setup()
            except Exception as e:
                pp.pwarning(str(e))

        if not skip_systemd:
            pp.pheadersuccess("Snips Skills installer complete! You can now reboot your device, or manually run 'snipsskills run' to start the Snips Skills server")
        else:
            pp.pheadersuccess("Snips Skills installer complete! Now run 'snipsskills run' to start the Snips Skills server.")
