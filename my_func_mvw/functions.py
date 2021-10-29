# Here I want to store all functions which I use in multiple scripts
import glob
import pickle
import pandas as pd
import numpy as np
from datetime import timedelta
from random import randrange
import statistics
import matplotlib.pyplot as plt
plt.style.use("seaborn")
import matplotlib.dates as mdates
import matplotlib.patches as patches
from collections import defaultdict
import math
from copy import deepcopy
import plotly
import plotly.express as px
import kaleido
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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


def find_nearest_date(base_date_name,date_index, method_type="nearest"):
    """find the nearest date to base_date_name in date_index
    base_date_name: put in as str or Timestamp, I use a format like this: '2021-06-07 18:52:45'
    date_index: index of a dataframe, which contains dates
    returns:
    date_name: str
    date_iloc: position of date_name in date_index
    """
    date_iloc=date_index.get_loc(base_date_name,method=method_type)
    date_name=str(date_index[date_iloc])
    return date_name, date_iloc


def calc_diff_between_channels(data1,data2,find_nearest_date=find_nearest_date,expected_difference_minutes=13,suppress_print_output=False,method_type="nearest",diff_type_only_diff=True):
    """
    think of flipping one dataframe regarding length, because in avearaging channels one dataframe (channel 5 and 7) are flipped
    At the moment I flip outise of this function, if desired
    result: dic to store result dataframes in
    """
    result={}
    date_names_chx_list=[]
    diff_lists={}
    if diff_type_only_diff==False:
        for diff_type in ["diff_re","diff_abs","diff_re_abs","diff"]:
            diff_lists[diff_type]=[]
    elif diff_type_only_diff==True:
        diff_lists["diff"]=[]

    # loop over all dates
    for i in range(1,len(data1.index)-1): #leave put first and last date
        date_name_chy, date_iloc_chy = find_nearest_date(data1.index[i],data2.index,method_type=method_type)
        date_name_chx = data1.index[i]

        if suppress_print_output==False:
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
        # iloc faster?
        T_data1 = data1.loc[date_name_chx] #array with length as index, with all Temp. of the date
        T_data2 = data2.loc[date_name_chy]
        diff = T_data1 - T_data2#[::-1] #dont flip one here, i do it before puting the data into this function
        if diff_type_only_diff==False:
            diff_abs = abs(diff)
            diff_re = diff/((T_data1+T_data2)/2) #ist das gut das so zu machen?
            diff_re_abs = abs(diff/T_data1)

        # save date in dataframe, date (columns name) is not the mean of both dates used
        date_names_chx_list.append(date_name_chx)
        diff_lists["diff"].append(diff.values)
        if diff_type_only_diff==False:
            diff_lists["diff_re"].append(diff_re.values)
            diff_lists["diff_abs"].append(diff_abs.values)
            diff_lists["diff_re_abs"].append(diff_re_abs.values)
        
    
    result["diff"]= pd.DataFrame(diff_lists["diff"],index=date_names_chx_list,columns=diff.index).transpose()
    if diff_type_only_diff==False:
        result["diff_abs"]= pd.DataFrame(diff_lists["diff_abs"],index=date_names_chx_list,columns=diff_abs.index).transpose()
        result["diff_re"]= pd.DataFrame(diff_lists["diff_re"],index=date_names_chx_list,columns=diff_re.index).transpose()
        result["diff_re_abs"]= pd.DataFrame(diff_lists["diff_re_abs"],index=date_names_chx_list,columns=diff_re_abs.index).transpose()
    return result


