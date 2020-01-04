from delirium.apps import dns
from click.testing import CliRunner
import pytest
import mock

"""
# gets hung up
def test_apps_loaded():
    testrun = CliRunner()
    result = testrun.invoke(dns)
    assert result.exit_code == 0
"""
