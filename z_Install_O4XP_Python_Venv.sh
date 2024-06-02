#! /bin/bash

py_ver="3.12"

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

venv_path=$SCRIPT_DIR/venv-ortho

if [ ! -f "$SCRIPT_DIR/Ortho4XP.py" ]; then
  echo " "
  echo "Error !"
  echo " "
  echo "Place z_Install_O4XP_Python_Venv.sh in the main O4XP direcory !"
  echo " "
  exit 1 
fi

# Semi-automated, guided installation for macOS

if [[ "$OSTYPE" == "darwin"* ]]; then
   echo "macOS"

   if [[ "$(uname -m)" == "arm64" ]]; then
     brew_path="/opt/homebrew/bin/brew"
   else
     brew_path="/usr/local/bin/brew"
   fi
 if ! [ -x "$(command -v brew)" ]; then
   echo " "
   echo "Homebrew is required but is not installed or is not in PATH!"
   echo " "
   echo "Install Homebrew. See: https://brew.sh"
   echo " "
   echo "Add Homebrew to the PATH by running this command and restart the terminal:"
   echo " "
   echo "echo 'eval \"\$($brew_path shellenv)\"' >> /Users/$USER/.zprofile"
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

 if ! [ -x "$(command -v python$py_ver)" ]; then
   echo "Python $py_ver not found! Installing ..."
   brew install python@$py_ver
 fi 

 if [[ "$(which python$py_ver)" != *"homebrew"* ]]; then
   echo " "
   echo "Python installed via Homebrew is required !" 
   echo "Remove the PATH for Python in the hidden file .zprofile in your user directory !"
   echo " "
   echo "Contents of /Users/$USER/.zprofile: "
   echo " "
   echo "$(</Users/$USER/.zprofile )"
   echo " "
   echo "But it should be: "
   echo " "
   echo "eval \"\$($brew_path shellenv)\""
   echo " "
   exit 1
 fi

if ! [ -x "$(command -v gdalwarp)" ]; then
   echo "GDAL not found! Installing..."
   brew install gdal
fi

if ! [ -x "$(command -v 7z)" ]; then
   echo "p7zip not found! Installing..."
   brew install p7zip
fi

package_exists python-tk@$py_ver
package_exists proj
package_exists spatialindex

# Semi-automated, guided installation for Linux

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then

 
if type lsb_release >/dev/null 2>&1; then
    # linuxbase.org
    OS=$(lsb_release -si)
    VER=$(lsb_release -sr)
elif [ -f /etc/lsb-release ]; then
    # For some versions of Debian/Ubuntu without lsb_release command
    . /etc/lsb-release
    OS=$DISTRIB_ID
    VER=$DISTRIB_RELEASE
elif [ -f /etc/debian_version ]; then
    # Older Debian/Ubuntu/etc.
    OS=Debian
    VER=$(cat /etc/debian_version)

fi

 echo "Linux $OS"
 echo "Version: $VER"


 Ubuntu24="apt-get install python3 python3-pip python3-venv python3-gdal python3-pil.imagetk p7zip-full libnvtt-bin freeglut3-dev gdal-bin"
 Debian="apt-get install python3 python3-venv python3-pip python3-gdal python3-pil.imagetk p7zip-full libnvtt-bin freeglut3 gdal-bin"
 Arch="pacman -S python python-pip python-gdal p7zip freeglut tk podofo netcdf mariadb hdf5 cfitsio postgresql"

 
 if [[ "$OS" == *"Ubuntu"* ]]; then
   py_ver="3"
   update="sudo apt-get update"
   if [[ "$VER" == *"24"* ]]; then
      system_packages=$Ubuntu24
   else
      system_packages=$Debian
   fi
 
 elif [[ "$OS" == *"Mint"* ]]; then
      py_ver="3"
      update="sudo apt-get update"
      system_packages=$Debian
 
 elif [[ "$OS" == *"Debian"* ]]; then
      py_ver="3"
      update="sudo apt-get update"
      system_packages=$Debian
 elif [[ "$OS" == *"Arch"* ]]; then
      py_ver="3.12"
      update="sudo pacman -Syu"
      system_packages=$Arch
 elif [[ "$OS" == *"Manjaro"* ]]; then
      py_ver="3.12"
      update="sudo pacman -Syu"
      system_packages=$Arch 
 else
     OS="Unknown"
 fi


if ! [ -x "$(command -v gdalwarp)" ]; then
    echo " "
    echo "It looks like system packages required by Ortho4XP are not installed!"
    echo " "
fi


if [[ "$OS" == "Unknown" ]]; then
echo " "
echo "Do you want to run update and install system packages required by O4XP ?"
read -p "Install for distribution based on Arch? (a) Debian? (d) Skip installation? (s) " ads 
echo " "
case $ads in
	s ) echo "ok, we will proceed without installation of system packages";;
        a ) echo "Updating system and installing packages for Arch-based distribution";
	    py_ver="3.12";
	    sudo pacman -Syu;
            sudo $Arch;;
	d ) echo "Updating system and installing packages for Debian-based distribution";
            py_ver="3"; 
	    sudo apt-get update;
            sudo $Debian;;		
	* ) echo invalid response;
	    exit 1;;
esac


else

read -p "Do you want to run update and install system packages for $OS required by O4XP? (y/n) " yn

case $yn in
	n ) echo "ok, we will proceed without installation of system packages";;
	y ) echo "Updating system and installing packages required by O4XP";
	    $update;
            sudo $system_packages;;
	* ) echo invalid response;
		exit 1;;
esac

fi

echo " "
      
else 
  echo "Unsupported system!"
  exit 1
fi

# Finding python command on older distributions

if ! [ -x "$(command -v python$py_ver)" ] && [[ "$OSTYPE" == "linux-gnu"* ]]; then
      if  [ -x "$(command -v python)" ]; then
          py_ver=""
      else
          py_ver="3"
      fi   
fi

# Remove existing venv

if [ -d $venv_path ]; then
  echo "Removing existing venv: $venv_path"
  rm -rf $venv_path
fi

# Create a Python virtual environment

python$py_ver -m venv --system-site-packages $venv_path

# Activate Python venv

source $venv_path/bin/activate

# Install packages with pip

cd $SCRIPT_DIR

pip install -I -r requirements.txt

if [[ "$OSTYPE" == "darwin"* ]] && [[ $py_ver != "3.12" ]] ; then
   pip install -I gdal==$(gdal-config --version)
fi

echo " "

if [ -d "$venv_path/bin" ]; then
  echo "$(python --version) venv has been created in the $venv_path directory"
fi

echo " "
echo "Installed packages:"
pip list
echo " "
echo " "
echo "Use $SCRIPT_DIR/z_Start_O4XP_PythonVenv.sh to start O4XP"
echo " "
