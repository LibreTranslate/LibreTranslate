from app.init import boot
from argostranslate import package


def test_boot_argos():
    """Test Argos translate models initialization"""
    boot()

    assert len(package.get_installed_packages()) > 2
