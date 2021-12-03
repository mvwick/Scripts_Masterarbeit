from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, rfft, rfftfreq, irfft
import numpy as np
from copy import deepcopy#, copy
import plotly
import plotly.express as px
import kaleido
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def resample_data_func(data,resample_hours=5):
    """"resample data for fourier analysis"""
    data_resample=data.resample(timedelta(hours=resample_hours)).mean()
    data_resample=round(data_resample,1)

    sampling_time=resample_hours*60*60 #[s]
    sampling_rate=1/sampling_time
    Duration=(data_resample.index.max()-data_resample.index.min()).total_seconds()
    N_samples=sampling_rate * Duration

    # Calc Nyquist frequency
    abtast_frequency=1/sampling_time #[Hz] #=sampling_rate
    #all frequncies of signal have to be smaller than nyquist frequncy, otherwise alliasing
    nyquist_frequency=0.5*abtast_frequency

    return data_resample, sampling_time, nyquist_frequency

def fourier_transform(data_resample, sampling_time, return_abs=False):
    """"""
    # shifting the values of data_resample to a mean of zero only affects the lowest frequency
    # so it seems to not be very important that the signals mean is 0

    # Fourier transformation
    yf=rfft(data_resample.values) 
    xf=rfftfreq(len(data_resample.index),sampling_time)

    if return_abs:
        yf=np.abs(yf)

    return yf, xf

def plot_frequency_spectrum(xf, yf, vlines, vlines_labels,nyquist_frequency, ylim=[0,40]):
    """x is expected to be in Hz"""
    vlines_colors=["green","red","pruple","orange"]
    # 1 day fluctutation:
    T_day=24*60*60*10**(-6) #mikro seconds
    f_12h=1/(T_day/2)
    f_day=1/T_day
    f_week=1/(T_day*7)
    f_month=1/(T_day*30)

    plt.figure(figsize=(16,4))

    # *10**6 convert xf to mikro Hz
    if type(xf)==dict:
        for channel in xf.keys():
            plt.plot(xf[channel]*10**6,np.abs(yf[channel]), label=f"fourier transform channel {channel}")
    else:
        plt.plot(xf*10**6,np.abs(yf), label="fourier transform")

    plt.vlines([f_12h],ylim[0],ylim[1],color="black",linestyle="dashdot",zorder=10,linewidth=3, alpha=0.3, label="half-day variations: 1/12 $h^{-1}$")
    plt.vlines([f_day],ylim[0],ylim[1],color="black",zorder=10,linewidth=3, alpha=0.3, label="daily variations: 1/24 $h^{-1}$")
    plt.vlines([f_week],ylim[0],ylim[1],color="black",linestyle="--",linewidth=3,zorder=10, alpha=0.3, label="weekly variations: 1/7 $d^{-1}$")
    plt.vlines([f_month],ylim[0],ylim[1],color="black",linestyle=":",linewidth=3,zorder=10, alpha=0.3, label="monthly variations: 1/4 $w^{-1}$")
    plt.vlines([nyquist_frequency*10**6],ylim[0],ylim[1],color="black",linestyle="solid",linewidth=1,zorder=1, alpha=1, label="Nyquist frequency")
    
    label_counter=0
    for vline in vlines:
        plt.vlines(vline,ylim[0],ylim[1],zorder=10, alpha=0.5, label=vlines_labels[label_counter], color=vlines_colors[label_counter])
        label_counter+=1
    plt.xlabel("Frequency [\u03BCHz]")
    plt.ylabel("Absolute Amplitute [K]")
    plt.ylim(ylim)
    plt.xlim(left=0)
    #plt.title("Frequency Spectrum")
    legend = plt.legend(fontsize=11, title_fontsize=11,frameon=True)
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.7)

# Carpet plot

