# Here multiple functions are stored
import glob
import pickle
import pandas as pd
import numpy as np
from datetime import timedelta
from random import randrange
import matplotlib.pyplot as plt
plt.style.use("seaborn")
import matplotlib.dates as mdates
from collections import defaultdict
import math
from copy import deepcopy
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

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

def file_len(fname):
    """returns the number of lines of a file"""
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def number_files(path):
    """counts the number of files in the repository"""
    total = 0
    for root, dirs, files in os.walk(path):
        total += len(files)
    return total

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
        # round down to be sure I dont add a nan behind an existing date - deleted this feature
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

def read_pickle(filename:str):
    #Function to read pickle Files
    with open(filename, 'rb') as f:
        return pickle.load(f)

def write_pickle(path,data):
    with open(path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def temp_watertank_func(x, df_Tlogger, channel_name = "Channel1_rolling_mean", time_diff_warning=5):
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
        if title_prefix=="":
            channel_string="Channel"
        else:
            channel_string="channel"
        axs[ax_num].set_title(title_prefix  + f'{channel_string} {title_chan}', fontsize = 12,loc="left") #\nresampled to {sample_hours} hour
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

def plot_water_rise(data,plot_save,linear_curve=[163,0.008],zminmax=[22,24],title="",data_type="chan14",show_additional_water_level_info=True):
    """linear_curve: [start_depth, m]"""
    #data plot
    if title=="Diff.":
        trace1=go.Heatmap(
            x=data.index,
            y=data.columns,
            z=data.transpose(),
            name=f"Temperature {title}",
            yaxis='y',zmin=zminmax[0],zmax=zminmax[1],colorbar={"title":f"Temp. [K]"},
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
    #points with water level information from other sources
    if show_additional_water_level_info:
        date_2020_wireline=pd.to_datetime("2020-11-24 12:00:00")
        water_level_wireline2020=158.5
        trace4 = go.Scatter(
            x=[date_2020_wireline],
            y=[water_level_wireline2020],
            name='additional water level info',
            yaxis='y',
            # fillcolor="black",
            mode="markers",
            marker={"color":"blue","size":15}
            )

    # # Quadratic fit - not used
    # a=-0.008
    # h=20000
    # k=140
    # x=datetonum-datetonum[0]
    # ground_water_depth_fit_quadratic=a*(x-h)**2+k
    # start_depth-m*(datetonum-datetonum[0])

    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2,secondary_y=False)
    fig.add_trace(trace3,secondary_y=False)
    if show_additional_water_level_info:
        fig.add_trace(trace4,secondary_y=False)
    fig.update_layout(yaxis = {"autorange":"reversed","title":"Depth [m]"},showlegend=False)

    if plot_save:
        if title=="Diff." and data_type=="chan14":
            filename=f"\\carpet_ch14_shaft_water_rise_diff"
        elif title=="" and data_type=="chan14":
            filename=f"\\carpet_ch14_shaft_water_rise"
        elif title=="Diff." and data_type=="chan58":
            filename=f"\\carpet_ch58_shaft_water_rise_diff"
        elif title=="" and data_type=="chan58":
            filename=f"\\carpet_ch58_shaft_water_rise"
        fig.write_image(r"C:\Users\Mathis\Desktop\Masterthesis\Masterthesis_tex\figs\chap4" + filename + ".pdf",width=1120, height=500)
        fig.write_image(r"C:\Users\Mathis\Desktop\Masterthesis\Masterthesis_tex\figs_raster\chap4" + filename + ".png",width=1120, height=500)
    
    fig.show()

    print(f"fitted water level rise: {round(m_year,1)} m / year") #global sea level rise 1900 to 2017: 1.4–1.8 mm per year
    print(f"this is a total of {round(m_measurement_time,1)} m in the measurement time")

def create_mask_egrt(dataframe,start_date_string="13.07.2021",end_date_string="23.07.2021",find_nearest_date=find_nearest_date):
    """create mask which contains True if not a EGRT date.
    Can also be used to create other masks.
    
    Date strings are converted with dayfirst=True"""
    if type(start_date_string) == str:
        date_start=pd.to_datetime(start_date_string,dayfirst=True)
        date_end  =pd.to_datetime(end_date_string,dayfirst=True)
    else:
        date_start=start_date_string
        date_end  =end_date_string

    date_name_start,date_iloc_start=find_nearest_date(date_start,dataframe.index)
    date_name_end,date_iloc_end=find_nearest_date(date_end,dataframe.index)
    egrt_dates=dataframe.index[date_iloc_start:date_iloc_end]

    mask_not_egrt=[False if x in egrt_dates else True for x in dataframe.index]

    # flipping the list
    mask_egrt=[not elem for elem in mask_not_egrt]
    return mask_not_egrt

def calc_mean_channels_n_pday(n_meas_pday_20xx_with0, channels, check_dates_equal=True):
    """calculate the number of measurements as mean over the 4 channels
    check_dates_equal=True only works for Alsdorf data at the moment
    """
    val={}
    date={}
    for channel in channels:
        val[channel]=np.array(list(n_meas_pday_20xx_with0[channel].values()))
        date[channel]=pd.to_datetime(list(n_meas_pday_20xx_with0["1"]))

    #mean measurements per day
    summe=val[channels[0]]
    for channel in channels[1:]:
        summe=summe + val[channel]
    mean=summe/len(channels)

    # # check if dates are equal
    if check_dates_equal:
        counter_equal=0
        counter_not_equal=0
        for i in range(len(date["1"])):
            if date["1"][i] == date["2"][i] and date["3"][i] and date["4"][i] and date["5"][i] and date["6"][i] and date["7"][i] and date["8"][i]:
                #print("all dates for mean calculation are equal")
                counter_equal+=1
        else:
            #print("dates for mean calculation are not equal!")
            #print(date_ch1[i]);print(date_ch2[i]);print(date_ch3[i]);print(date_ch4[i])
            counter_not_equal+=1
        if counter_not_equal >= 3: # 31.12. seems to be a problem? Dont know why. Not very important.
            print("check dates")

    #all dates are equal, so I can just return one date
    return mean, date["1"]

