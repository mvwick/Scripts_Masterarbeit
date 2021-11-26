:: Old script, which I used to copy data to the sciebo repositoy
:: I keep it in old_versions because its my first .bat script, maybe I come back here to look things up

:: this script uploads my_database to sciebo and adds the newest version of my script to the my_databse repository

:: copy scripts from my scripts folder to my_database folder, also copy outsourced functions
:: ----------------------------------------------------------------
copy /Y "C:\Users\Mathis\Desktop\Masterarbeit\Scripts\my_database_script.ipynb" "C:\Users\Mathis\Desktop\Masterarbeit\Alsdorf\Daten\my_database"
copy /Y "C:\Users\Mathis\Desktop\Masterarbeit\Scripts\analyse_shaft_temperature.ipynb" "C:\Users\Mathis\Desktop\Masterarbeit\Alsdorf\Daten\my_database"
copy /Y "C:\Users\Mathis\Desktop\Masterarbeit\Scripts\compare_both_devices.ipynb" "C:\Users\Mathis\Desktop\Masterarbeit\Alsdorf\Daten\my_database"
copy /Y "C:\Users\Mathis\Desktop\Masterarbeit\Scripts\analyse_ch1-4_my_database_alsdorf.ipynb" "C:\Users\Mathis\Desktop\Masterarbeit\Alsdorf\Daten\my_database"
copy /Y "C:\Users\Mathis\Desktop\Masterarbeit\Scripts\my_func_mvw\functions_import_my_database.py" "C:\Users\Mathis\Desktop\Masterarbeit\Alsdorf\Daten\my_database\my_func_mvw"
copy /Y "C:\Users\Mathis\Desktop\Masterarbeit\Scripts\my_func_mvw\functions_measurements_per_day.py" "C:\Users\Mathis\Desktop\Masterarbeit\Alsdorf\Daten\my_database\my_func_mvw"
copy /Y "C:\Users\Mathis\Desktop\Masterarbeit\Scripts\my_func_mvw\functions.py" "C:\Users\Mathis\Desktop\Masterarbeit\Alsdorf\Daten\my_database\my_func_mvw"
:: ----------------------------------------------------------------

:: change date in Readme.txt of my_database
:: ----------------------------------------------------------------
:: get date information
@echo off &setlocal DisableDelayedExpansion
For /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
::time information - wont use them
::For /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
::_%mytime%
::echo %mydate% 

:: write date into file
set "file=C:\Users\Mathis\Desktop\Masterarbeit\Alsdorf\Daten\my_database\README.txt" 
set "lastline=%mydate%" 
setlocal EnableDelayedExpansion
<"!file!" >"!file!.tmp~" (
  for /f %%i in ('type "!file!"^|find /c /v ""') do for /l %%j in (2 1 %%i) do (
    set "line=" &set /p "line="
    echo(!line!
  )
)
>>"!file!.tmp~" echo(!lastline!
move /y "!file!.tmp~" "!file!"
:: ----------------------------------------------------------------

:: copy my_database to myowncloud (my client for synching sciebo) - not optimal yet I have my_databse 2 times on my pc
:: ----------------------------------------------------------------
xcopy /e /v /Y "C:\Users\Mathis\Desktop\Masterarbeit\Alsdorf\Daten\my_database" "C:\Users\Mathis\ownCloud\Projekt Eduardschacht 2019\RWTH Projektunterlagen\my_database"
:: ----------------------------------------------------------------

pause