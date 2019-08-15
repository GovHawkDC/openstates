# local dev

## requirements

Assumes following deps:

- Python 3.x
- Pip (for Python 3.x)
- Virtualenv

### macos

To install on macOS, the following worked for me
(assuming homebrew installed):

```shell
# Python 3.x and pip
brew install python

# Verify python and pip versions
python3 --version
pip3 --version

# Install virtualenv
pip3 install virtualenv
```

### via apt

```shell
# Pip, if not already installed
sudo apt install python3-pip

# Verify python and pip versions
python3 --version
pip3 --version

# Install virtualenv
pip3 install virtualenv
```

Note: you may have to re-source `~/.profile` depending on your `$PATH`, if `virtualenv`
can't be found.

### resources

- https://docs.python-guide.org/dev/virtualenvs/

## dev

### start

```shell
# Assuming (but not required) root of repo
source scripts/local-up
```

### stop

```shell
# Assuming (but not required) root of repo
source scripts/local-down
```

### remove

To remove venv, assuming having used steps above:

```shell
# Assuming root of repo
rm -rf venv
```

## notes

By default, `pupa` is fetched remotely; however, for
local testing, can run the following (assuming from
within venv):

```shell
pip3 uninstall pupa -y
pip3 install local/path/to/pupa
```