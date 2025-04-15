[Download Ortho4XP](https://github.com/w8sl/Ortho4XP/archive/refs/heads/Progressive_140.zip)

Installation on macOS - quick method
---------------------

Download and install Python 3.12 from [www.python.org](https://www.python.org/downloads/macos/)
- Use **“z_Install_Mac.sh”** script to install O4XP. Follow these steps:

  - Open the terminal in the main Ortho4XP directory -> right click on the folder, choose: **Services** -> **New Terminal at Folder**

  - Execute the following commands in the terminal (copy-paste and press enter):


    `chmod +x z_Install_Mac.sh`

    `./z_Install_Mac.sh`
    
 - To launch Ortho4XP, double-click on the file named **"z_Start_O4XP.command"**

Installation on Linux, macOS with [Homebrew](https://brew.sh/)
------------------------------------------

- Use **“z_Install_O4XP.sh”** script (run `chmod +x z_Install_O4XP.sh` first)
- Follow the terminal output for instructions
- Use **“z_Start_O4XP.sh”** to run Ortho4XP
- Both scripts find working directory automatically
- On Linux, the script forces system updates. It may be safer to run “sudo apt update” or equivalent manually

Windows:
-------------------------------
- Download and install Python from the official website: [www.python.org](https://www.python.org/downloads/windows/) Python versions 3.10 to 3.13 are supported
- Customize the installation to include “Add python.exe to PATH”, “pip”, “tcl/tk and IDLE”, “Add Python to environment variables”
- **Download and install:** [Latest Microsoft Visual C++ Redistributable Version](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Click on **"win_install.bat"** file for the installation and **"win_start.bat"** to run Ortho4XP
- For manual installation, run: **pip install -r requirements.txt**
- Use only Notepad++ or a similar editor to open/edit Ortho4XP files

Important notices:
-------------------------------
- Set the `custom_overlay_src` config variable to the: `../X-Plane 12/Global Scenery/X-Plane 12 Global Scenery` directory !
- After modifying the settings, press the `Apply` button, for the current session. Press `Write App Config` to make cahanges permanent
- Always close Ortho4XP by pressing the blue “turn-off” button
- To use the progressive_zl feature or create symlinks to Custom Scenery, set the `xplane_install_dir` in the Ortho4XP Config settings

