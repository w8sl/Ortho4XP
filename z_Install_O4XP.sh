#! /bin/bash

#Get path to the Ortho4XP directory
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

#Change to the Ortho4XP directory
cd "$(dirname "${BASH_SOURCE[0]}")"

venv_path="./venv-ortho"

if [ ! -f ./Ortho4XP.py ]; then
  echo " "
  echo "Error !"
  echo " "
  echo "z_Install_O4XP.sh should be in the main O4XP directory !"
  echo " "
  exit 1 
fi

# Semi-automated, guided installation for macOS

if [[ "$OSTYPE" == "darwin"* ]]; then
   echo "macOS"

# Choose the Python version for macOS installation

read -p "Which version of Python would you like to use with Ortho4XP? (0) 3.10, (1) 3.11, (2) 3.12 (3) 3.13  " nr
         case $nr in
	          0 ) echo " ";
	              echo "Proceeding with Python 3.10";
                  py_ver="3.10" 
	              echo " " ;;
	          1 ) echo " ";
	              echo "Proceeding with Python 3.11";
                  py_ver="3.11" 
	              echo " " ;;
	          2 ) echo " ";
	              echo "Proceeding with Python 3.12";
                  py_ver="3.12" 
	              echo " " ;; 
	          3 ) echo " ";
	              echo "Proceeding with Python 3.13";
                  py_ver="3.13" 
	              echo " " ;;                               
	          * ) echo invalid response;
		      exit 1;;
          esac 

# Path to Homebrew

   if [[ "$(uname -m)" == "arm64" ]]; then
     brew_path="/opt/homebrew/bin/brew"
   else
     brew_path="/usr/local/bin/brew"
   fi

update_path(){
    
    if [[ "$(uname -m)" == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/$USER/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
        else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> /Users/$USER/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
}

 if ! [ -x "$(command -v brew)" ]; then
   
   echo " "
       
     if [ -f $brew_path ]; then
       echo "It looks like Homebrew is installed but it is not in the PATH !"
       echo " "
       
       read -p "Would you like to update the PATH automatically by this script? (y/n) " yn

         case $yn in
	          n ) echo " ";
	              echo "You can add Homebrew to the PATH manually";
                      echo " ";
                      echo "Run this command and restart the terminal:";
                      echo " ";
                      echo "echo 'eval \"\$($brew_path shellenv)\"' >> /Users/$USER/.zprofile";
	              echo " ";
	              exit 1;;
	          y ) echo "Adding Homebrew to the PATH in: /Users/$USER/.zprofile";
	              update_path;;	              
	          * ) echo invalid response;
		      exit 1;;
          esac 
     else
       echo "Homebrew is required but is not installed !"  
       echo " "
       echo "Install Homebrew ! See: https://brew.sh"
       echo " "
       exit 1
     fi
   echo " "      
 fi

 if ! [ -x "$(command -v python$py_ver)" ]; then
   echo "Python $py_ver not found! "
 fi 

echo " "
read -p "Do you want to (re)install Homebrew packages required by O4XP? (y/n) " yn

case $yn in
	n ) echo "ok, we will proceed without installation of Homebrew packages";;
	y ) echo "Installing Homebrew packages required by O4XP...";
	    brew install python@$py_ver proj geos spatialindex p7zip python-tk@$py_ver;;
	* ) echo invalid response;
            exit 1;;
esac

echo " "

