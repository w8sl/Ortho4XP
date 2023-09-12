# Install XCode Command Line Tools(open terminal, enter the command: xcode-select --install   →hit return)
# Install Homebrew (open terminal, enter the command: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"  →hit return.)
# Verify integrity (enter the command: brew doctor  →hit return), read terminal output, follow recommendations if neccesary.
# Copy paste line 8,12 and 16 into terminal or run install_mac.sh as a script.

# Install dependencies

brew install gdal python proj spatialindex p7zip python-tk

# Install pyproj

pip3 install pyproj

# Install other dependencies

pip3 install numpy shapely rtree pillow requests
