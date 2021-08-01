# Here I want to store all functions which I use in multiple scripts
import glob
import pickle
import pandas as pd
import numpy as np
from datetime import timedelta
from random import randrange
import statistics

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


def find_nearest_date(base_date_name,date_index):
    """find the nearest date to base_date_name in date_index
    base_date_name: put in as str or Timestamp, I use a format like this: '2021-06-07 18:52:45'
    date_index: index of a dataframe, which contains dates
    returns:
    date_name: str
    date_iloc: position of date_name in date_index
    """
    date_iloc=date_index.get_loc(base_date_name,method="nearest")
    date_name=str(date_index[date_iloc])
    return date_name, date_iloc


def calc_diff_between_channels(data1,data2,find_nearest_date=find_nearest_date,expected_difference_minutes=13):
    """
    think of flipping one dataframe regarding length, because in avearaging channels one dataframe (channel 5 and 7) are flipped
    At the moment I flip outise of this function, if desired
    result: dic to store result dataframes in
    """
    all_dates=[]
    result={}
    df_diff=pd.DataFrame()
    df_diff_re=pd.DataFrame()
    df_diff_abs=pd.DataFrame()
    df_diff_abs_re=pd.DataFrame()
    # loop over all dates
    for i in range(1,len(data1.index)-1): #leave put first and last date
        date_name_chy, date_iloc_chy = find_nearest_date(data1.index[i],data2.index)
        date_name_chx = data1.index[i]

        # check difference between the two dates
        # not needed anymore, because its done at the beginning of the script now. But I will also keep it here
        allowed_difference = timedelta(minutes=expected_difference_minutes)
        time_diff = pd.to_datetime(date_name_chy) - date_name_chx
        if time_diff > timedelta(minutes=0):
            if time_diff > allowed_difference:
                print("Warning 1: large time difference")
                print(time_diff)
        elif time_diff < timedelta(minutes=0):
            if time_diff * -1 >  allowed_difference:
                print("Warning 2: large time difference")
                print(time_diff * -1)
        else: #val=0
            print("Something is wrong? No time diff between different channels!")

        # Calculate difference
        T_data1 = data1.loc[date_name_chx] #array with length as index, with all Temp. of the date
        T_data2 = data2.loc[date_name_chy]
        diff = T_data1 - T_data2#[::-1] #dont flip one here, i do it before puting the data into this function
        diff_abs = abs(diff)
        diff_re = diff/((T_data1+T_data2)/2) #ist das gut das so zu machen?
        diff_re_abs = abs(diff/T_data1)

        # save date in dataframe, date (columns name) is not the mean of both dates used
        df_diff_re[date_name_chx] = diff_re
        df_diff_abs[date_name_chx] = diff_abs
        df_diff_abs_re[date_name_chx] = diff_re_abs
        df_diff[date_name_chx] = diff
    
    result["diff"]= df_diff
    result["diff_abs"]= df_diff_abs
    result["diff_re"]= df_diff_re 
    result["diff_abs_re"]= df_diff_abs_re 
    return result


def watertank_shift(dataframe, df_Tlogger, watertank_len, watertank_T_range_min, watertank_T_range_max, channels=["5","6","7","8"], find_nearest_date=find_nearest_date):
    """shift the data to the temperature of the watertank, at first watertank position"""
    val_watertank_ch={}
    diff_in_watertank={}
    corrected_val={} # dic for different channel, containing the dataframe of the corrected values
    watertank_diff_log={}
    for chan in channels:
        df_c_v = pd.DataFrame(index=dataframe[chan].columns) # df for the corrected values
        df_c_v.columns.name="Date"

        df_watertank_diff_log=pd.DataFrame(index=[watertank_len[0]])

        # before always watertank position 0
        # want to test how much this influences the result, espeacially mean of channels
        # in mean calculation channel 5 and 7 are flipped
        watertank_pos=0 # for avearagefirst this is used, even when the below if are not commented out
        # if chan=="6" or chan=="8":
        #     watertank_pos=0
        # elif chan=="5":
        #     watertank_pos=1
        # elif chan=="7":
        #     watertank_pos=3

        # dataframe is cut so it fits the tlogger date range before
        for date_name in dataframe[chan].index:
            # Using chan in the following is somewhat unnecessary, because one date belongs only to one channel
            # But its not that bad I would say, because it makes things more explicit
            #date_numeric=mdates.date2num(date_name) # creates numeric of date, usefull for calculations
            
            # Temp of DTS cable at first watertank position
            val_watertank_ch[chan]=dataframe[chan].loc[str(date_name)][watertank_len[watertank_pos]]
            # Temp of watertank, measured by PT100
            val_watertank=temp_watertank_func([date_name], df_Tlogger)[0]
            # difference between PT100 and DTS at first watertank position
            # round values may be helpfull for reducing memory, 
            # decimal of 2 would be sufficient for the data accuaracy.
            diff_in_watertank[chan] = val_watertank_ch[chan] - val_watertank
            df_watertank_diff_log[date_name] = diff_in_watertank[chan] # save the difference

            # correct watertank diff; for all DTS points, based on first watertank position
            chan_val = np.array(dataframe[chan].loc[str(date_name)].values) # uncorrected DTS Temp
            # save corrected values in dataframe; c_v: corrected_value
            df_c_v[date_name] = chan_val - diff_in_watertank[chan]

        # save corected values of the channel in dic
        corrected_val[chan] = df_c_v.transpose() # same format as data_all
        # save watertank difference of the channel
        watertank_diff_log[chan] = df_watertank_diff_log
    
    return corrected_val, watertank_diff_log

def read_pickle(filename:str):
    #Function to read pickle Files
    with open(filename, 'rb') as f:
        return pickle.load(f)

def write_pickle(path,data):
    with open(path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def temp_watertank_func(x, df_Tlogger):
    """returns Temperature of Watertank at given time x, of the moving avearage values
    this is not really a matheamtical function, but I named it like this when I was using a polynomial function
    """
    # find nearest date in moving avearge
    temp = []
    for date in x:
        date_name, date_iloc = find_nearest_date(date,df_Tlogger["Channel1-rolling_mean"].index)
        Temperature = df_Tlogger["Channel1-rolling_mean"][date_name]
        Temperature_round = round(Temperature, 7) #round to 7s decimal place
        temp.append(Temperature_round)
    return temp

def random_date(start, end):
    """This function will return a random datetime between two datetime objects.
    https://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

def check_first_last_date(data_all_processed, channels=["5","6","7","8"]):
    """check if first and last date of all channels fit to each other
    so that every same index (iloc) corresponds to the closest measurement of the other channel
    """
    for chan in channels:
        len_chan=len(data_all_processed[chan].index)
        print()
        print(f"Channel: {chan}; Number of dates: {len_chan}")
        f_date=data_all_processed[chan].index[0]
        l_date=data_all_processed[chan].index[-1]
        print(f"first (oldes) date: {f_date}")
        print(f"last (newest) date: {l_date}")

def calc_stat_of_difference(df_diff):
    """
    calculates the mean and stdev over all dates, of a dataframe with columns as depth and rows as dates
    """
    diff_statistic=pd.DataFrame(columns=df_diff.columns,index=["mean","stdev"])
    diff_statistic.index.names=["Statistic"]
    for depth in df_diff.columns:
        data_array=np.array(df_diff[[depth]]).flatten() # transform column to numpy array
        mean=np.nanmean(data_array)
        stdev=np.nanstd(data_array)
        diff_statistic[[depth]]=[[mean],[stdev]]
    return diff_statistic