import sys
from cx_Freeze import setup, Executable

# Dependencies for your Tkinter code
build_exe_options = {
    "packages": ["tkinter", "serial", "re", "PIL", "datetime", "serial.tools.list_ports"],
    "include_files": ["log.txt", "tkintermapview", "green.png","offline_tiles_RAMGARH_Google.db"]
}

# Executablep
executables = [
    Executable("app.py",  base="Win32GUI")
]

# Setup configuration
setup(
    name="Node Map GUI",
    version="1.0",
    description="",
    options={"build_exe": build_exe_options},
    executables=executables
)
