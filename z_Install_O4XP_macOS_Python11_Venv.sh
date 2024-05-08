#! /bin/bash

brew install gdal python@3.11 python-tk@3.11 proj spatialindex p7zip

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

cd $SCRIPT_DIR

# 1. Create a Python virtual environment

python3.11 -m venv $SCRIPT_DIR/venv-ortho

# 2. Activate Python venv

source $SCRIPT_DIR/venv-ortho/bin/activate

# 3. Install packages with pip

pip install -r requirements.txt
pip install gdal
pip install scikit-fmm

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
