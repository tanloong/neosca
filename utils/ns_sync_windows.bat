REM https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/xcopy
xcopy Z:\projects\neosca\ C:\Users\tanlo\Desktop\neosca\ /E /Y /exclude:C:\Users\tanlo\Desktop\ns_sync_windows_excludes.txt
echo Source code synchronized. Press any key to start packaging, or close the window to stop here.
pause >nul
mklink /d C:\Users\tanlo\Desktop\neosca\src\neosca\ns_data\stanza_resources Z:\stanza_resources
cd C:\Users\tanlo\Desktop\neosca\
call %WORKON_HOME%\neosca\Scripts\activate
pyinstaller .\utils\neosca.spec -y --clean
pause
