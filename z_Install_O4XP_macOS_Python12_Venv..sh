#! /bin/bash

brew install gdal python python-tk proj spatialindex p7zip

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

cd $SCRIPT_DIR

# 1. Create a Python virtual environment

python3 -m venv $SCRIPT_DIR/venv-ortho

# 2. Activate Python venv

source $SCRIPT_DIR/venv-ortho/bin/activate

# 3. Install packages with pip

pip install -r requirements.txt
pip install gdal

# 4. Download scikit-fmm's "meson" branch, compile and install it

git clone -b meson https://github.com/scikit-fmm/scikit-fmm.git $SCRIPT_DIR/venv-ortho/scikit-fmm

python -m build $SCRIPT_DIR/venv-ortho/scikit-fmm

pip install $SCRIPT_DIR/venv-ortho/scikit-fmm

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
