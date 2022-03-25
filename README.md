# Scripts_Masterarbeit
Here I collect all my scripts I need for my Masterthesis.
I use VSCode as primary editor and anaconda as package manager.
v1.0.0 corresponds to the submitting date of my thesis.

The data, which the scripts work with, is available on a sciebo repository of the GGE: `sciebo\DTS Data`.
If you currently read this from the sciebo repository, consider cloning the scripts folder from [Scripts_Masterarbeit](https://github.com/mvwick/Scripts_Masterarbeit.git).
The scripts are up-to-date on this sciebo repository but I think it is not a good practice to work or execute them here and create new branches or commits.
Each collaborator should do that locally.
This means download the complete DTS Data repository from sciebo and replace the ``Scripts`` folder with a clone of the GitHub repository ([Scripts_Masterarbeit](https://github.com/mvwick/Scripts_Masterarbeit.git))
Currently I dont follow this, I work directly on the sciebo repository.
Maybe as a maintainer you are allowed to break your own rules.
I am the only one using this at the moment anyway, so it doesnt matter.

# Overview Scripts
Some scripts are made for the data of a specific DTS device (Controller: `Alsdorf`, `EONERC`) others are not DTS device related or have inputs for the different devices (Controller: `universal`).
| Script  | Controller | Description |
| ------- | ---------- | ----------- |
| [my_func_mvw](my_func_mvw/)  | universal | Functions used in various notebooks of this repository |
| [Alsdorf_Plot_py.py](Alsdorf_Plot_py.py) | Alsdorf | Plotting script for channels 1 to 4 |
| [EGRT_analysis.ipynb](EGRT_analysis.ipynb) | Alsdorf | Calculation of depth dependent apparent effective thermal conductivity, form data measured by Solexperts |
| [analyse_ch1-4_my_database_alsdorf.ipynb](analyse_ch1-4_my_database_alsdorf.ipynb) | Alsdorf | Various plots and analyses of channels 1 to 4. Highlights are histogram of water tank difference, difference to PTSal log from 24.11.2020, length dependent difference between channels.|
| [analyse_my_database_alsdorf.ipynb](analyse_my_database_alsdorf.ipynb) | Alsdorf | Mostly channels 5 to 8 are analysed. Highlights are interactive plot of data, statistics of difference at water tank positions of channels 5 to 8, differences between channels (also between channels of both cables), linear trend analysis, difference of up and down measurements |
| [analyse_shaft_temperature.ipynb](analyse_shaft_temperature.ipynb) | Alsdorf | Only the shaft temperature measurements from the mean of channels 7 and 8 on its own are analysed. Difference of up and down is plotted and variability over time shown. |
| [charon3_txt_to_python_and_merge_EONERC.ipynb](charon3_txt_to_python_and_merge_EONERC.ipynb) | EONERC | Loads the data exported with Charon3 and saves them in an easier to acces format |
| [charon4_txt_to_python.ipynb](charon4_txt_to_python.ipynb) | universal | Loads the data exported with Charon4 and saves them in an easier to acces format |
| [charon4_txt_to_python_2018data.ipynb](charon4_txt_to_python_2018data.ipynb) | Alsdorf | Loads the data exported with Charon4 from 2018 and saves them in an easier to acces format |
| [compare_both_devices.ipynb](compare_both_devices.ipynb) | Alsdorf | Compares (calculate differences) the measurements of Solexperts with the measurements made with the Lios device |
| [compare_ch14_to_heatexchanger_usage_and_EGRT.ipynb](compare_ch14_to_heatexchanger_usage_and_EGRT.ipynb) | Alsdorf | Borehole Heat Exchanger (BHE) usage is compared to the DTS measurements (channels 1 to 4). Additionally Enhanced Geothermal Response Test (EGRT) heating phases are compared to channels 1 to 4. |
| [frequency_analysis.ipynb](frequency_analysis.ipynb) | Alsdorf | Frequency dependence of channels 1 to 8 is analysed, using a fast fourier transformation. The frequqncy is also analysed depth dependent resulting in carpet plots.|
| [my_database_script.ipynb](my_database_script.ipynb) | Alsdorf | Creates some basic plots. The idea of this notebook is to get an overview of the data, which comes directly from the DTS device, without processesing. |
| [my_database_script_EONERC.ipynb](my_database_script_EONERC.ipynb) | EONERC | Creates some basic plots. The idea of this notebook is to get an overview of the data, which comes directly from the DTS device, without processesing. |
| [process_ch1-4.ipynb](process_ch1-4.ipynb) | Alsdorf | Processing of channels 1 to 4. |
| [process_ch5-8.ipynb](process_ch5-8.ipynb) | Alsdorf | Processing of channels 5 to 8. |
| [raw_backscattered_to_temp.ipynb](raw_backscattered_to_temp.ipynb) | universal | Calcualte temperature values from the raw data (stokes and anti-stokes) |
| [raw_backscattered_to_temp_from_Charon3.ipynb](raw_backscattered_to_temp_from_Charon3.ipynb) | universal | Calcualte temperature values from the raw data (stokes and anti-stokes). Additionally calculate dB (exported by Charon3) into counts. |
| [shaft_water_rise.ipynb](shaft_water_rise.ipynb) | Alsdorf | Monitoring of the shaft water rise of all channels. |
| [tlogger_to_python.ipynb](tlogger_to_python.ipynb) | Alsdorf | Data from Lete TLogger is smoothed, ploted and saved in an easy to acces format. |
| [Charon_tips_tricks.md](Charon_tips_tricks.md) | universal | Various hints and learnings I discovered during using the Charon software |
| [old_versions/MWE_plotly_problem.ipynb](old_versions/MWE_plotly_problem.ipynb) | universal  | Example notebook for a Issue I created for plotly |
| [old_versions/compare.ipynb](old_versions/compare.ipynb) | Alsdorf | compare the data created by merge_files.ipynb to data in the databse |
| [old_versions/merge_files.ipynb](old_versions/merge_files.ipynb) | Alsdorf | converts Charon4 data into less files, used for old data repository I found on the PC |
| [old_versions/compilation_of_helpfull_code.ipynb](old_versions/compilation_of_helpfull_code.ipynb) | universal | Code which has no use currently but may be helpfull in the future |
| [old_versions/upload_my_database.bat](old_versions/upload_my_database.bat) | universal |Has been used to copy data to the sciebo repositoy|

# How To ...
In the following are explained some workflows, which aim to facilitate the begin of the work with the GGE-DTS.

## Where to start? It is the first time I am here. 
1. Get the data; the data is saved separately on sciebo, not public. Without the data you can not run any of the scripts. Go to the sciebo repository `sciebo\DTS Data` and download it, this script repository is included there.
2. `my_database_script.ipynb` gives a first overview and should be the first notebook you run.
3. Set up environment: Install plotly and kaleido, all other used libraries are part of Anaconda by default. If you need a more detailed explanation see [Set up python environment](#set-up-python-environment).
4. You now have a first overview of the data and should be able to run all scripts.

### Set up python environment
If you are familier with python you dont need this section.
I will explain one option how you can install all libraries and get the scripts to run.
By the way I am (usually) a windows guy.
I use [Anaconda](https://www.anaconda.com/products/individual) as package manager.
In some scripts, I use libraries which are not installed by default in Anaconda.
1. If you are new to python install [Anaconda](https://www.anaconda.com/products/individual).
2. You can use an editor from Anaconda, personally I use a different one: [VSCode](https://code.visualstudio.com/). VSCode is an editor for everything, you need to install extensions for different file types. Install the following ones: Jupyter, Pylance and Python.
3. Open the anaconda prompt (found in Anaconda Navigator or Search) and install the following libraries, they are not by default installed from Anaconda.
````
conda install -c plotly plotly
conda install -c conda-forge python-kaleido
````
4. You are now equipped for executing all scripts.

## Install Charon4 and import all available data
Some of my experiences with Charon are summarized in [Charon_tips_and_tricks](./Charon_tips_tricks.md#charon3-and-charon4-tips-and-tricks).
You will need about 10 minutes to import all data.
1. Install a standard Charon4 version on you working PC, e.g. `sciebo\DTS Data\Miscellaneous\Charon_Software\Charon4_2_39_Support`. You could also use Charon3 but 3 and 4 are not compatible with each other. Currently the download from the devices is done with Charon4, this would have to be changed first, if you want to use Charon3.
2. alt + shift + F3 to enter User Level 3, which has more rights. Username and password are given in chapter Login Charon from `sciebo\DTS Data\Log-In_DTS_devices_software.docx` I recommend using the *keep me logged in* option.
3. Import the already existing data (`.mex4`) into Charon4. Click on *Charon Symbol* in top left corner then *Import* and import `sciebo/DTS Data/Alsdorf/Daten/unprocessed/mex_backup/all_data_until_04112021.mex4`. This imports 8 files because the data has been split among them.
4. Import all other `.mex4` files from `sciebo/DTS Data/Alsdorf/Daten/unprocessed/mex_backup`. When you finished your Charon4 now contains all available data from Alsdorf.
5. Now import the data from the EONERC. Go to `sciebo\DTS Data\EONERC\Data\unprocessed\mex_backup` and import all `.mex4` files. When the import is finished your Charon4 now contains all available data from EONERC.

## I want to add new DTS data to the database
First you should take a look at [where to start?](#where-to-start-it-is-the-first-time-i-am-here), if you are here the first time.
Additionally, you should consider [installing Charon4 and import all available data](#install-charon4-and-import-all-available-data) on you working PC.
My workflow is to export the data from the measurement site as `.mex4`.
I then import these files in my "personal" Charon4 installation.
Then I export them in a readable format and process the data with the scripts.
This workflow is described in the following.
1. Export the data from the device at the measurement site as `.mex4` using Charon4.
    1. Open Charon4 if not already open, if you are not logged in as Service user: press alt + shift + F3, username and password are given in `sciebo\DTS Data\Log-In_DTS_devices_software.docx`
        * You could start a data download from the device to the PC: *Service*, *Data Download* the process can be seen in the property window usually at the bottom left.
        * With the current settings the data is downloaded and deleted on the DTS device automatically, so manually downloading it is not needed
        * If you manual download you should delete the data on the device to avoid a full CF-Card
    2. Click on the controller number you want to export from, it needs to be selected for the next step.
    3. top left corner *Charon Symbol*, *Export*, *Measurement Data (.mex4)*
    4. New window opens: Choose the exported time range, use a range which overlaps with the before exported data time range, so no data ist forgotten. Duplicates are not imported by Charon.
2. Import this file to the "personal" Charon4 installation: top left corner *Charon Symbol*, *Import*
3. Export the data in a readable format (`.txt`)
    1. Click on the controller number you want to export from, it needs to be selected.
    2. top left corner *Charon Symbol*, *Export*, *Measurement Data (.txt)*
    3. New window opens: select the time range you want to export, use a range which overlaps with the before exported data time range, the scripts in this repository will filter duplicates.
    4. *Path*: Create a new folder in `sciebo\DTS Data\Alsdorf\Daten\unprocessed\Charon4\charon4_export_as_txt` or `sciebo\DTS Data\EONERC\Daten\unprocessed\charon4_export_as_txt` and add the path from the new folder.
    5. For all other settings use the same as given in `charon4_txt_to_python.ipynb`.
4. Add the path to the controller of the `.txt` repository to `charon4_txt_to_python.ipynb`, adapt the inputs for the used device (3195 or 3188).
5. Run `charon4_txt_to_python.ipynb`, this takes a few minutes.
6. For EONERC only: run `charon3_txt_to_python_and_merge_EONERC.ipynb` to merge the new data with all other avaible data
7. Run the process scripts (not yet implemented for EONERC)
8. The new data is now saved. You should now run the analyse scripts (or `my_database_script` for a first overview) to incorporate the new data in the plots.

## I want to add new reference temperature data (TLogger) to the database - Currently only in Alsdorf
Currently the logging device needs a permanent connection to the PC, otherwise the logging stops and needs to be started manually again.
If you want to change the settings maybe this notes are off help: [I want to set up or change settings of the Lete TLogger](#i-want-to-set-up-or-change-settings-of-the-Lete-TLogger)
1. The Lete Logging software should be open on the measurement PC.
    * If the software is not open, then no data is logged, with the current settings.
2. Go to the Lete data save folder and extract `kanal_1.txt` and `kanal_2.txt` from the data folder.
    * The Lete software will create new files if a new data point is saved.
3. Create a new folder in `sciebo\DTS Data\Alsdorf\Daten\T-logger` and add the files into it.
4. run `tlogger_to_python.ipynb`
5. New reference temperature measurements are now saved. You should now run the process and analyse scripts to incorporate the newer data in the plots.

## I want to set up or change settings of the Lete TLogger
You should definitely take a look at the manuals: `sciebo\DTS Data\Miscellaneous\T_logger_lete_software`
Lothar installed the hardware.
I did not manage to set up a stable CF-Card use: *Extras* *Speicher Karte*.
I noticed short connection interruptions, which stop the logging or reset the date labelling.
Therefore, the data is at the moment directly saved on the PC.
The downside is that the logger needs to be connected to the turned on PC all the time.
1. Follow the installation description in 5 Softwareinstallation of `sciebo\DTS Data\Miscellaneous\T_logger_lete_software\LE-LOG_1623_USB_TE_SP.pdf`
    * I did not need to add the driver manually
2. Got *Formel Editor* and select for each channel the logging type.
3. If the shown value is not in the expected range maybe change the mode to *Berechnung im Controller* or *Berechnung im PC*
4. Deactivate all unused channels: *Kanal deaktivieren*
5. Choose the logging time per channel in *Zeit (ms)*
6. Tick *Logger an/aus*; The logging should work now, the data is saved in the `data` folder of the Lete repository.
<!-- Here are som notes on how to use the logger in remote mode (Speicher Karte). Currently this mode is not used.
How-to-export data:
Fenster für Speicherkarte öffnen; update drücken; download /read file starten; im pop up Fenster auf öffnen drücken von _daten;
alles aus dem Ordner kopieren; manchmal klappt konvertieren nicht direkt?; 
Man kann im Fenster der Speicherkarte unten rechts auf konvertieren klicken, dann wird ein neuer file abgespeichert der ein einfacheres Format hat (adc...);
Dann auf init, so wird die Speicherkarte gelöscht; Danach läuft alles normal weiter -->

