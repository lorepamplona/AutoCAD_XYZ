import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "glob", "tkinter", "ctypes", "pyautocad"], "excludes": []}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="XYZIN - Automation",
    version="0.1",
    description="AutoCAD Automation Script",
    options={"build_exe": build_exe_options},
    executables=[Executable("XYZIN.py", base=base)],
)
