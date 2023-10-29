# Install dependencies

brew install gdal python proj spatialindex p7zip python-tk

# Install other dependencies

pip3 install -r ./requirements.txt

# Remove .app extension. This step is necessary on the latest version of macOS

python3 ./Filename_fix_macOS.py
