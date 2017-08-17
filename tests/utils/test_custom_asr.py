from unittest import TestCase
from snipsskills.utils.custom_asr import CustomASR


class BaseTest(TestCase):
    def setUp(self):
        self.customASR = CustomASR(True, '/home/pi/project/asr.tar.gz')

class TestUnixCommands(BaseTest):
    def test_generates_asr_extraction_command(self):
        generated_cmd = self.customASR.generate_asr_archive_extraction_command()
        self.assertEqual(generated_cmd,
                         'sudo mkdir -p /opt/snips/asr && sudo tar xf /home/pi/project/asr.tar.gz -C /opt/snips/asr --strip-components 1')



