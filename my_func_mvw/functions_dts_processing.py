import pickle
import pandas as pd
import numpy as np
from datetime import timedelta
from random import randrange
import matplotlib.pyplot as plt
plt.style.use("seaborn")
import matplotlib.dates as mdates
from collections import defaultdict
from copy import deepcopy

from my_func_mvw.functions import find_nearest_date, temp_watertank_func

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
            # Temp of watertank, measured by PT-sensor
            val_watertank=temp_watertank_func([date_name], df_Tlogger, time_diff_warning=time_diff_warning)[0]
            # difference between PT-sensor and DTS at first watertank position
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
        print(f"first (oldest) date: {f_date}")
        print(f"last (newest) date: {l_date}")

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

def plot_segments_mean_correction(calibration_segments_mean_correction,dates,calibration_segments_mean_correction_dates,watertank_diff_log_data_all,df_Tlogger,watertank_len,ymax=5, ymin=-15, plot_width=16):
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
        axs.plot(x,y,label=f"correction for mean of channels {chan_legend}")

    # plot watertank Temp for comparisson
    name="Channel1_rolling_mean"
    mean = np.nanmean(df_Tlogger[name].values)
    y=df_Tlogger[name].values - mean
    x_dates=df_Tlogger[name].index
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

def diff_to_watertank(data_calc, watertank_len, watertank_T_range_min,watertank_T_range_max,df_Tlogger,find_nearest_date = find_nearest_date,shorten_input_date=False):
    """Calculate differences of corrected values to watertank
    alle variables I need and defined before are as default inputs

    pos: Temp von DTS höher als in Wassertank
    neg: Temp von DTS niedriger als in Wassertank
    """

    diff_watertank_aftercorr_alldates={}
    data_calc_shorten={} #so not the inout data is changed
    for chan in data_calc.keys():
        # df for watertank diffs of corrected values
        #diff_watertank_aftercorr = pd.DataFrame(index=watertank_len)
        diff_dic_lists={}
        date_name_dic_lists={}
        diff_dic_lists[chan]=[]
        date_name_dic_lists[chan]=[]

        if shorten_input_date:
            # find the date range of this channel, which also is covered by the T-Logger
            # Im prinzip unnötig, da corrected value eh komplett gecoverde sind von T-logger
            date_name_min, date_iloc_min = find_nearest_date(watertank_T_range_min,data_calc[chan].index,method_type="bfill")
            date_name_max, date_iloc_max = find_nearest_date(watertank_T_range_max,data_calc[chan].index,method_type="ffill")
            #all_dates_in_range_channel   = data_calc[chan].index[date_iloc_min:date_iloc_max]           
            data_calc_shorten[chan]=data_calc[chan][date_iloc_min:date_iloc_max]
        else:
            data_calc_shorten[chan]=data_calc[chan]
            
        for date_name in data_calc_shorten[chan].index:
            #date_numeric=mdates.date2num(date_name)# create numeric of date for calculations
            val_watertank=temp_watertank_func([date_name], df_Tlogger)[0]  # T of watertank, measured by PT-sensor
            # when using constshift dates which are not in watertank_func range become nan because rolling mean is nan
 
            if chan in ["5","6"] or chan in["5and6"]:
                # corrected values of DTS at watertank positions
                c_v_watertank0 = data_calc_shorten[chan][watertank_len[0]][date_name] # c_v: corrected value
                c_v_watertank1 = data_calc_shorten[chan][watertank_len[1]][date_name]
                diffs = [c_v_watertank0 - val_watertank, c_v_watertank1 - val_watertank, np.nan, np.nan]
                

            elif chan in ["7","8"] or chan in ["7and8"]: 
                # these channels are longer and contain the last two watertank positions
                # corrected values of DTS at watertank positions
                c_v_watertank0 = data_calc_shorten[chan][watertank_len[0]][date_name] # c_v: corrected value
                c_v_watertank1 = data_calc_shorten[chan][watertank_len[1]][date_name]
                c_v_watertank2 = data_calc_shorten[chan][watertank_len[2]][date_name]
                c_v_watertank3 = data_calc_shorten[chan][watertank_len[3]][date_name]
                # differences
                diffs = [c_v_watertank0 - val_watertank, c_v_watertank1 - val_watertank, c_v_watertank2 - val_watertank, c_v_watertank3 - val_watertank]
            
            elif chan in ["1","2","3","4"]:
                c_v_watertank0 = data_calc_shorten[chan][watertank_len[0]][date_name] # c_v: corrected value
                diffs=[c_v_watertank0 - val_watertank]
            
            diff_dic_lists[chan].append(diffs)
            date_name_dic_lists[chan].append(date_name)
            #diff_watertank_aftercorr[date_name] = diffs

        # save diffs to other watertank positions of this channel in dic
        diff_watertank_aftercorr_alldates[chan] = pd.DataFrame(diff_dic_lists[chan],index=date_name_dic_lists[chan],columns=watertank_len).transpose()
    
    return diff_watertank_aftercorr_alldates


