# Install XCode Command Line Tools(open terminal, enter the command: xcode-select --install   →hit return)
# Install Homebrew (open terminal, enter the command: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"  →hit return.)
# Verify integrity (enter the command: brew doctor  →hit return), read terminal output, follow recommendations if neccesary.
# Copy paste line 8 and 12 into terminal or run install_mac.sh as a script.

# Install dependencies

brew install gdal python proj spatialindex p7zip python-tk

# Install other dependencies
# Go to the Ortho4XP folder:
# cd /path/to/Ortho4XP
# or write in terminal: cd   →drag and drop Ortho4XP folder   →hit return

pip3 install -r requirements_mac.txt
