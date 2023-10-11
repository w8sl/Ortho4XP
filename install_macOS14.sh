# Install dependencies

brew install gdal python proj spatialindex p7zip python-tk

# Install other dependencies

pip3 install -r ./requirements_mac.txt

# Rename files for macOS 14 compatibility

python3 ./macOS14_fix.py