def watertank_shift(dataframe, df_Tlogger, watertank_len, watertank_T_range_min, watertank_T_range_max, channels=["5","6","7","8"], find_nearest_date=find_nearest_date, time_diff_warning=5):
    """shift the data to the temperature of the watertank, at first watertank position"""
    val_watertank_ch={}
    diff_in_watertank={}
    corrected_val={} # dic for different channel, containing the dataframe of the corrected values
    watertank_diff_log={}
    for chan in channels:
        c_v_list=[]
        c_v_list_datenames=[]
        df_c_v = pd.DataFrame(columns=dataframe[chan].columns) # df for the corrected values
        df_c_v.index.name="Date"

        df_watertank_diff_log=pd.DataFrame(columns=[watertank_len[0]])

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
            val_watertank=temp_watertank_func([date_name], df_Tlogger, time_diff_warning=time_diff_warning)[0]
            # difference between PT100 and DTS at first watertank position
            # round values may be helpfull for reducing memory, 
            # decimal of 2 would be sufficient for the data accuaracy.
            diff_in_watertank[chan] = val_watertank_ch[chan] - val_watertank
            #swapped index and columns compared t an older version
            #df_watertank_diff_log[date_name] = diff_in_watertank[chan] # save the difference
            df_watertank_diff_log=pd.concat([df_watertank_diff_log,pd.DataFrame(diff_in_watertank[chan],index=[date_name],columns=[watertank_len[0]])])


            # correct watertank diff; for all DTS points, based on first watertank position
            chan_val = np.array(dataframe[chan].loc[str(date_name)].values) # uncorrected DTS Temp
            # save corrected values in dataframe; c_v: corrected_value
            #df_c_v[date_name] = chan_val - diff_in_watertank[chan] # performance warning
            #df_c_v.loc[date_name]=chan_val - diff_in_watertank[chan] # very slow: addind values row by row to a dataframe is slow!
            c_v_list.append(chan_val - diff_in_watertank[chan])
            c_v_list_datenames.append(date_name)

        # save corected values of the channel in dic
        corrected_val[chan] = pd.DataFrame(c_v_list, columns=dataframe[chan].columns, index=c_v_list_datenames) # same format as data_all
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

def temp_watertank_func(x, df_Tlogger, channel_name = "Channel1-PT100_rolling_mean", time_diff_warning=5):
    """returns Temperature of Watertank at given time x, of the moving avearage values
    this is not really a matheamtical function, but I named it like this when I was using a polynomial function

    x should be a list
    """
    # find nearest date in moving avearge
    temp = []
    for date in x:
        date_name, date_iloc = find_nearest_date(date,df_Tlogger[channel_name].index)
        Temperature = df_Tlogger[channel_name][date_name]
        Temperature_round = round(Temperature, 7) #round to 7s decimal place
        temp.append(Temperature_round)

        # check timediff
        timediff = date - pd.to_datetime(date_name)
        if date > pd.to_datetime(date_name):
            if timediff > timedelta(minutes=time_diff_warning):
                print(f"Warning1 from temp_watertank_func: timediff larger than {time_diff_warning} minutes: {timediff} at requested date of: {date}")
        elif date < pd.to_datetime(date_name):
            if -(timediff) > timedelta(minutes=time_diff_warning):
                print(f"Warning2 from temp_watertank_func: timediff larger than {time_diff_warning} minutes: {timediff} at requested date of: {date}")


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


def cut_dataframe_to_range_tlogger(channels, data, watertank_T_range_min, watertank_T_range_max, check_first_last_date=check_first_last_date, do_check=True, find_nearest_date=find_nearest_date):
    """Cut dataframes so they only cover the time of the t-Logger"""
    data_processed = {}
    date_iloc_min_list=[]
    date_iloc_max_list=[]
    for chan in channels:
        date_name_min, date_iloc_min = find_nearest_date(watertank_T_range_min,data[chan].index)
        date_name_max, date_iloc_max = find_nearest_date(watertank_T_range_max,data[chan].index)
        #all_dates_in_range_channel   = data[chan].index[date_iloc_min:date_iloc_max]
        date_iloc_max_list.append(date_iloc_max)
        date_iloc_min_list.append(date_iloc_min)
        #print(chan);print(date_iloc_min);print(date_iloc_max);print()
    #range dates which has to be applied to all channels. Channels have been "alligned" regarding the date before. To keep this allignmend datepoints of all channels have to be dropped togehter. So the channel which has the newest first date in t-logger date range is important.[-->max(date_iloc_min_list)] And the channel which has the oldest last date in t-logger range is important. [-->min(date_iloc_max_list)]
    date_iloc_max = min(date_iloc_max_list)
    date_iloc_min = max(date_iloc_min_list)
    # drop the dates which are not covered by t-logger
    if channels == ["5and6","7and8"] or channels == ["7and8","5and6"]:
        # cut is different for each channel
        counter_chan=0
        for chan in channels:
            data_processed[chan] = data[chan].drop(data[chan].index[0:date_iloc_min_list[counter_chan]],axis=0)
            new_max_index = date_iloc_max_list[counter_chan] - date_iloc_min_list[counter_chan] # I already dropped some values, therefore the index changed
            data_processed[chan] = data_processed[chan].drop(data_processed[chan].index[new_max_index:],axis=0)
            counter_chan+=1
    else:
        # cut is the same for all channels
        for chan in channels:
            data_processed[chan] = data[chan].drop(data[chan].index[0:date_iloc_min],axis=0)
            new_max_index = date_iloc_max - date_iloc_min # I already dropped some values, therefore the index changed
            data_processed[chan] = data_processed[chan].drop(data_processed[chan].index[new_max_index:],axis=0)
    
    if do_check:
        check_first_last_date(data_processed, channels=channels)

    return data_processed

