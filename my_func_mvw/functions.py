# Here I want to store all functions which I use in multiple scripts

# not sure if I need all of these here ... ?
import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
from matplotlib import colors
from datetime import date, timedelta
from collections import defaultdict
from collections import Counter
import matplotlib.patches as patches
import matplotlib.dates as mdates

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
get_abspath("sdfdsf")

def all_days_of_year(year, day_format="%Y-%m-%d"):
    """returns list with all days of a year in day_format (used in .strftime)"""
    output=[]
    #A timedelta object of 1 day
    oneday = timedelta(days=1)

    #A date object of the start of the year
    current_day = date(year, 1, 1)

    #Print all the days of the given year in YYYYmmdd format
    while current_day.year == year:
        output.append(current_day.strftime(day_format))
        current_day += oneday
    return output

def calculate_measurements_per_day(dic,print_output=True):
    """dic has to be the nested data dictionary
    returns dataframe with number pf unique days, depending on channelnumber and month
    """
    #create dataframe to save the number of unique days per month.
    #this means the number of days per month with at least one measurement
    channels=[1,2,3,4,5,6,7,8]
    months=[1,2,3,4,5,6,7,8,9,10,11,12]

    df_unique_days_month=pd.DataFrame(index=months,columns=channels)
    df_unique_days_month.index.names = ['Month']

    n_meas_pday=defaultdict(dict) # save number of measurements per day, depending on channel
    channelnumbers=dic.keys()
    for c in channelnumbers: # loop over each channel
        months_values=dic[c].keys()
        for m in months_values: # loop over each month
            one_file=dic[c][m]

            dates = one_file.index.get_level_values('Date').floor('D') # drop time of day information
            number_unique_day = len(dates.unique())
            #print(f"In month {m} of channel {c} are {number_unique_day} days with measurements")
            df_unique_days_month[int(c)][int(m)]=number_unique_day 
            
            count_measurements=Counter(dates) #Counts the occurence of the same date
            min_meas_day = 10 # threshhold of allowed measurements per day which is ok.
            for day in dates.unique():
                n_meas_pday[c][day.strftime("%Y-%m-%d")]=count_measurements[day]
                #if c == 1:
                #    test_1[day]=count_measurements[day]

                # print if day has less than 10 measurements
                if count_measurements[day] <= min_meas_day and print_output == True: 
                    print(f"{day.date()} has less than 10 measurements per day in channel {c}")


    return df_unique_days_month, n_meas_pday

def improve_n_meas_pday(n_meas_pday, year):
    """returns a dic, which also has days with 0 measurements
    
    Improve n_meas_pdy: add days where 0 measurements were made
    days with 0 measurements will occur in th new dictionaries

    used for output of calculate_measurements_per_day()
    """
    improved_n_meas_pday=defaultdict(dict)
    channelnumbers=["1","2","3","4","5","6","7","8"]
    for c in channelnumbers: # loop over each channel
        for day in all_days_of_year(year):
            if day in n_meas_pday[c].keys():
                improved_n_meas_pday[c][day] = n_meas_pday[c][day]
            else:
                improved_n_meas_pday[c][day] = 0
    return improved_n_meas_pday

