import os

import pytest

from libretranslate.security import SuspiciousFileOperationError, path_traversal_check


def test_safe_path(tmp_path):
    safe = path_traversal_check(str(tmp_path / "file.txt"), str(tmp_path))
    assert safe == os.path.abspath(str(tmp_path / "file.txt"))


def test_nested_safe_path(tmp_path):
    nested = tmp_path / "sub" / "dir" / "file.txt"
    safe = path_traversal_check(str(nested), str(tmp_path))
    assert safe == os.path.abspath(str(nested))


def test_traversal_is_rejected(tmp_path):
    with pytest.raises(SuspiciousFileOperationError):
        path_traversal_check(str(tmp_path / ".." / "secret.txt"), str(tmp_path))


def test_absolute_path_outside_is_rejected(tmp_path):
    with pytest.raises(SuspiciousFileOperationError):
        path_traversal_check("/etc/passwd", str(tmp_path))


def test_sibling_prefix_dir_is_rejected(tmp_path):
    # "safe" and "safe-evil" share a string prefix but are different directories
    safe_dir = tmp_path / "safe"
    evil_dir = tmp_path / "safe-evil"
    safe_dir.mkdir()
    evil_dir.mkdir()

    with pytest.raises(SuspiciousFileOperationError):
        path_traversal_check(str(evil_dir / "file.txt"), str(safe_dir))