def check_processed_data(channels,data_all_processed, gap_begin=1661, gap_end=2137, my_Warning=False):
    """some checks for my processed data
    channels has to be in order
    """
    # check if all channels have the same number of date points (index length)
    def helper_dates_not_equal_zero(chan,other_chan, my_Warning):
        n_dates_difference = n[chan] - n[other_chan]
        if n_dates_difference != 0:
            my_Warning = True
            print(f"Channel {chan} and Chanel {other_chan} have a different index length --> different number of dates")
        return my_Warning
    
    n={}
    for chan in channels:
        n[chan]=len(data_all_processed[chan].index) # number of date points of this channel
    if channels == ["1","2","3","4"]:
        for chan in n:
            for other_chan in n: # it also counts the channel of the upper loop but thats not important
                my_Warning = helper_dates_not_equal_zero(chan, other_chan, my_Warning)
    elif channels == ["5","6","7","8"]:
        for chan in ["5","7"]:
            if chan == "5":
                other_chan = "6"
            elif chan == "7":
                other_chan = "8"
            my_Warning = helper_dates_not_equal_zero(chan, other_chan, my_Warning)
    print("Check timedifferences between channels: done")
    #------------------------------------------------------------------------------------------------------------------------------
    # check if the first measurement of channel 1 has the oldest measurement and the first of channel 8 the newest
    a=data_all_processed # for shortening code
    if a[channels[0]].index[0] < a[channels[1]].index[0] and a[channels[1]].index[0] < a[channels[2]].index[0] and a[channels[2]].index[0] < a[channels[3]].index[0]:
        #print("order of first dates is good")
        pass
    else:
        my_Warning = True
        print("!order of first dates is not good!")
    # check last dates
    if a[channels[0]].index[-1] < a[channels[1]].index[-1] and a[channels[1]].index[-1] < a[channels[2]].index[-1] and a[channels[2]].index[-1] < a[channels[3]].index[-1]:
        #print("order of last dates is good")
        pass
    else:
        my_Warning = True
        print("!order of last dates is not good!")
    print("Check first and last date: done")
    #------------------------------------------------------------------------------------------------------------------------------
    # check all date differences
    allowed_diff_5_min={}
    allowed_diff_9_min={}
    allowed_diff_13_min={}

    if channels == ["1","2","3","4"]:
        allowed_diff_5_min["2 - 1"]  = a["2"].index - a["1"].index
        allowed_diff_5_min["3 - 2"]  = a["3"].index - a["2"].index
        allowed_diff_5_min["4 - 3"]  = a["4"].index - a["3"].index
        allowed_diff_9_min["4 - 2"]  = a["4"].index - a["2"].index
        allowed_diff_9_min["3 - 1"]  = a["3"].index - a["1"].index
        allowed_diff_13_min["4 - 1"] = a["4"].index - a["1"].index

    elif channels == ["5","6","7","8"]:
        # drop some dates for the check, because 5 and 6 have a data gap in between due to EGRT from Solexperts
        # now added as input
        # gap_begin=1928
        # gap_end=2404
        # # gap_begin=1661
        # # gap_end=2137
        allowed_diff_5_min["6 - 5"]  = a["6"].index - a["5"].index
        allowed_diff_5_min["7 - 6"]  = a["7"].index.drop(a["7"].index[gap_begin : gap_end]) - a["6"].index
        allowed_diff_5_min["8 - 7"]  = a["8"].index - a["7"].index
        allowed_diff_9_min["8 - 6"]  = a["8"].index.drop(a["8"].index[gap_begin : gap_end]) - a["6"].index
        allowed_diff_9_min["7 - 5"]  = a["7"].index.drop(a["7"].index[gap_begin : gap_end]) - a["5"].index
        allowed_diff_13_min["8 - 5"] = a["8"].index.drop(a["8"].index[gap_begin : gap_end]) - a["5"].index

    def print_timediff_warning(channelpair, timediff, index_counter):
        print("timediff between two dates is not in expected range")
        print(f"in Channel {channelpair}: {timediff}")
        print(f"At Index: {index_counter}")
        print()
    
    def check_diff_dics(allowed_diff_x_min,minut,print_timediff_warning=print_timediff_warning, my_Warning = my_Warning):
        for channelpair in allowed_diff_x_min:
            index_counter=0
            for timediff in allowed_diff_x_min[channelpair]:
                #-before second timedelta to allow timediff of 0
                if timediff > timedelta(minutes=minut) or timediff < timedelta(minutes=minut-1):
                    print_timediff_warning(channelpair, timediff, index_counter)
                    my_Warning = True
                index_counter+=1
        return my_Warning

    my_Warning = check_diff_dics(allowed_diff_5_min, minut=5)
    my_Warning = check_diff_dics(allowed_diff_9_min, minut=9)
    my_Warning = check_diff_dics(allowed_diff_13_min,minut=13) # has only one channelpair
    print("Check number date measurements: done")
    #------------------------------------------------------------------------------------------------------------------------------
    if my_Warning == True: # Print Warning if one check was wrong
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!Do the manual check again!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        print("All checks passed")

    return my_Warning

