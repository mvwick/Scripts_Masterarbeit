import pandas as pd
import numpy as np
from collections import defaultdict
import pickle


def correct_lienar_trend(dat,linear_trend_correction):
    """
    dat: dic with dataframes of channels, which are the keys
    linear_trend_correction: dic with the same keys as dat, containing the slope of the linear correction in K/m (one value)"""
    linear_trend_corrected_df={}
    for chan in dat.keys():
        correction_values_array=np.array(dat[chan].columns) * linear_trend_correction[chan]
        correction_values_list=correction_values_array.tolist()
        correction_2d_list=[]
        for i in range(len(dat[chan].index)):
            correction_2d_list.append(correction_values_list)

        correction_df=pd.DataFrame(data=correction_2d_list, index=dat[chan].index,columns=dat[chan].columns)

        linear_trend_corrected_df[chan] = round(dat[chan] + correction_df,2)
    
    return linear_trend_corrected_df
