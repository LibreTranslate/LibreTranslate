import pytest
from app.init import boot
from argostranslate import package

def test_boot_argos():
    """Test Argos translate models initialization"""
    boot()

    print(package.get_installed_packages())
    assert len(package.get_installed_packages()) > 2
    # Check length models?
    # assert 0.80 < scores['precision'] < 0.95