def calc_mean_for_each_segment(channels, calibration_segments, watertank_diff_log_data_all, watertank_len, find_nearest_date=find_nearest_date):
    """
    measurements close to borders are left out.
    the returned date variable also left put dates!
    """
    # erstmal checken ob segment in logger range ist, sonst vorheriges nehmen

    calibration_segments_mean_correction = {} # same order as in calibration_segments
    calibration_segments_mean_correction_dates = {}
    for chan in channels:
        segment_mean_list = []
        segment_dates_list = []
        for segment in calibration_segments:
            start_date=segment[0]
            end_date=segment[1]
            chan_dates = watertank_diff_log_data_all[chan][watertank_len[0]].index
            date_name_start, date_iloc_start = find_nearest_date(start_date,chan_dates)
            date_name_end, date_iloc_end = find_nearest_date(end_date,chan_dates)

            data = watertank_diff_log_data_all[chan][watertank_len[0]]
            #leave out measurement close to border
            segment_mean = np.nanmean(data[date_iloc_start+5:date_iloc_end-5])
            segment_mean_list.append(segment_mean)
            segment_dates_list.append([date_iloc_start+5,date_iloc_end-5])
        calibration_segments_mean_correction[chan] = segment_mean_list
        calibration_segments_mean_correction_dates[chan] = segment_dates_list
    
    return calibration_segments_mean_correction, calibration_segments_mean_correction_dates

def plot_segments_mean_correction(calibration_segments_mean_correction,dates,calibration_segments_mean_correction_dates,watertank_diff_log_data_all,df_Tlogger_PT100,watertank_len,ymax=5, ymin=-15, plot_width=16):
    """"""
    fig,axs=plt.subplots(1,1,figsize=(plot_width,5))
    # Plot border calibration segments
    plt.vlines(dates,ymin,ymax,colors="black",linestyle=":", label="correction segment borders")

    # Plot mean shift for calibration segments seperate
    for chan in calibration_segments_mean_correction.keys():
        segment_number=0
        for segment_mean in calibration_segments_mean_correction[chan]:
            date_border = calibration_segments_mean_correction_dates[chan][segment_number]
            x=watertank_diff_log_data_all[chan].index[date_border[0]:date_border[1]]
            if x.size != 0: # some segments can be empty for some channels (channel 5 and 6 data gap EGRT)
                start = x[0]
                end = x[-1]
                # at beginning there was no watertank so my x determination is not good,
                # in generall its good to use the extra step with x to make sure data exists, 
                # I could also just use date_border in hlines
                if segment_number == 0:
                    start = pd.to_datetime("2021-06-01 19:00:00")
                axs.hlines(segment_mean, start, end, color="black", linestyle="--", label="mean correction")
            segment_number+=1

        x=watertank_diff_log_data_all[chan].index
        y=watertank_diff_log_data_all[chan][watertank_len[0]]
        if chan in ["5and6","7and8"]:
            chan_legend=f"{chan[0]} {chan[1:4]} {chan[4]}"
        else:
            chan_legend=chan
        axs.plot(x,y,label=f"correction for channel {chan_legend}")

    # plot watertank Temp for comparisson
    name="Channel1-PT100_rolling_mean"
    mean = np.nanmean(df_Tlogger_PT100[name].values)
    y=df_Tlogger_PT100[name].values - mean
    x_dates=df_Tlogger_PT100[name].index
    axs.plot(x_dates,y,color="black", label="water tank\nshifted to mean = 0")


    # Erstmal weglassen im Plot
    # plot avearagefirst watertank shift
    # for chan in watertank_diff_log_avearagefirst.keys():
    #     y=watertank_diff_log_avearagefirst[chan].loc[watertank_len[0]]
    #     x=watertank_diff_log_avearagefirst[chan].columns
    #     axs.plot([x[0],x[-1]],[y.mean(),y.mean()],color="black",linestyle="--")
    #     plt.plot(x,y,label=f"Correction for avearagefirst: {chan}")

    axs.set_ylabel("Temperature [°C]")
    axs.set_ylim(ymin,ymax)
    # get labels for legend to remove duplicates
    # https://stackoverflow.com/questions/13588920/stop-matplotlib-repeating-labels-in-legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles)) # but them in dictionary: uniqueness, multiple labels are dropped
    # make legend looking nicer
    legend = axs.legend(by_label.values(), by_label.keys(),fontsize=11, title_fontsize=12,frameon=True) #loc="upper right"
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.7) #not supported with eps
    #plt.show()

