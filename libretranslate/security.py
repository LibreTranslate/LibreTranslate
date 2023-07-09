import os


class SuspiciousFileOperationError(Exception):
    pass


def path_traversal_check(unsafe_path, known_safe_path):
    known_safe_path = os.path.abspath(known_safe_path)
    unsafe_path = os.path.abspath(unsafe_path)

    if (os.path.commonprefix([known_safe_path, unsafe_path]) != known_safe_path):
        raise SuspiciousFileOperationError(f"{unsafe_path} is not safe")

    # Passes the check
    return unsafe_path
