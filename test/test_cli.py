import pytest
from time import sleep
import threading

from click.testing import CliRunner

from delirium.apps import dns


runner = CliRunner()

def test_cli_help():
    response = runner.invoke(dns, ['--help'])
    assert 'Show this message and exit.' in response.output

def test_cli_bad_switch():
    response = runner.invoke(dns, ['oiuytrew'])
    assert 'Got unexpected extra argument' in response.output

def test_cli_no_args():

    def run_clirunner():
        response = runner.invoke(dns,)

    thread = threading.Thread(target=run_clirunner)
    thread.daemon = True
    thread.start()
    assert thread.is_alive() == True

@pytest.mark.parametrize('switch, parameter',[('-l', '127.0.0.1'),
                                    ('--laddr', '127.0.0.1'),
                                    ('-p', '7357'),
                                    ('--lport', '7357'),
                                    ('-t', 500),
                                    ('--time', 500),
                                    ('-a', '10.10.10.1-10.10.10.10'),
                                    ('--addr-pool', '10.10.10.1-10.10.10.10'),
                                    ('-d', ':memory:'),
                                    ('--db-path', ':memory:')])

def test_cli_switches(switch, parameter):
    #  Test that switch works with parameter
    def run_clirunner():
        response = runner.invoke(dns,[switch,parameter])

    thread = threading.Thread(target=run_clirunner)
    thread.daemon = True
    thread.start()
    assert thread.is_alive() == True

    #  Test that switch doesn't work without parameter
    def run_clirunner():
        response = runner.invoke(dns,[switch])

    thread = threading.Thread(target=run_clirunner)
    thread.daemon = True
    thread.start()
    assert thread.is_alive() == False
