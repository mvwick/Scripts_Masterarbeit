from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, rfft, rfftfreq, irfft
import numpy as np


def resample_data_func(data,resample_hours=5):
    """"resample data for fourier analysis"""
    data_resample=data.resample(timedelta(hours=resample_hours)).mean()
    data_resample=round(data_resample,1)

    sampling_time=resample_hours*60*60 #[s]
    sampling_rate=1/sampling_time
    Duration=(data_resample.index.max()-data_resample.index.min()).total_seconds()
    N_samples=sampling_rate * Duration

    return data_resample, sampling_time

def fourier_transform(data_resample, sampling_time):
    """"""
    # Fourier transformation
    yf=rfft(data_resample.values) 
    xf=rfftfreq(len(data_resample.index),sampling_time)

    return yf, xf

def plot_frequency_spectrum(xf, yf, vlines, vlines_labels, ylim=[0,200]):
    """"""
    vlines_colors=["green","red","pruple","orange"]
    # 1 day fluctutation:
    T_day=24*60*60
    f_day=1/T_day
    f_week=1/(T_day*7)
    f_month=1/(T_day*30)

    plt.figure(figsize=(16,4))

    if type(xf)==dict:
        for channel in xf.keys():
            plt.plot(xf[channel],np.abs(yf[channel]), label=f"fourier transform channel {channel}")
    else:
        plt.plot(xf,np.abs(yf), label="fourier transform")

    plt.vlines([f_day],ylim[0],ylim[1],color="black",zorder=10,linewidth=3, alpha=0.3, label="daily variations: 1/24 $h^{-1}$")
    plt.vlines([f_week],ylim[0],ylim[1],color="black",linestyle="--",linewidth=3,zorder=10, alpha=0.3, label="weekly variations: 1/7 $d^{-1}$")
    plt.vlines([f_month],ylim[0],ylim[1],color="black",linestyle=":",linewidth=3,zorder=10, alpha=0.3, label="monthly variations: 1/4 $w^{-1}$")
    label_counter=0
    for vline in vlines:
        plt.vlines(vline,ylim[0],ylim[1],zorder=10, alpha=0.5, label=vlines_labels[label_counter], color=vlines_colors[label_counter])
        label_counter+=1
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Absolute Amplitute [°C]")
    plt.ylim(ylim)
    plt.xlim(left=0)
    #plt.title("Frequency Spectrum")
    legend = plt.legend(fontsize=11, title_fontsize=11,frameon=True)
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.7)
