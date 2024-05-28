#! /bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

venv_path=$SCRIPT_DIR/venv-ortho

if [ ! -f "$SCRIPT_DIR/Ortho4XP.py" ]; then
  echo " "
  echo "Error: file Ortho4XP.py not found!"
  echo " "
  echo "Place z_Install_O4XP_macOS_Python3.11_Venv.sh in the main O4XP direcory !"
  echo " "
  exit 1 
fi

if [[ "$OSTYPE" != "darwin"* ]]; then
   echo "This script is for macOS only!"
   exit 1
fi

# Semi-automated install for macOS
if ! [ -x "$(command -v brew)" ]; then
   echo " "
   echo "Homebrew is required but is not installed or is not in PATH!"
   echo "Install Homebrew. Read the terminal messages carefully and follow the PATH setting instructions!"  
   echo "See included Install_Instructions.txt and: https://brew.sh"
   echo " "
   exit 1
fi

package_exists(){
    package=$1
    if brew list | grep $package; then
        echo "$package found"
    else
        echo "$package not found"
        echo "Installing $package"
        brew install $package
    fi
}

package_exists python@3.11
string="$(which python3.11)"
if [[ $string != *"homebrew"* ]]; then
  echo " "
  echo "Python installed via Homebrew is required. Remove alternative Python from PATH!"
  echo "See included Install_Instructtions.txt for more information"
  echo " "
  exit 1
fi
package_exists gdal
package_exists python-tk@3.11
package_exists proj
package_exists spatialindex
package_exists p7zip

# Remove existing venv

if [ -d $venv_path ]; then
  echo "Removing existing venv: $venv_path"
  rm -rf $venv_path
fi

# Create a Python virtual environment

python3.11 -m venv $venv_path

# Activate Python venv

source $venv_path/bin/activate

# Install packages with pip

cd $SCRIPT_DIR
pip install -r requirements.txt
pip install gdal=="$(gdal-config --version).*"
pip install scikit-fmm

# DONE

echo " "

if [ -d "$venv_path/bin" ]; then
  echo "$(python --version) virtual environment has been created in $venv_path directory"
fi

echo " "
echo "Installed packages:"
echo " "
pip list
echo " "
echo "GDAL version: $(gdal-config --version)"
echo " "
echo "Use $SCRIPT_DIR/z_Start_O4XP_PythonVenv.sh to start O4XP"
echo " "
