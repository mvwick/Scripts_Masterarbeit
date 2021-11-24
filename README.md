# Scripts_Masterarbeit
Here I collect all my scripts I need for my Masterthesis. I use VSCode as primary editor and anaconda as package manager.

The data, which the scripts work with, is available on different sciebo repositories.

v1.0.0 corresponds to the submitting date of my thesis.

# It is the first time I am here - where to start?
1. Get the data, the data is saved separately on sciebo, not puplic. Without the data you can not run any of the scripts.  **explanation here** 
2. `my_database_script.ipynb` gives an first overview and should be the first notebook you run. It can be run with the default libraries of Anaconda.
3. Set up environment: Install all libraries which are needed for the other scripts and not default in Anaconda.
**TO DO: link tutorial/explanation here**
4. You now have a first overview of the data and should be able to run all scripts.

# I want to add new data to the database
1. First you should do the *where to start?* points, if you are here the first time.
2. Export the data from the device using Charon4. **add explanation** This repository is currently suited for the device in Alsdorf and EONERC.
3. Add the path to the `.txt` repository to `charon4_txt_to_python.ipynb`, adapt the inputs for the used device.
4. Run `charon4_txt_to_python.ipynb`, this takes a few minutes.
5. The new data is now saved. You should now run the analyse scripts to incorporate the newer data in the plots.