def const_shift_data(channels,calibration_segments, calibration_segments_mean_correction,data_all_processed, find_nearest_date=find_nearest_date,round_x=1):
    """"""
    data_all_processed_constshifted = {}
    for chan in channels:
        data_all_processed_constshifted_parts = defaultdict(dict)
        for i_segment in range(len(calibration_segments_mean_correction[chan])):
            #date = calibration_segments_mean_correction_dates[chan][i_segment] # dates where the mean was calculated with

            # date border of segment
            date_begin = calibration_segments[i_segment][0]
            date_end = calibration_segments[i_segment][1]
            # date border of segment for this channel
            # exact match is always used, independent of method_type
            date_begin_chan, date_begin_chan_iloc = find_nearest_date(date_begin, data_all_processed[chan].index, method_type="bfill") #bfill
            date_end_chan, date_end_chan_iloc = find_nearest_date(date_end, data_all_processed[chan].index, method_type="ffill")

            # Correct data
            raw_data_segment = data_all_processed[chan][date_begin_chan_iloc : date_end_chan_iloc + 1]
            mean_correction_segment = calibration_segments_mean_correction[chan][i_segment]
            # if i_segment == 1: #EGRT Segment
            #     # not much watertank measurements and they are not good for coorrecting
            #     # Therfore, look at raw data and calculate difference to segment before
                

            #use for egrt segment other solution because it has so few watertank measurements
            #or use solexperts watertank measurements and add them to my tlogger dataframe
            # bringt aber im endeffekt auch nichts weil die korrektur eh falsch wäre dann
            data_all_processed_constshifted_parts[chan][i_segment] = raw_data_segment - mean_correction_segment
        
        # concat all parts in one dataframe
        final_dataframe = data_all_processed_constshifted_parts[chan][0]
        for i_segment in list(data_all_processed_constshifted_parts[chan].keys())[1:]:
            final_dataframe = pd.concat([final_dataframe, data_all_processed_constshifted_parts[chan][i_segment]])

        data_all_processed_constshifted[chan] = round(final_dataframe,round_x)

    return data_all_processed_constshifted

def add_nan_val_in_datagaps(data_chan, minutes_gap=35):
    """biggest problem the searching for gaps is static.
    But when measurement sheme of dts device changes this is not valid.
    I do not plan to change this because I just need this function for nicer looking plots
    Solution: resample dataframe to bigger timegapps"""
    data_chan_new=deepcopy(data_chan)
    diff = data_chan.index[1:] - data_chan.index[:-1]
    
    index_datagaps=[]
    for i in range(len(diff)):
        bo = diff[i] > timedelta(minutes=minutes_gap)
        if bo == True:
            index_datagaps.append(i)
            #print(i)#;print(diff[i]) #i gibt einem die position des Datums ab welchem danach die Lücke ist

    # add values in data gaps
    n_appended_values = 0 # count the number of values I add to the dataframe
    for index in index_datagaps:
        index_corrected = index + n_appended_values # the dataframe gets new values in other date gaps before this one
        # number of dates with nan, that will be added behin the index position
        # round down and minus 1 to be sure I dont add a nan behind an existing date - deleted this feature
        n_nan_dates = math.floor(diff[index] / timedelta(minutes=minutes_gap))
        n_appended_values += n_nan_dates
        list_nan = [np.nan] * n_nan_dates # list of nan

        # add nan's in data gaps, by creating new datapoints with a timedifference of 32 min.
        # create dataframe which contains the dates and nan values
        #new_val = pd.DataFrame({data_chan.columns[0]: list_nan, df_Tlogger.columns[1]: list_nan}) #, df_Tlogger.columns[2]: list_nan}
        #new_val.index = [data_chan.index[index_corrected] + timedelta(minutes=x*35) for x in range(1,n_nan_dates+1)]
        new_index = [data_chan_new.index[index_corrected] + timedelta(minutes=x*minutes_gap) for x in range(1,n_nan_dates+1)]
        new_val=pd.DataFrame(index=new_index,columns=data_chan.columns)
        

        # add nan values to dataframe and sort it
        data_chan_new = pd.concat([data_chan_new, new_val],axis=0).sort_index()
    print(f"{n_appended_values} dates with nan have been added")


    # Check if everything worked correct
    # find data gaps
    diff = data_chan_new.index[1:] - data_chan_new.index[:-1]
    for i in range(len(diff)):
        bo = diff[i] > timedelta(minutes=minutes_gap)
        if bo == True:
            print("There are still some indexes missing:")
            print(i);print(diff[i]);print() #i gibt einem die position des Datums ab welchem danach die Lücke ist
    
    return data_chan_new