def calc_fourier_carpet_data(data_input,channels=["5and6","7and8"],drop_egrt_dates=True,resample_hours=5):
    """"""
    yf={}; xf={}; df_yf={};df_xf={}

    for channel in channels:
        data=data_input[channel]
        yf[channel]=pd.DataFrame(columns=data.columns)
        xf[channel]=pd.DataFrame(columns=data.columns)
        data_resample=0; sampling_time=0#clear variables which are used later
        for cable_length in data.columns:
            # Resample data
            data_resample, sampling_time, nyquist_frequqncy = resample_data_func(data[cable_length],resample_hours=resample_hours)
            if channel in ["5","6","5and6"]:
                # Remove date gaps, meaning delete points so neighbaring points are atleast similar in time of day
                bool_no_data=data_resample.notna() == False
                bool_data=data_resample.notna()

                # data gaps fits already good
                data_resample=data_resample[bool_data]

                # Check if everything is as expected with this code
                # diff=data_resample[bool_data].index[1:] - data_resample[bool_data].index[:-1]
                # diff.sort_values() #diff should be all around 5 h, ignoring full days
                # # diff.get_loc(diff.sort_values()[-1])

            if drop_egrt_dates:
                if channel in ["7","8","7and8"]: # check if increased frequency even in shaft are from EGRT
                    #drop EGRT dates
                    data_resample=data_resample.drop(data_resample.index[190:248])

            # Fourier Transform
            if len(data_resample.index) == 0: #if one columns contains only nan values
                #!!not optimal!! assumes this column does not have nan
                yf[channel][cable_length]=np.ones(len(xf[channel][data.columns[0]]))*np.nan
                xf[channel][cable_length]=deepcopy(xf[channel][data.columns[0]]) 
            else:
                yf[channel][cable_length], xf[channel][cable_length] = fourier_transform(data_resample, sampling_time, return_abs=True)

        #put results in dataframe
        df_yf[channel]=pd.DataFrame(yf[channel])
        df_yf[channel].columns.names=["Length [m]"]
        df_xf[channel]=pd.DataFrame(xf[channel])
        df_xf[channel].columns.names=["Length [m]"]

        # check results and simplify
        columns_equal=True
        col_1st=df_xf[channel].columns[0]
        for column in df_xf[channel].columns[1:]: #check if first columns equals all other columns
            if (df_xf[channel][col_1st] == df_xf[channel][column]).all():
                pass
            else:
                columns_equal=False
                print("Error: time span of depth is different to others")
                print(f"{column}")

        if columns_equal==True:
            xf=df_xf[channel][col_1st]
            df_yf[channel].index=(xf*10**(6)).round(2)
            df_yf[channel].index.names=["Frequency [mikro Hz]"]
            if channel not in ["5and6","7and8"]:
                df_yf[channel]=df_yf[channel].astype(int)
            else:
                df_yf[channel]=df_yf[channel].round(0) #astype doesnt work for nans; want to keep all columns for plot
    
    return df_yf

