[Download Ortho4XP](https://github.com/w8sl/Ortho4XP/archive/refs/heads/Progressive_140.zip)

**Steps specific for macOS:**

[Install Homebrew](https://brew.sh)

On Apple silicon Mac (if not done already) install Rosetta (run in terminal: **softwareupdate --install-rosetta**)

Installation on macOS and Linux
--------------------------------

Use "**z_Install_O4XP_Python_Venv.sh**" script (you need to first run: *chmod +x z_Install_O4XP_Python_Venv.sh*)

Follow the terminal output messages for instructions!

Use "**z_Start_O4XP_PythonVenv.sh**" script to run Ortho4XP

Both scripts will find working directory automatically. Just drag and drop into terminal. Avoid spaces in directory names!

Windows
-------
*Use only Notepad++ or similar editor to open/view files included in [Ortho4XP download](https://github.com/w8sl/Ortho4XP/archive/refs/heads/Progressive_140.zip)*

Download and install **Python 3.11** from www.python.org

Customize installation, check the following options:

"Add python.exe to PATH",
"pip",
"tcl/tk and IDLE",
"py launcher",
"Install Python 3.11 for all users",
"Add Python to environment variables",

Download binary wheel [GDAL for Python 3.11](https://github.com/cgohlke/geospatial-wheels/releases/download/v2024.2.18/GDAL-3.8.4-cp311-cp311-win_amd64.whl)

Download and install: 

[The Microsoft Visual C++ Redistributable packages for Visual Studio 2022](https://aka.ms/vs/17/release/vc_redist.x64.exe)

[Visual C++ Redistributable Packages for Visual Studio 2013](https://www.microsoft.com/en-us/download/details.aspx?id=40784)

Right-click Windows Start menu, then click "Terminal"(PowerShell)

Change directory to Ortho4XP (cd \path to\Ortho4XP folder [downloaded from GitHub](https://github.com/w8sl/Ortho4XP/archive/refs/heads/Progressive_140.zip)) and run:

**pip install -r requirements_win.txt**

Open Terminal(Admin) and execute the following command:

pip install /path to downloaded GDAL-***.whl file

Add the directory containing gdal.py, gdal_translate and gdalwarp (usually: *Program Files/Python311/Lib/site-packages/osgeo/*)
into the system PATH variable (right-click Windows Start menu -> System -> Advanced system settings -> Environment variables)

Open Terminal window in the Ortho4XP directory and run: **python Ortho4XP.py**

