#! /bin/bash

if ! [ -x "$(command -v brew)" ]; then
  echo 'Homebrew is required but is not installed or is not in PATH! See: https://brew.sh' >&2
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
package_exists gdal
package_exists python-tk@3.11
package_exists proj
package_exists spatialindex
package_exists p7zip

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

venv_path=$SCRIPT_DIR/venv-ortho

if [ -d $venv_path ]; then
  echo "Removing existing venv: $venv_path"
  rm -rf $venv_path
fi

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
