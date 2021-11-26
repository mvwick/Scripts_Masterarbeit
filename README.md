# Scripts_Masterarbeit
Here I collect all my scripts I need for my Masterthesis.
I use VSCode as primary editor and anaconda as package manager.
v1.0.0 corresponds to the submitting date of my thesis.

The data, which the scripts work with, is available on a sciebo repository of the GGE: `sciebo\DTS Data`.
If you currently read this from the sciebo repository, consider cloning the scripts folder from [Scripts_Masterarbeit](https://github.com/mvwick/Scripts_Masterarbeit.git).
The scripts are up-to-date on this sciebo repository but I think it is not a good practice to work or execute them here and create new branches or commits.
Each collaborator should do that locally.
Currently I dont follow this, I work directly on the sciebo repository.
Maybe as a maintainer you are allowed to break your own rules.
I am the only one using this at the moment anyway, so it doesnt matter.

# How To ...
In the following are explained some workflows, which aim to facilitate the begin of the work with the GGE-DTS.
## Where to start? It is the first time I am here. 
1. Get the data, the data is saved separately on sciebo, not public. Without the data you can not run any of the scripts. Go to the sciebo repository `sciebo\DTS Data` and download it, this script repository is included there.
2. `my_database_script.ipynb` gives a first overview and should be the first notebook you run. It can be run with the default libraries of Anaconda.
3. Set up environment: Install all libraries which are needed for the other scripts and not by default part of Anaconda.
**TO DO: link tutorial/explanation here**
4. You now have a first overview of the data and should be able to run all scripts.

## Install Charon4 and import all available data
You will need about 15 minutes to import all data.
1. Install a standard Charon4 version on you working PC, e.g. `sciebo\DTS Data\Miscellaneous\Charon_Software\Charon4_2_39_Support`. You could also use Charon3 but 3 and 4 are not compatible with each other. Currently the download from the devices is done with Charon4, this would have to be changed first, if you want to use Charon3.
2. alt + shift + F3 to enter User Level 3, which has more rights. Username and password are given in chapter Login Charon from `sciebo\DTS Data\Log-In_DTS_devices_software.docx` I recommend using the *keep me logged in* option.
3. Import the already existing data (`.mex4`) into Charon4. Click on *Charon Symbol* in top left corner then *Import* and import `sciebo/DTS Data/Alsdorf/Daten/unprocessed/mex_backup/laptop_all_split/laptop_all_20210708.mex4`, this is all the data from the old laptop in Alsdorf, which has been replaced by a new PC.
4. Import all other `.mex4` files from `sciebo/DTS Data/Alsdorf/Daten/unprocessed/mex_backup`, if the import is finished your Charon4 now contains all available data from Alsdorf.
5. Now import the data from the EONERC. Got to `sciebo\DTS Data\EONERC\Data\unprocessed\mex_backup` and import all `.mex4` files. When the import is finished your Charon4 now contains all available data from EONERC.

## I want to add new DTS data to the database
1. First you should take a look at *where to start?*, if you are here the first time.
2. You should consider installing Charon4 on you working PC and import all available data first, take a look at *Install Charon4 and import all available data*. My workflow is to export the data from the measurement site as `.mex4`. I then import these files in my "personal" Charon4 installation. Then I export them in a readable format and process the data with the scripts. This workflow is described in the following.
3. Export the data from the device at the measurement site as `.mex4` using Charon4.
    1. Open Charon4 if not already open, if you are not logged in as Service user: press alt + shift + F3, username and password are given in `sciebo\DTS Data\Log-In_DTS_devices_software.docx`
        * You could start a data download from the device to the PC: *Service*, *Data Download* the process can be seen in the property window usually at the bottom left.
        * With the current settings the data is downloaded and deleted on the DTS device automatically, so manually downloading it is not needed
        * If you manual download you should delete the data on the device to avoid a full CF-Card
    2. Click on the controller number you want to export from, it needs to be selected for the next step.
    3. top left corner *Charon Symbol*, *Export*, *Measurement Data (.mex4)*
    4. New window opens: Choose the exported time range, use a range which overlaps with the before exported data time range, so no data ist forgotten. Duplicates are not imported by Charon.
4. Import this file to the "personal" Charon4 installation: top left corner *Charon Symbol*, *Import*
5. Export the data in a readable format (.txt)
    1. Click on the controller number you want to export from, it needs to be selected.
    2. top left corner *Charon Symbol*, *Export*, *Measurement Data (.txt)*
    3. New window opens: select the time range you want to export, use a range which overlaps with the before exported data time range, the scripts in this repository will filter duplicates.
    4. Path: Create a new folder in `sciebo\DTS Data\Alsdorf\Daten\unprocessed\Charon4\charon4_export_as_txt` and ad the path from the new folder.
    5. For all other settings use the same as given in `charon4_txt_to_python.ipynb`.
6. Add the path to the controller of the `.txt` repository to `charon4_txt_to_python.ipynb`, adapt the inputs for the used device (3195 or 3188).
5. Run `charon4_txt_to_python.ipynb`, this takes a few minutes.
6. Run the process scripts
7. The new data is now saved. You should now run the analyse scripts to incorporate the newer data in the plots.


## I want to add new reference temperature data (TLogger) to the database - Currently only in Alsdorf
Currently the logging device is not working in a stand alone mode. It needs to have a permanent connection to the PC, otherwise the logging stops and needs to be started manually again. **Add how to set up TLogger Lete**
1. The Lete Logging software should be open on the measurement PC.
    * If the software is not open, then no data is logged, with the current settings.
2. Go to the Lete data save folder and extract `kanal_1.txt` and `kanal_2.txt` from the data folder.
    * The Lete software will create new files if a new data point is saved.
3. Create a new folder in `sciebo\DTS Data\Alsdorf\Daten\T-logger` and add the files into it.
4. Add the path to `kanal_1.txt` to `tlogger_to_python.ipynb` and run the script.
5. New reference temperature measurements are now saved. You should now run the process and analyse scripts to incorporate the newer data in the plots.


## I want to set up or change settings of the Lete TLogger
Here I will write my experiences with the TLogger.
