import mock
from unittest import TestCase
from snipsskills.utils.os_helpers import cmd_exists, which
from snipsskills.utils.custom_asr import CustomASR



class BaseTest(TestCase):
    def setUp(self):
        pass

class TestUnixCommandExists(BaseTest):
    @mock.patch('snipsskills.utils.os_helpers.subprocess')
    def test_command_exists(self, mock_subprocess):
        mock_subprocess.call.return_value = 1
        result_for_incorrect_command = cmd_exists("snip")

        mock_subprocess.call.assert_called_with("type snip",  # Assert the subprocess.call method was called with correct parameters
                                                shell=True,
                                                stdout=mock_subprocess.PIPE,
                                                stderr=mock_subprocess.PIPE)

        self.assertFalse(result_for_incorrect_command)

        mock_subprocess.call.return_value = 0
        result_for_correct_command = cmd_exists("snips")
        self.assertTrue(result_for_correct_command)

    @mock.patch('snipsskills.utils.os_helpers.subprocess')
    def test_command_which(self, mock_subprocess):
        mock_subprocess.check_output.return_value = "/usr/bin/snips"

        result_for_correct_command = which('snips')

        mock_subprocess.check_output.assert_called_with(['which', 'snips'])
        self.assertEqual(result_for_correct_command, "/usr/bin/snips")



