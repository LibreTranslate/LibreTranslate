import os
import time

from libretranslate.remove_translated_files import remove_translated_files


def test_removes_old_files(tmp_path):
    old_file = tmp_path / "old.txt"
    old_file.write_text("stale")
    old_mtime = time.time() - 3600
    os.utime(old_file, (old_mtime, old_mtime))

    remove_translated_files(str(tmp_path))

    assert not old_file.exists()


def test_keeps_recent_files(tmp_path):
    new_file = tmp_path / "new.txt"
    new_file.write_text("fresh")

    remove_translated_files(str(tmp_path))

    assert new_file.exists()


def test_ignores_directories(tmp_path):
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    old_mtime = time.time() - 3600
    os.utime(subdir, (old_mtime, old_mtime))

    remove_translated_files(str(tmp_path))

    assert subdir.exists()
