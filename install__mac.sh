# Install dependencies

brew install gdal python proj spatialindex p7zip python-tk

# Install other dependencies

pip3 install -r ./requirements_mac.txt

# Remove .app extension

python3 ./Filename_fix_macOS.py
