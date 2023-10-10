# Install dependencies

brew install gdal python proj spatialindex p7zip python-tk

# Install other dependencies

pip3 install -r ./requirements_mac.txt

# Rename files for OSX14 compatibility

python3 ./OSX14_fix.py