def carpet_plot_with_gaps(data_input,channels,title_prefix="",sample_hours=3,add_nan_val_in_datagaps=add_nan_val_in_datagaps,
                         vmin = 15, vmax = 35):
    """you shouldnt use sample_hours smaller than 1. Could cause unexpected behaviour."""
    # add nan values in gaps so the gaps appear in the plots
    data_all_processed_nan={}
    for chan in channels:
        print(chan)
        data_all_processed_nan[chan] = add_nan_val_in_datagaps(data_input[chan])
        print()

    # Check my processed data - check function needs to be slightly adapted
    #just_for_test={}
    #for chan in ["5","6","7","8"]:
    #    just_for_test[chan]=data_all_processed_nan[chan].resample("3H").ffill()
    #my_Warning = check_processed_data(channels=["5","6","7","8"], data_all_processed = just_for_test,gap_begin=0,gap_end=0)

    fig,axs=plt.subplots(len(channels),1,figsize=(16,len(channels)*5))
    ax_num=0
    for chan in channels:
        data=data_all_processed_nan[chan].resample(f"{sample_hours}H").ffill()
        print(f"Number of dates in Channel {chan}: {len(data.index)}")
        depth=data.columns
        date = data.index.to_series()
        # Datum-Ticks auf x-Achse und Farbskala
        starti = depth[0]
        stopi = depth[-1]
        xax3 = mdates.date2num(date)
        xstart = xax3[0]
        xstop  = xax3[-1]

        if chan in ["5and6","7and8"]:
            title_chan=f"{chan[0]} {chan[1:4]} {chan[4]}"
        else:
            title_chan=chan
        axs[ax_num].set_title(title_prefix + f'of channel {title_chan}', fontsize = 12) #\nresampled to {sample_hours} hour
        axs[ax_num].grid(False) #axs[0,1].grid(color = '#10366f', alpha = 0.1)
        caxa = axs[ax_num].imshow(data.transpose(), interpolation = 'gaussian', extent = [xstart, xstop, stopi, starti],
                        cmap = 'viridis', aspect = 'auto', vmin = vmin, vmax = vmax) 
        axs[ax_num].set_ylabel("Length [m]")
        axs[ax_num].tick_params(axis="x", which='both',length=4,color="grey")
        ax_num+=1

    cbax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    cbar = fig.colorbar(caxa, cax = cbax, orientation = 'vertical', fraction = 0.05, pad = - 0.05)
    cbar.set_label('Temperature [°C]', rotation = 0, fontsize = 9, labelpad = -20,  y = 1.03)

    if channels == ["5and6","7and8"]:
        axs[0].sharex(axs[1])
        axs[1].tick_params(axis = 'x', labelrotation = 0)
        axs[1].xaxis_date()
        date_format = mdates.DateFormatter('%Y-%m-%d')
        axs[1].xaxis.set_major_formatter(date_format)

    else:
        axs[0].sharex(axs[3])
        axs[1].sharex(axs[3])
        axs[2].sharex(axs[3])

        axs[3].tick_params(axis = 'x', labelrotation = 0)
        axs[3].xaxis_date()
        date_format = mdates.DateFormatter('%Y-%m-%d')
        axs[3].xaxis.set_major_formatter(date_format)

def save_values_in_file(file_line, name, value, path_to_file):
    """saves a value in a txt file, can then be read with latex
    the fileline is overwritten and must exists"""
    with open(path_to_file, 'r') as file:
        # read a list of lines into data
        values_for_read_in_tex = file.readlines()

    values_for_read_in_tex[file_line] = f"{name} = {value} \n"

    with open(path_to_file, 'w') as file:
        file.writelines(values_for_read_in_tex)

