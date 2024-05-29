#! /bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

venv_path=$SCRIPT_DIR/venv-ortho

if [ ! -f "$SCRIPT_DIR/Ortho4XP.py" ]; then
  echo " "
  echo "Error: file Ortho4XP.py not found!"
  echo " "
  echo "Place z_Install_O4XP_Python3.12_Venv.sh in the main O4XP direcory !"
  echo " "
  exit 1 
fi

# Semi-automated installation for macOS

if [[ "$OSTYPE" == "darwin"* ]]; then
   echo "macOS"

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

package_exists python@3.12
string="$(which python3.12)"
 if [[ $string != *"homebrew"* ]]; then
   echo " "
   echo "Python installed via Homebrew is required. Remove alternative Python from PATH!"
   echo "See included Install_Instructtions.txt for more information"
   echo " "
   exit 1
 fi
package_exists gdal
package_exists python-tk@3.12
package_exists proj
package_exists spatialindex
package_exists p7zip

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
   echo "LINUX"
   
   if ! [ -x "$(command -v python3.12)" ]; then
    echo " "
    echo "Python 3.12 is not installed. Aborting! "
    echo " "
    exit 1
   fi
   if ! [ -x "$(command -v gdalwarp)" ]; then
    echo " "
    echo "Install system packages required by Ortho4XP as per included Install_Instructions.txt!"
    echo " "
    exit 1
   fi

else 
  echo "Unsupported system!"
  exit 1
fi

# Remove existing venv

if [ -d $venv_path ]; then
  echo "Removing existing venv: $venv_path"
  rm -rf $venv_path
fi

# Create a Python 3.12 virtual environment

python3.12 -m venv --system-site-packages $venv_path

# Activate Python venv

source $venv_path/bin/activate

# Install packages with pip

cd $SCRIPT_DIR

pip install -I -r requirements.txt
pip install build

# Download scikit-fmm's "meson" branch, compile and install it

git clone https://github.com/scikit-fmm/scikit-fmm.git $venv_path/scikit-fmm

python -m build $venv_path/scikit-fmm

pip install $venv_path/scikit-fmm

# DONE

echo " "

if [ -d "$venv_path/bin" ]; then
  echo "$(python --version) virtual environment has been created in $venv_path directory"
fi

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
