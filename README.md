# LGBATTERY

System tray battery indicator for Windows Logitech devices. BECAUSE LOGITECH WON'T FOR SOME REASON.

![Screenshot](tray-screenshot.png)

## WHAT ITS DOING
It uses the Python websockets library to watch for battry changed notifications from LG Hub - yeah, sorry, you'll still need that.

It puts an icon in the system tray after extracting the battery level icons it needs from `C:\Windows\SystemResources\wpdshext.dll.mun` These are saved in `%APPDATA%\lgbattery`.

On first run it'll display the icon with a question mark until you right click the tray icon and select your device which will cause it to get the battery level immediately.

Battery level is shown as a tooltip on the system tray icon which also changes depending on the battery level.

After that it'll save the selected device in `%APPDATA%\lgbattery\config.ini` so it'll pick it up on restart.

if you want, you can add a `level_file` entry to the prefs. This will cause the battery level to be written to that file, in case you want to display it in 72pt **Trebuchet MS** on the desktop using the ([now dead](https://en.wikipedia.org/wiki/Samurize)) Samurize or something.

## PREFERENCES
Preferences are stored in `%APPDATA%\lgbattery\config.ini` as a regular INI file. entries are as follows, under the `[PREFS]` section.

|Name|Description|
|--|--|
|`selected_device`|Logitech ID for the device being monitored. Updated by the application when item selected from system tray rigt click|
|`level_file`|Path to a text file that the application will create/update when the battery level changes|
|`log_level`|One of `DEBUG`, `INFO`, `WARNING` (default), `ERROR` or `CRITICAL` affecting the verbnosity of logging.|
|`log_file`|If present, should point to a text file to receive the loging output. Otherwise logging is done to console|

## IMPROVEMENTS
The selected device is not ticked (checked: US) when selected. This is a limitation of the `infi.systray` library so if they add that functionality there I'll update this program.

## CREDITS
Authors of all the libraries used (obviously) also @andyworld for [LGSTrayBattery](https://github.com/andyvorld/LGSTrayBattery/tree/master). I'd have just used that but it kept crashing for me, so I looked at the code as documentation for how to call the Logitech websockets API.

## APOLOGIES
There are probably many threading crimes committed in this code. I have zero experience with websockets or Python asyncio. Debug Duck is now in rehab.

---
## Build
Built on Python 3.12.0. From PowerShell:

```powershell 
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt
pyinstaller --hidden-import pkg_resources --hidden-import infi.systray --onefile --noconsole .\lgbattery.py
```
Then enjoy `.\dist\lgbattery.exe`