def statistic_plot(data_shaft,date_min_max=[61650,62200],c="1",temp_ax_min=22, temp_ax_max=26, sample_hours = 1):
    """Copied / Inspired by Daniels plot"""
    header_fontsize=12
    legend_font=10
    shaft_nan_chan = data_shaft[c][date_min_max[0]:date_min_max[1]]
    shaft_nan_chan = add_nan_val_in_datagaps(shaft_nan_chan)

    data_down=shaft_nan_chan.resample(f"{sample_hours}H").mean()#ffill()

    depth = data_down.columns
    # for every depth minimum along all dates

    tempmin = data_down.min(axis = 0)
    tempmax = data_down.max(axis = 0)
    tempmean = data_down.mean(axis = 0)
    tempstd = data_down.std(axis = 0)

    fig , axs=plt.subplots(2,2,figsize=[14,7]) #, sharey = True #,constrained_layout=True
    # Make one axes out of two subplots
    gs = axs[1, 0].get_gridspec()
    fig.delaxes(axs[0,0])
    fig.delaxes(axs[1,0])
    big_axs = fig.add_subplot(gs[:, 0])

    # 1. Axes
    big_axs.set_title('Statistic Temperature Over Time', fontsize = header_fontsize)
    big_axs.plot(tempmean, depth, color='#10366f', alpha = 0.8, label = 'mean')
    big_axs.fill_betweenx(depth, tempmin, tempmax,
                    #facecolor="blue",           # The fill color
                    color='#7fc7ff',             # The outline color
                    alpha=0.3, label = 'min - max') # Transparency of the fill
    big_axs.fill_betweenx(depth, tempmean - tempstd, tempmean + tempstd,
                    # facecolor="#1CB992",       # The fill color
                    color="#c52b2f",             # The outline color
                    alpha=0.3, label = 'standart deviation') # Transparency of the fill

    big_axs.set_ylim([(depth.max() + 0.05 * (depth.max()-depth.min())), 
                    (depth.min() - 0.05 * (depth.max() - depth.min()))])
    
    big_axs.set_ylabel("Depth [m]",fontsize=legend_font)
    big_axs.set_xlabel("Temperature [°C]",fontsize=legend_font)
    big_axs.set_xlim(temp_ax_min,temp_ax_max)
    big_axs.set_ylim(depth[-1],depth[0])
    legend = big_axs.legend(fontsize=11, title_fontsize=11,frameon=True)
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.7) #not supported with eps

    # 2. Axes
    date = data_down.index.to_series()
    # Datum-Ticks auf x-Achse und Farbskala
    starti = depth[0]
    stopi = depth[-1]
    xax3 = mdates.date2num(date)
    xstart = xax3[0]
    xstop  = xax3[-1]

    axs[0,1].set_title('Temperature in Shaft', fontsize = header_fontsize)
    axs[0,1].tick_params(axis = 'x', labelrotation = 30, labelcolor = 'w')
    axs[0,1].grid(False) #axs[0,1].grid(color = '#10366f', alpha = 0.1)
    caxa = axs[0,1].imshow(data_down.transpose(), interpolation = 'gaussian', extent = [xstart, xstop, stopi, starti],
                    vmin = temp_ax_min, vmax = temp_ax_max, cmap = 'viridis', aspect = 'auto')
    cbax = fig.add_axes([0.92, 0.5, 0.015, 0.38])
    cbar = fig.colorbar(caxa, cax = cbax, orientation = 'vertical', fraction = 0.05, pad = - 0.05)
    cbar.set_label('Temp [°C]', rotation = 0, fontsize = 9, labelpad = -20,  y = 1.08)
    axs[0,1].set_ylabel("Depth [m]",fontsize=legend_font)
    #axs[0,1].sharey(big_axs)

    # 3. Axes
    axs[1,1].set_title('Mean Temperature in Shaft', fontsize = header_fontsize)
    axs[1,1].set_ylabel('Temperature [°C]',fontsize=legend_font)
    axs[1,1].tick_params(axis = 'x', labelrotation = 30)
    axs[1,1].set_ylim(temp_ax_min, temp_ax_max)
    axs[1,1].plot(data_down.mean(axis = 1), color = '#10366f', alpha = 0.9, label = 'DTS-Temperatur')
    axs[1,1].sharex(axs[0,1])
    axs[1,1].xaxis_date()
    date_format = mdates.DateFormatter('%Y-%m-%d')
    axs[1,1].xaxis.set_major_formatter(date_format)

    axs[1,1].tick_params(axis="x", which='both',length=4,color="grey")
    axs[0,1].tick_params(axis="x", which='both',length=4,color="grey")

