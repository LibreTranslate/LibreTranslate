# Contributing

If you want to make changes to the code, you can build from source, and run the API.

## Build Dependencies

* cmake

### Debian / Ubuntu

```sh
sudo apt-get install cmake
```

### Fedora / RHEL

```sh
sudo dnf install cmake
```

## FAQ

### Externally Managed Environment

Some users may encounter the following error while installing packages:

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    …
```

This occurs when your operating system depends on and manages Python for core functionality. In this case, you should install and setup venv (virtual environments) to manage project dependencies.

This prevents pip packages from being installed system-wide. This way, there are no risks of pip packages conflicting between multiple projects or the operating system.

References:
* [Python venv documentation](https://docs.python.org/library/venv.html) 
