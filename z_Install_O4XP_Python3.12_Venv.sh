#! /bin/bash

#Uncomment the next line for a complete install on macOS

#brew install gdal python python-tk proj spatialindex p7zip

#On Linux - install system packages as per Install_Instructions.txt

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

venv_path=$SCRIPT_DIR/venv-ortho

# 1. Create a Python 3.12 virtual environment

python3.12 -m venv --system-site-packages $venv_path

# 2. Activate Python venv

source $venv_path/bin/activate

# 3. Install packages with pip

cd $SCRIPT_DIR

pip install -I -r requirements.txt
pip install build

# 4. Download scikit-fmm's "meson" branch, compile and install it

git clone -b meson https://github.com/scikit-fmm/scikit-fmm.git $venv_path/scikit-fmm

python -m build $venv_path/scikit-fmm

pip install $venv_path/scikit-fmm

# 6. DONE

echo " "

if [ -d "$venv_path/bin" ]; then
  echo "$(python --version) virtual environment has been created in $venv_path directory"
fi

echo " "
echo "Installed packages:"
echo " "
pip list
echo " "
echo "GDAL version:"
gdal-config --version
echo " "
echo " "
echo "Use $SCRIPT_DIR/z_Start_O4XP_PythonVenv.sh to start O4XP"
echo " "
