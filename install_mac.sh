# Install XCode Command Line Tools(enter the command: xcode-select --install   in the terminal)
# Install Homebrew (download and run .pkg installer from https://github.com/Homebrew/brew/releases)
# Verify integrity (enter the command: brew doctor  in the terminal), follow instructions if neccesary.

# Install dependencies
brew install gdal spatialindex p7zip python-tk

# (python, proj, numpy should be already installed as a gdal dependencies. Verify with command: brew list --versions)

# Install pyproj
pip3 install pyproj

# Install other dependencies
pip3 install shapely rtree pillow requests
