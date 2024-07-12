#! /bin/bash

# Define Python version for macOS (tested with 3.10; 3.11; 3.12)
py_ver="3.12"

ssp=1
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

venv_path=$SCRIPT_DIR/venv-ortho

if [ ! -f "$SCRIPT_DIR/Ortho4XP.py" ]; then
  echo " "
  echo "Error !"
  echo " "
  echo "z_Install_O4XP_Python_Venv.sh should be in the main O4XP direcory !"
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

 
 if [[ "$(which python$py_ver)" != *"homebrew"* ]]; then
   echo " "
   echo "Python installed via Homebrew is required !" 
   echo " "
   echo "The PATH for Python in the hidden file .zprofile in your user directory should be removed !"
   echo " "
   echo "Contents of /Users/$USER/.zprofile: "
   echo " "
   echo "$(</Users/$USER/.zprofile )"
   echo " "
   echo "But only this line is required by Homebrew: "
   echo " "
   echo "eval \"\$($brew_path shellenv)\""
   echo " "
   read -p "Would you like the changes to be made automatically by this script? (y/n)  " yn
      case $yn in
	          n ) echo " ";
	              echo "You can edit /Users/$USER/.zprofile manually using TextEdit ";
                      echo " ";
	              exit 1;;
	          y ) echo " ";
	              echo "Renaming the original file to .zprofile_bak";
	              echo " ";
	              echo "Saving changes to:  /Users/$USER/.zprofile";
	              
	              if [ -f "/Users/$USER/.zprofile" ]; then                   
                      mv /Users/$USER/.zprofile /Users/$USER/.zprofile_bak
                      fi
	              echo " ";
	              echo "In the next step, (re)install Homebrew packages required by Ortho4XP !";
	              
	              update_path;;
	                           
	          * ) echo invalid response;
		      exit 1;;
      esac 
   

 fi

if ! [ -x "$(command -v gdalwarp)" ]; then
   echo "GDAL not found!" 
fi

if ! [ -x "$(command -v 7z)" ]; then
   echo "p7zip not found!"
fi

echo " "
read -p "Do you want to install Homebrew packages required by O4XP? (y/n) " yn

case $yn in
	n ) echo "ok, we will proceed without installation of Homebrew packages";;
	y ) echo "Installing Homebrew packages required by O4XP...";
	    brew install gdal python@$py_ver proj spatialindex p7zip python-tk@$py_ver;;
	* ) echo invalid response;
            exit 1;;
esac

echo "Approving the use of executables from $SCRIPT_DIR/Utils/ directory"
xattr -dr com.apple.quarantine $SCRIPT_DIR/Utils/*

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
 
 Debian="sudo apt install python3 python3-venv python3-pip python3-gdal python3-pil.imagetk p7zip-full libnvtt-bin freeglut3-dev gdal-bin gcc"
 Arch="sudo pacman -S python python-pip python-gdal p7zip freeglut tk podofo netcdf mariadb hdf5 cfitsio postgresql gcc"
 Fedora="sudo dnf install python3 python3-devel python3-pip python3-gdal python3-tkinter p7zip freeglut gcc-c++"
 openSUSE="sudo zypper install python311 python311-tk python311-devel gdal python3-GDAL p7zip freeglut-devel gcc-c++"
 
 if [[ "$OS" == *"Ubuntu"* ]]; then
      py_ver="3"
      update="sudo apt update"
      system_packages=$Debian
 
 elif [[ "$OS" == *"Mint"* ]]; then
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
      ssp=0

 elif [[ "$OS" == *"Manjaro"* ]]; then
      py_ver="3.12"
      update="sudo pacman -Syu"
      system_packages=$Arch
      ssp=0 
 
 elif [[ "$OS" == *"Fedora"* ]]; then
      py_ver="3.12"
      update="sudo dnf update"
      system_packages=$Fedora 

elif [[ "$OS" == *"openSUSE"* ]]; then
      py_ver="3.11"
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

# Using --system-site-packages for other configurations than macOS & GDAL 3.9

if [[ "$OSTYPE" == "darwin"* ]]; then
   if [[ "$(gdal-config --version)" == *"3.9"* ]]; then
   ssp=0
   fi
fi   


if [[ "$ssp" == 0 ]]; then
   python$py_ver -m venv $venv_path
else
   python$py_ver -m venv --system-site-packages $venv_path
fi

# Activate Python venv

source $venv_path/bin/activate

# Install packages with pip

cd $SCRIPT_DIR


if [[ "$ssp" == 0 ]]; then
   pip install -r requirements.txt
   pip install gdal==$(gdal-config --version)
else
   pip install -I -r requirements.txt
fi

echo " "

if [ -d "$venv_path/bin" ]; then
  echo "$(python --version) venv has been created in the $venv_path directory"
fi

# Make "z_Start_O4XP_PythonVenv.sh" an executable file
chmod +x z_Start_O4XP_PythonVenv.sh

echo " "
echo "Installed packages:"
pip list
echo " "
echo " "
echo " "
echo "Use $SCRIPT_DIR/z_Start_O4XP_PythonVenv.sh to start O4XP"
echo " "