def plot_fourier_carpet(data,channel,mastertheseis_save=False,zmin=0,zmax=20):
    """put in the result of calc_fourier_carpet_data()"""
    trace1=go.Heatmap(
        x=data.index,
        y=data.columns,
        z=data.transpose(),
        name=f"Fourier Amplitude",
        yaxis='y',zmin=zmin,zmax=zmax,colorbar={"title":f"Amp. [K]"},)

    #frequency lines as reference
    T_day=24*60*60
    f_12h=1/(T_day/2)
    f_day=1/T_day
    f_week=1/(T_day*7)
    f_month=1/(T_day*30)

    # hex_color if you want to use different transperency (alpha)
    def hex_to_rgba(h, alpha):
        '''
        converts color value in hex format to rgba format with alpha transparency
        '''
        return tuple([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)] + [alpha])

    hex_color="#808080" #grey
    color='rgba' + str(hex_to_rgba(h=hex_color,alpha=1))

    # Make plot
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(trace1,row=1, col=1)
    # color="gray"
    width=10

    # y0 y1 does not work with pdf save ...
    # seems to be a bug: y positions are measured from 0 to 1 in graph during save,
    # in normal plot they are measures at y axis
    if mastertheseis_save==False:
        if channel=="5and6":
            y0_0=0;y1_0=500;y0_1=1200;y1_1=1800;wekkly_anno_pos=200
        elif channel=="7and8":
            y0_0=0;y1_0=500;y0_1=1200;y1_1=2200;y0_2=2920;y1_2=3700;wekkly_anno_pos=200
        elif channel in ["1","2","3","4","mean_all"]:
            y0_0=0;y1_0=180;wekkly_anno_pos=0.9
    elif mastertheseis_save==True:
        if channel=="5and6":
            y0_0=0.72;y1_0=1;y0_1=0;y1_1=0.28;  wekkly_anno_pos=0.9
        elif channel=="7and8":
            y0_0=0.86;y1_0=1;y0_1=0.36;y1_1=0.64;y0_2=0;y1_2=0.13;  wekkly_anno_pos=0.9
        elif channel in ["1","2","3","4","mean_all"]:
            y0_0=0.8;y1_0=1;wekkly_anno_pos=0.9

    #daily
    fig.add_vline(x=f_day*10**6, line_width=width, line_dash="solid", line_color=color,
            y0=y0_0,y1=y1_0, #does not work with pdf save
            annotation_text="daily variation",annotation={"font_size":13,"bgcolor":"white"},row=1, col=1) # annotation_position="top right"
    # half day
    fig.add_vline(x=f_12h*10**6, line_width=width, line_dash="solid", line_color=color,
            y0=y0_0,y1=y1_0,#does not work with pdf save
            annotation_text="half-day variation", annotation_position="top right",annotation={"font_size":13,"bgcolor":"white"},row=1, col=1)
    # weekly
    fig.add_vline(x=f_week*10**6, line_width=width, line_dash="solid", line_color=color,
            y0=y0_0,y1=y1_0,#does not work with pdf save
            annotation_text="weekly variation",annotation={"font_size":13,"bgcolor":"white","y":wekkly_anno_pos},row=1, col=1) # #annotation_position="top right"
    #monthly
    fig.add_vline(x=f_month*10**6, line_width=width, line_dash="solid", line_color=color,
            y0=y0_0,y1=y1_0,#does not work with pdf save
            annotation_text="monthly variation", annotation_position="top right",annotation={"font_size":13,"bgcolor":"white"},row=1, col=1)

    if channel in ["5and6", "7and8"]:
        fig.add_vline(x=f_day*10**6, line_width=width, line_dash="solid", line_color=color,row=1, col=1,
                    y0=y0_1,y1=y1_1,#does not work with pdf save
                    )#daily
        fig.add_vline(x=f_12h*10**6, line_width=width, line_dash="solid", line_color=color,row=1, col=1,
                    y0=y0_1,y1=y1_1,#does not work with pdf save
                    )# half day
        fig.add_vline(x=f_week*10**6, line_width=width, line_dash="solid", line_color=color,row=1, col=1,
                    y0=y0_1,y1=y1_1,#does not work with pdf save
                    )# weekly
        fig.add_vline(x=f_month*10**6, line_width=width, line_dash="solid", line_color=color,row=1, col=1,
                    y0=y0_1,y1=y1_1,#does not work with pdf save
                    )#monthly

    if channel =="7and8":
        fig.add_vline(x=f_day*10**6, line_width=width, line_dash="solid", line_color=color,row=1, col=1,
        y0=y0_2,y1=y1_2,#does not work with pdf save
        ) #daily
        fig.add_vline(x=f_12h*10**6, line_width=width, line_dash="solid", line_color=color,row=1, col=1,
        y0=y0_2,y1=y1_2,#does not work with pdf save
        )# half day
        fig.add_vline(x=f_week*10**6, line_width=width, line_dash="solid", line_color=color,row=1, col=1,
        y0=y0_2,y1=y1_2,#does not work with pdf save
        )# weekly
        fig.add_vline(x=f_month*10**6, line_width=width, line_dash="solid", line_color=color,row=1, col=1,
        y0=y0_2,y1=y1_2,#does not work with pdf save
        )#monthly

    fig.update_layout(yaxis = {"title":"Length [m]"},xaxis={"title":"Frequency [\u03BCHz]"},
                        legend={"x":0.005,"y":0.85,"traceorder":"normal","font":{"size":11,"color":"black"},"orientation":"h","xanchor":"left","yanchor":"bottom"},showlegend=True)
    fig.update_yaxes(range=[data.columns[-1], 0], row=1, col=1)

    if mastertheseis_save:
        if channel in ["7and8","mean_all"]:
            if channel=="7and8":
                data_type=78
                filename=f"\\fourier_carpet_ch{data_type}"
            elif channel=="mean_all":
                data_type=14
                filename=f"\\fourier_carpet_ch{data_type}"
            fig.write_image(r"C:\Users\Mathis\Desktop\Masterthesis\Masterthesis_tex\figs\chap4" + filename + ".pdf",width=1120, height=500)
            fig.write_image(r"C:\Users\Mathis\Desktop\Masterthesis\Masterthesis_tex\figs_raster\chap4" + filename + ".png",width=1120, height=500)
        elif channel == "5and6":
            data_type=56
            filename=f"\\fourier_carpet_ch{data_type}"
            fig.write_image(r"C:\Users\Mathis\Desktop\Masterthesis\Masterthesis_tex\appendix" + filename + ".pdf",width=1120, height=500)
            fig.write_image(r"C:\Users\Mathis\Desktop\Masterthesis\Masterthesis_tex\appendix_raster" + filename + ".png",width=1120, height=500)

    fig.show()
