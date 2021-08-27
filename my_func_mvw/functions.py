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

def temp_watertank_func(x, df_Tlogger, channel_name = "Channel1-PT100_rolling_mean"):
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
            if timediff > timedelta(minutes=5):
                print("Warning1 from temp_watertank_func: timediff larger than 5 minutes")
        elif date < pd.to_datetime(date_name):
            if -(timediff) > timedelta(minutes=5):
                print("Warning2 from temp_watertank_func: timediff larger than 5 minutes")


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
    
    def check_diff_dics(allowed_diff_x_min,min,print_timediff_warning=print_timediff_warning, my_Warning = my_Warning):
        for channelpair in allowed_diff_x_min:
            index_counter=0
            for timediff in allowed_diff_x_min[channelpair]:
                if timediff > timedelta(minutes=min) or timediff < timedelta(minutes=min-1):
                    print_timediff_warning(channelpair, timediff, index_counter)
                    my_Warning = True
                index_counter+=1
        return my_Warning

    my_Warning = check_diff_dics(allowed_diff_5_min, min=5)
    my_Warning = check_diff_dics(allowed_diff_9_min, min=9)
    my_Warning = check_diff_dics(allowed_diff_13_min,min=13) # has only one channelpair
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
            chan_dates = watertank_diff_log_data_all[chan].loc[watertank_len[0]].index
            date_name_start, date_iloc_start = find_nearest_date(start_date,chan_dates)
            date_name_end, date_iloc_end = find_nearest_date(end_date,chan_dates)

            data = watertank_diff_log_data_all[chan].loc[watertank_len[0]]
            #leave out measurement close to border
            segment_mean = np.nanmean(data[date_iloc_start+5:date_iloc_end-5])
            segment_mean_list.append(segment_mean)
            segment_dates_list.append([date_iloc_start+5,date_iloc_end-5])
        calibration_segments_mean_correction[chan] = segment_mean_list
        calibration_segments_mean_correction_dates[chan] = segment_dates_list
    
    return calibration_segments_mean_correction, calibration_segments_mean_correction_dates

def plot_segments_mean_correction(calibration_segments_mean_correction,dates,calibration_segments_mean_correction_dates,watertank_diff_log_data_all,df_Tlogger_PT100,watertank_len,ymax=5, ymin=-15):
    """"""
    fig,axs=plt.subplots(1,1,figsize=(16,5))
    # Plot border calibration segments
    plt.vlines(dates,ymin,ymax,colors="black",linestyle=":", label="correction segment borders")

    # Plot mean shift for calibration segments seperate
    for chan in calibration_segments_mean_correction.keys():
        segment_number=0
        for segment_mean in calibration_segments_mean_correction[chan]:
            date_border = calibration_segments_mean_correction_dates[chan][segment_number]
            x=watertank_diff_log_data_all[chan].columns[date_border[0]:date_border[1]]
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

        x=watertank_diff_log_data_all[chan].columns
        y=watertank_diff_log_data_all[chan].loc[watertank_len[0]]
        axs.plot(x,y,label=f"correction for channel {chan}")

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

    axs.set_title("Analyse Water Tank Correction", fontsize=13)
    axs.set_xlabel("Date")
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

def const_shift_data(channels,calibration_segments, calibration_segments_mean_correction,data_all_processed, find_nearest_date=find_nearest_date):
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
            date_begin_chan, date_begin_chan_iloc = find_nearest_date(date_begin, data_all_processed[chan].index, method_type="bfill")
            date_end_chan, date_end_chan_iloc = find_nearest_date(date_end, data_all_processed[chan].index, method_type="ffill")

            # Correct data
            raw_data_segment = data_all_processed[chan][date_begin_chan_iloc : date_end_chan_iloc]
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

        data_all_processed_constshifted[chan] = round(final_dataframe,1)

    return data_all_processed_constshifted