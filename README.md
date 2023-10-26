# LGBATTERY

System tray battery indicator for Windows Logitech devices. BECAUSE LOGITECH WON'T for some reason.



## Build
```powershell
pyinstaller --hidden-import pkg_resources --hidden-import infi.systray --onefile --noconsole .\lgbattery.py
```