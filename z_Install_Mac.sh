 #!/bin/bash

venv_path="./venv-ortho"

#Get path to the Ortho4XP directory
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)


# Function to install Rosetta
install_rosetta() {
  if /usr/bin/pgrep oahd >/dev/null 2>&1; then
    echo "Rosetta is already installed."
  else
    echo "Installing Rosetta (required for DDS conversion) ..."
      softwareupdate --install-rosetta --agree-to-license

    if [[ $? -eq 0 ]]; then
      echo "Rosetta has been successfully installed."
    else
      echo "Failed to install Rosetta."
    fi
  fi
}

check_python_tk() {
  echo ""
  echo "Checking for Tkinter..."
  python$py_ver -c "import tkinter" &>/dev/null
  if [ $? -eq 0 ]; then
    echo "Tkinter is installed."
  else
    echo ""
    echo "Tkinter is not installed!"
    echo ""
    echo "Install Tkinter: brew install python-tk@3.12"
    exit 1
  fi
}

check_python() {
  echo ""
  echo "Checking for Python $py_ver..."
  if command -v python$py_ver &>/dev/null; then
    echo "Python $py_ver is installed."
    check_python_tk
  else
    echo ""
    echo "Python $py_ver is not installed!"
    echo ""
    echo "Install Python $py_ver from www.python.org"
    echo ""
    echo "Alternatively, install python@$py_ver and python-tk@$py_ver from Homebrew"
    echo ""
    exit 1
  fi
}

#Change to the Ortho4XP directory
cd "$(dirname "${BASH_SOURCE[0]}")"

install_macOS_recent(){
  
  check_python
  python$py_ver -m venv $venv_path
  source $venv_path/bin/activate
  
  pip install -r requirements.txt
  
  }

install_macOS_older(){

 check_python
 python$py_ver -m venv $venv_path
 source $venv_path/bin/activate

 pip install numpy==1.26.4
 pip install pillow==10.4.0
 pip install shapely==2.0.6
 pip install rtree==1.3.0
 pip install pyproj==3.6.1
 pip install rasterio==1.4.1
 pip install requests==2.32.3
 }

# Get the macOS version
macos_version=$(sw_vers -productVersion)

# Extract the major version
major_version=$(echo $macos_version | cut -d '.' -f 1)


# Main script execution
echo ""

if [[ "$(uname -m)" == "arm64" ]]; then
   install_rosetta
fi

echo "Approving the use of executables from $SCRIPT_DIR/Utils/mac directory"
xattr -dr com.apple.quarantine ./Utils/mac/*

# Remove existing venv
if [ -d $venv_path ]; then
  echo "Removing existing venv: $venv_path"
  rm -rf $venv_path
fi

# Create an if statement based on the major version
if [ "$major_version" -lt 14 ]; then
    echo "Your macOS version is less than 14.x.x"
    py_ver="3.12"
    install_macOS_older
else
    echo "Your macOS version is 14.x.x or higher"
    py_ver="3.12"
    install_macOS_recent
fi

if [ -d "$venv_path/bin" ]; then
  echo "$(python --version) venv has been created in the $venv_path directory"
  echo "Installed packages:"
  pip list
fi

# Make "z_Start_O4XP.sh" an executable file
chmod +x ./z_Start_O4XP.sh
xattr -dr com.apple.quarantine ./z_Start_O4XP.sh

echo " "
echo "Use $SCRIPT_DIR/z_Start_O4XP.sh to start O4XP"
echo " "