def plot_water_rise(data,plot_save,linear_curve=[163,0.008],zminmax=[22,24],title="",data_type="chan14"):
    """linear_curve: [start_depth, m]"""
    #data plot
    if title=="Diff.":
        trace1=go.Heatmap(
            x=data.index,
            y=data.columns,
            z=data.transpose(),
            name=f"Temperature {title}",
            yaxis='y',zmin=zminmax[0],zmax=zminmax[1],colorbar={"title":f"Temp. [°C]"},
            colorscale='gray',reversescale=True
            )#,zmin=20,zmax=24,labels={"color":"Temp. °C"}) #,cmap={"title":"Dept]"}
    else:
        trace1=go.Heatmap(
            x=data.index,
            y=data.columns,
            z=data.transpose(),
            name=f"Temperature {title}",
            yaxis='y',zmin=zminmax[0],zmax=zminmax[1],colorbar={"title":f"Temp. [°C]"},
            colorscale='thermal'
            )#,zmin=20,zmax=24,labels={"color":"Temp. °C"}) #,cmap={"title":"Dept]"}

    #Linear fit
    datetonum=mdates.date2num(data.index)#[:-300]
    m=linear_curve[1] #[m / datetonum pixel]
    timediff=data.index[0] - data.index[-1]
    years=abs(timediff.days /365.25) #years in measurement time
    m_measurement_time=m*(datetonum[-1]-datetonum[0]) #[m / complete_time]
    m_year=m_measurement_time/years #[m / a]
    start_depth=linear_curve[0]
    ground_water_depth_fit=start_depth-m*(datetonum-datetonum[0])

    #linear fit plot
    trace2 = go.Scatter(
        x=data.index,
        y=ground_water_depth_fit, #np.ones(len(data.index))*150
        name='line fit',
        yaxis='y',
        fillcolor="blue",
        line={"color":"blue","dash":"dash","width":3},
        )
    #horizontal line as reference
    trace3 = go.Scatter(
        x=data.index,
        y=np.ones(len(data.index))*linear_curve[0], #
        name='line horizontal',
        yaxis='y',
        fillcolor="black",
        line={"color":"green","dash":"dot","width":3},
        )
    #Quadratic fit
    a=-0.008
    h=20000
    k=140
    x=datetonum-datetonum[0]
    ground_water_depth_fit_quadratic=a*(x-h)**2+k
    start_depth-m*(datetonum-datetonum[0])

    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2,secondary_y=False)
    fig.add_trace(trace3,secondary_y=False)
    fig.update_layout(yaxis = {"autorange":"reversed","title":"Depth [m]"},showlegend=False)

    if plot_save:
        if title=="Diff." and data_type=="chan14":
            filename=f"\\carpet_ch14_shaft_water_rise_diff.pdf"
        elif title=="" and data_type=="chan14":
            filename=f"\\carpet_ch14_shaft_water_rise.pdf"
        elif title=="Diff." and data_type=="chan58":
            filename=f"\\carpet_ch58_shaft_water_rise_diff.pdf"
        elif title=="" and data_type=="chan58":
            filename=f"\\carpet_ch58_shaft_water_rise.pdf"
        fig.write_image(r"..\Masterthesis_tex\figs\chap4" + filename,width=1120, height=500)
    
    fig.show()

    print(f"fitted water level rise: {round(m_year,1)} m / year") #global sea level rise 1900 to 2017: 1.4–1.8 mm per year
    print(f"this is a total of {round(m_measurement_time,1)} m in the measurement time")

def create_mask_egrt(dataframe,start_date_string="13.07.2021",end_date_string="23.07.2021",find_nearest_date=find_nearest_date):
    """create mask which contains True if not a EGRT date"""
    date_name_start,date_iloc_start=find_nearest_date(pd.to_datetime(start_date_string,dayfirst=True),dataframe.index)
    date_name_end,date_iloc_end=find_nearest_date(pd.to_datetime(end_date_string,dayfirst=True),dataframe.index)
    egrt_dates=dataframe.index[date_iloc_start:date_iloc_end]

    mask_not_egrt=[False if x in egrt_dates else True for x in dataframe.index]
    return mask_not_egrt

