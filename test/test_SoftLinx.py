import sys
import os
import pytest

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../src"))
)
import SoftLinx


class TestSoftLinx:
    def test_temp(self):
        assert True