echo "Approving the use of executables from $SCRIPT_DIR/Utils/mac directory"
xattr -dr com.apple.quarantine ./Utils/mac/*

# Semi-automated, guided installation for Linux

elif [[ "$OSTYPE" == "linux"* ]]; then

 
if   type lsb_release >/dev/null 2>&1; then
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
elif [ -f /etc/os-release ]; then
     # freedesktop.org and systemd
     . /etc/os-release
     OS=$NAME
     VER=$VERSION_ID
fi

 echo "Linux $OS"
 echo "Version: $VER"
 
# Required system packages
 
 Debian="sudo apt-get install python3 python3-venv python3-pip python3-gdal libgdal-dev python3-pil.imagetk p7zip-full libnvtt-bin freeglut3-dev gdal-bin gcc"
 Arch="sudo pacman -S python python-pip python-gdal p7zip freeglut tk podofo netcdf mariadb hdf5 cfitsio postgresql gcc"
 Fedora="sudo dnf install python3 python3-devel python3-pip python3-gdal gdal-devel python3-tkinter p7zip freeglut gcc-c++"
 openSUSE="sudo zypper install python312 python312-tk python312-devel gdal python3-GDAL p7zip freeglut-devel gcc-c++"
 
 if [[ "$OS" == *"Ubuntu"* ]]; then
      py_ver="3"
      update="sudo apt update"
      system_packages=$Debian
 
 elif [[ "$OS" == *"Linuxmint"* ]]; then
      py_ver="3"
      update="sudo apt update"
      system_packages=$Debian
 
 elif [[ "$OS" == *"Debian"* ]]; then
      py_ver="3"
      update="sudo apt update"
      system_packages=$Debian

 elif [[ "$OS" == *"Arch"* ]]; then
      py_ver="3.12"
      update="sudo pacman -Syu"
      system_packages=$Arch

 elif [[ "$OS" == *"Manjaro"* ]]; then
      py_ver="3.12"
      update="sudo pacman -Syu"
      system_packages=$Arch
 
 elif [[ "$OS" == *"Fedora"* ]]; then
      py_ver="3"
      update="sudo dnf update"
      system_packages=$Fedora 

elif [[ "$OS" == *"openSUSE"* ]]; then
      py_ver="3.12"
      update="sudo zypper dup"
      system_packages=$openSUSE

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
echo " "
read -p "Install for distribution based on Arch? (a) Debian? (d) Skip installation? (s) " ads 
echo " "
case $ads in
	s ) echo "ok, we will proceed without installation of system packages";;
        a ) echo "Updating system and installing packages for Arch-based distribution";
	    py_ver="3.12";
	    sudo pacman -Syu;
            $Arch;;
	d ) echo "Updating system and installing packages for Debian-based distribution";
            py_ver="3"; 
	    sudo apt update;
            $Debian;;		
	* ) echo invalid response;
	    exit 1;;
esac


else

read -p "Do you want to run update and install system packages for $OS required by O4XP? (y/n) " yn

case $yn in
	n ) echo "ok, we will proceed without installation of system packages";;
	y ) echo "Updating system and installing packages required by O4XP";
	    $update;
            $system_packages;;
	* ) echo invalid response;
            exit 1;;
esac

fi

echo " "
      
else 
  echo "Unsupported system!"
  exit 1
fi

if [ "$(uname -m)" = "aarch64" ]; then

    #compile triangle and Triangle4XP from source on Linux aarch64
    echo "Linux aarch64 - compiling triangle and Triangle4XP from source..."
    gcc -O2 ./Utils/src/triangle.c -lm -o ./Utils/lin/triangle
    gcc -O2 ./Utils/src/Triangle4XP.c -lm -o ./Utils/lin/Triangle4XP
fi 

# Finding python command on "Unknown" distribution

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

python$py_ver -m venv $venv_path

# Activate Python venv

source $venv_path/bin/activate

if [[ "$OSTYPE" == "linux"* ]]; then
# Get the version of GDAL
gdal_version=$(gdal-config --version)

# Compare version strings

if [[ "$(printf '%s\n' "$gdal_version" "3.5.0" | sort -V | head -n1)" == "$gdal_version" && "$gdal_version" != "3.5.0" ]]; then
  # Replace strings in the "requirements.txt" file
  sed -i 's/^numpy.*$/numpy==1.26.4/' requirements.txt
  sed -i 's/^rasterio.*$/rasterio==1.3.11/' requirements.txt
  echo "Modyfying requirements.txt for GDAL<3.5"
fi
fi

# Install required packages with pip

pip install -r requirements.txt

echo " "

if [ -d "$venv_path/bin" ]; then
  echo "$(python --version) venv has been created in the $venv_path directory"
fi

echo " "
echo "Installed packages:"
pip list
echo " "
echo "Making \"z_Start_O4XP.sh\" an executable file"
chmod +x ./z_Start_O4XP.sh
xattr -dr com.apple.quarantine ./z_Start_O4XP.sh
echo " "
echo "Use z_Start_O4XP.sh to run Ortho4XP"
echo " "
