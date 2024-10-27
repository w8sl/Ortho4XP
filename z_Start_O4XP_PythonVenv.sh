#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"


venv_path="./venv-ortho"

if [ ! -f ./Ortho4XP.py ]; then
  echo " "
  echo "Error: file Ortho4XP.py not found!"
  echo " "
  echo "Place z_Start_O4XP_PythonVenv.sh in the main O4XP direcory !"
  echo " "
  exit 1 
fi

if [ ! -d $venv_path ]; then
  echo " "
  echo "Virtual environment not available. Install Python venv!"
  echo " "
  exit 1 
fi


source $venv_path/bin/activate

python Ortho4XP.py
