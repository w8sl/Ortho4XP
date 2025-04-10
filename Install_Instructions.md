[Download Ortho4XP](https://github.com/w8sl/Ortho4XP/archive/refs/heads/Progressive_140.zip)

Installation on macOS - quick method
---------------------

Download and install Python 3.12 from [www.python.org](https://www.python.org/downloads/macos/)
- Use **“z_Install_Mac.sh”** script to install O4XP. Follow these steps:

  - Open the terminal in the main Ortho4XP directory -> right click on the folder, choose: **Services** -> **New Terminal at Folder**

  - Type:   **_chmod +x z_Install_Mac.sh_**   press enter

  - Type:   **_./z_Install_Mac.sh_**   press enter
    
 - To launch Ortho4XP, simply double-click on the file named **"z_Start_O4XP.command"**

Installation on Linux, macOS with [Homebrew](https://brew.sh/)
------------------------------------------

- Use **“z_Install_O4XP.sh”** script (run chmod +x z_Install_O4XP.sh first)
- Follow the terminal output for instructions
- Use **“z_Start_O4XP.sh”** to run Ortho4XP
- Both scripts find working directory automatically

Windows:
-------------------------------
- Download and install Python from the official website: www.python.org. Python versions 3.10 to 3.13 are supported
- Customize the installation to include “Add python.exe to PATH”, “pip”, “tcl/tk and IDLE”, “Add Python to environment variables”
- **Download and install:** [Latest Microsoft Visual C++ Redistributable Version](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Click on **"win_install.bat"** file for the installation and **"win_start.bat"** to run Ortho4XP
- For manual installation, simply run: **pip install -r requirements.txt**
- Use only Notepad++ or a similar editor to open/edit Ortho4XP files

Important notices:
-------------------------------
- The "**custom overlay src**" config variable must be set to the: "../X-Plane 12/Global Scenery/X-Plane 12 Global Scenery" directory
- After modifying the settings, press the “Apply” button
- Always close Ortho4XP by pressing the blue “turn-off” button

