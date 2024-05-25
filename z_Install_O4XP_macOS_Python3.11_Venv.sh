#! /bin/bash

#Uncomment the next line for a complete install on macOS

#brew install gdal python@3.11 python-tk@3.11 proj spatialindex p7zip

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

venv_path=$SCRIPT_DIR/venv-ortho

# 1. Create a Python virtual environment

python3.11 -m venv $venv_path

# 2. Activate Python venv

source $venv_path/bin/activate

# 3. Install packages with pip

cd $SCRIPT_DIR
pip install -r requirements.txt
pip install gdal=="$(gdal-config --version).*"
pip install scikit-fmm

# 6. DONE

echo " "

if [ -d "$venv_path/bin" ]; then
  echo "Python virtual environment has been installed in $venv_path directory"
fi

echo " "
echo "Python version:"
python --version
echo " "
echo "Installed packages:"
pip list
echo " "
echo "GDAL version:"
gdal-config --version
echo " "
echo " "
echo "Use $SCRIPT_DIR/z_Start_O4XP_PythonVenv.sh to start O4XP"
echo " "
echo " "