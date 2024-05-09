#! /bin/bash

#Uncomment the nest line for complete install

#brew install gdal python python-tk proj spatialindex p7zip

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

venv_path=$SCRIPT_DIR/venv-ortho

# 1. Create a Python virtual environment

python3 -m venv $venv_path

# 2. Activate Python venv

source $venv_path/bin/activate

# 3. Install packages with pip

cd $SCRIPT_DIR

pip install -r requirements.txt
pip install gdal
pip install build

# 4. Download scikit-fmm's "meson" branch, compile and install it

git clone -b meson https://github.com/scikit-fmm/scikit-fmm.git $venv_path/scikit-fmm

python -m build $venv_path/scikit-fmm

pip install $venv_path/scikit-fmm

# 6. DONE

echo " "
echo "Preparation complete!"
echo " "
echo "Use $SCRIPT_DIR/z_Start_O4XP_Venv_Mac.sh to start O4XP"
echo " "
echo " "

# Function: Pause
function pause(){
   read -p "$*"
}

pause "Press enter to continue... "
