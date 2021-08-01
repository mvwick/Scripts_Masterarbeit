# dont really understand why they have to be imported here
import pickle
from collections import defaultdict
import glob
import pandas as pd

############## PICKLE IMPORTER ######################

def import_my_database_pickle(year, path_to_my_database_pickle):
    """import script for pickle data of 2019+, imports each year seperate"""
    def read_pickle(filename:str):
        #Function to read pickle Files
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def importer_pickle(data_20xx, path_to_my_database_pickle, year, c):
        """just for shortening the code"""
        
        filename = f"temp_ch{c}_{year}"
        path_to_file[filename] = path_to_my_database_pickle + "\\" + filename

        data_20xx[str(c)] = read_pickle(path_to_file[f"temp_ch{c}_{year}"])

        return data_20xx

    path_to_file={}
    data_20xx = {}
    if year == 2021: # all channels are activated since 01.06.2021
        channels = [1,2,3,4,5,6,7,8]
        for c in channels:
            importer_pickle(data_20xx, path_to_my_database_pickle, year, c)

    if year == 2019 or 2020: # channels 5-8 are empty
        channels = [1,2,3,4]
        for c in channels:
            importer_pickle(data_20xx, path_to_my_database_pickle, year, c)

    return data_20xx

def import_my_database_2018_pickle(path_to_my_database_2018_pickle):
    """imports 2018 pickle data"""
    def get_abspath(basepath):
        """Get the files you need to import into your script with Path
        Returns a list of all filepaths (or folderpaths) of the files (or folders) in a repository.
        The repository is given this function with basepath.

        you need to import: import glob
        """
        df_list = []
        basepath = glob.glob(basepath)
        for entry in basepath:
            df_list.append(entry)
        return (df_list)

    def read_pickle(filename:str):
        """Function to read pickle Files"""
        with open(filename, 'rb') as f:
            return pickle.load(f)

    data_2018=defaultdict(dict)
    all_paths_2018_pickle = get_abspath(path_to_my_database_2018_pickle + "\\*")
    for path in all_paths_2018_pickle:
        # get info about data from name
        partition=path.partition("_cablelength")[-1].partition("_ch")
        cable_length=partition[0]
        channel=partition[2]

        one_file=read_pickle(path)
        
        data_2018[cable_length][channel]=one_file

    return data_2018

############## CSV IMPORTER ######################

def import_my_database_csv(year,path_to_my_database):
    """ import the data of my_databse, every year seperate"""

    def importer(data_20xx, path_to_my_database, year, c):
        """just for shortening the code"""
        filename = f"temp_ch{c}_{year}.csv"
        path_to_file[filename] = path_to_my_database + "\\" + filename

        data_20xx[str(c)]         = pd.read_csv(path_to_file[f"temp_ch{c}_{year}.csv"], index_col=0)
        data_20xx[str(c)].index   = pd.to_datetime(data_20xx[str(c)].index, infer_datetime_format=True)
        data_20xx[str(c)].columns = data_20xx[str(c)].columns.astype(int)

        return data_20xx

    path_to_file={}
    data_20xx = {}
    if year == 2021: # all channels are activated since 01.06.2021
        channels = [1,2,3,4,5,6,7,8]
        for c in channels:
            importer(data_20xx, path_to_my_database, year, c)

    if year == 2019 or 2020: # channels 5-8 are empty
        channels = [1,2,3,4]
        for c in channels:
            importer(data_20xx, path_to_my_database, year, c)

    return data_20xx

def import_my_database_2018_csv(path_to_my_database_2018_csv):
    """imports 2018 csv data"""
    def get_abspath(basepath):
        """Get the files you need to import into your script with Path
        Returns a list of all filepaths (or folderpaths) of the files (or folders) in a repository.
        The repository is given this function with basepath.

        you need to import: import glob
        """
        df_list = []
        basepath = glob.glob(basepath)
        for entry in basepath:
            df_list.append(entry)
        return (df_list)

    data_2018=defaultdict(dict)
    all_paths_2018_csv = get_abspath(path_to_my_database_2018_csv + "\\*")
    for path in all_paths_2018_csv:
        # get info about data from path name
        partition=path.partition("_cablelength")[-1].partition("_ch")
        cable_length=partition[0]
        channel=partition[2][:-4]

        one_file         = pd.read_csv(path, index_col=0)
        one_file.index   = pd.to_datetime(one_file.index, infer_datetime_format=True)
        one_file.columns = one_file.columns.astype(float) #!!!!!!!different to other years
        
        data_2018[cable_length][channel]=one_file

    return data_2018


def merge_data_year(list_data_years):
    """input the different year dics as a list
    Merge the different year dics into one
    """
    data = {}

    for data_20xx in list_data_years:
        for channel in data_20xx.keys():

            if channel in data.keys():
                data[channel] = pd.concat([data[channel], data_20xx[channel]], axis = 0)

            else: # channel not in data dic
                data[channel] = data_20xx[channel]

    #eventle noch sort index machen; the seperate years are already sorted by index during saving
    return data


