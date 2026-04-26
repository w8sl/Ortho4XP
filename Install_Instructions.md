[Download Ortho4XP](https://github.com/w8sl/Ortho4XP/archive/refs/heads/mesh_dev.zip)

Installation on Linux, macOS with [Homebrew](https://brew.sh/)
------------------------------------------

- Use **“z_Install_O4XP.sh”** script (run `chmod +x z_Install_O4XP.sh` first)
- Follow the terminal output for instructions
- Use **“z_Start_O4XP.sh”** to run Ortho4XP
- Both scripts find working directory automatically
- On Linux: first, install system updates using the GUI (if possible) or run “sudo apt update” or equivalent command for your distro

Windows:
-------------------------------
- Download and install Python from the official website: [www.python.org](https://www.python.org/downloads/windows/) Python versions 3.10 to 3.13 are supported
- Customize the installation to include “Add python.exe to PATH”, “pip”, “tcl/tk and IDLE”, “Add Python to environment variables”
- **Download and install:** [Latest Microsoft Visual C++ Redistributable Version](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Click on **"win_install.bat"** file for the installation and **"win_start.bat"** to run Ortho4XP
- For manual installation, run in PowerShell: **pip install -r requirements.txt**

Important notes:
-------------------------------
- On Windows, use Notepad++ or a similar editor to open Ortho4XP files
- After modifying the settings, press the `Apply` button, for the current session. Press `Write App Config` to make changes permanent
- Always close Ortho4XP by pressing the blue “turn-off” button
- To use the progressive_zl feature or create symlinks to Custom Scenery, set the `xplane_install_dir` in the Ortho4XP Config settings
