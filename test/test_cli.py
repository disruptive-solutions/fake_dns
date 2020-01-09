import pytest
from os import getpid
from os import kill
from time import sleep
import threading

from click.testing import CliRunner

from delirium.apps import dns

runner = CliRunner()

def test_cli_help():
    response = runner.invoke(dns, ['--help'])
    assert 'Show this message and exit.' in response.output

def test_cli_bad_arg():
    response = runner.invoke(dns, ['oiuytrewqasdfghjkmnbvc'])
    assert 'Got unexpected extra argument' in response.output

def test_cli_no_args():
    pid = getpid()

    def trigger_signal():
        while len(mock_print.mock_calls) < 1:
            time.sleep(0.2)
        os.kill(pid, signal.SIGINT)

    thread = threading.Thread(target=trigger_signal)
    #thread.daemon = True
    thread.start()
    assert thread.is_alive() == True
