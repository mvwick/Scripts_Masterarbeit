# -*- coding: utf-8 -*-
"""
Created on Wed May  6 22:07:14 2020

@author: Daniel
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
from matplotlib.animation import FuncAnimation
import mpl_toolkits.axes_grid1
import matplotlib.widgets
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#tickno = 20  # number of labels for imshow-plot
tincol = 1 # selector for fluid plot
toutcol = 2
volcol = 3
dtsmeancol = 4

#%% load and select data
#probe = "Name"
#df1 = pd.read_csv('Data2s_date.csv', delimiter=';')

ch1 = ["temp_ch1_2019.csv", "temp_ch1_2020.csv", "temp_ch1_2021.csv"]
ch2 = ["temp_ch2_2019.csv", "temp_ch2_2020.csv", "temp_ch2_2021.csv"]
ch3 = ["temp_ch3_2019.csv", "temp_ch3_2020.csv", "temp_ch3_2021.csv"]
ch4 = ["temp_ch4_2019.csv", "temp_ch4_2020.csv", "temp_ch4_2021.csv"]
ch5 = ["temp_ch5_2021.csv"]
ch6 = ["temp_ch6_2021.csv"]
ch7 = ["temp_ch7_2021.csv"]
ch8 = ["temp_ch8_2021.csv"]



img = "Ch4.png"
path_to_my_database = r"..\Alsdorf\Daten\my_database" #added by mathis
dff = []
for i in ch4: #ch1 ch2 ch3 ch4 ch5 ch6 ch7 ch8
    df = pd.read_csv(path_to_my_database + "\\csv\\" + i,delimiter = ',',index_col=0, header=0 )
    dff.append(df)
dfa = pd.concat(dff, axis=0)
print(dfa)



#data =  "temp_ch4_2021.csv"
#dfa = pd.read_csv(data, delimiter=',', index_col = 0)

#dfa = dfa.iloc[1410 : 2400, :]

#dfa = dfa.iloc[0:5000,0:100]
dfa.index = pd.to_datetime(dfa.index, dayfirst = True)
#%%
dfa = dfa.resample('h').mean()
#dfa = dfa.resample('h').mean()
#dfa.resample('40M').mean() #.mean().fillna("pad")
#%%
#pd.to_datetime(dfa.index)


#%%
#dfa = dfa.iloc [200 : 1000, :]
#dfa = dfa.reset_index().iloc[:,1:]


#date = dfa.iloc[:,0] #date index
date = dfa.index.to_series()
date_ym = pd.to_datetime(date, dayfirst = True).dt.strftime('%d.%m.%y %H:%M') # Short date index


#%% select dts and fluid data

probe = "Westschacht" #Title plot 1

offset =  -0 #shift depth: 36 Meter für S24, ~3 Meter für S18
tempof =0# -2.06 #Offset Süd = +2.69, Offset Ost = -2.06, Offset West = -2.06

dfa = dfa + tempof
"""
B11 = dfa.iloc[:,170 : 368] 
B12 = dfa.iloc[:, 380 : 595 ] 
B1 = dfa.iloc[:, 628 : 828 ] # 606 : 849 Zuleitung
B3 = dfa.iloc[:, 868 : 1068] #860 : 1080 Zuleitung
B8 = dfa.iloc[:, 1094 :1294 ] #1089 : 1308 Zuleitung, Artefakt bei ~ 1177: 1190
B9 = dfa.iloc[:, 1356 : 1549 ] #1316 : 1555 Zuleitung
B10 = dfa.iloc[:, 1617 : 1817] 
"""
#%% Mittelwert für die Sonden, die in Betrieb sind

#sonden = [B11, B12, B1, B3, B10]
sondendf = dfa#pd.concat(sonden, axis = 1)
sondenmean = sondendf.mean(axis = 1)
#%%


#dfsonfor = dfa.iloc[:, 1094 :1294 ] + tempof  #S8
#dfsonfor = dfa.iloc[:, 1356 : 1549] + tempof  #S9
#dfsonfor = dfa.iloc[:, 1617 : 1817] + tempof  #S10 
#dfsonfor = dfa.iloc[:,  : ] + tempof
#dfsonfor = B12
dfsonfor = dfa.iloc[:] 


dfsonmean = dfsonfor.mean(axis=1)

#%% calculate mean from up and down

dfsoncol = dfsonfor.columns.values[:]
dfsonrev = dfsonfor.iloc[:, ::-1]
dfsonrev.columns = dfsoncol

dfson = (dfsonfor + dfsonrev) / 2
dfson = dfsonfor # plot original data #u.a. wenn nicht einzelne Sonde sondern ganzes Kabel geplottet wird

"""
#%% Betriebs/Fluiddaten einldaen
databetrieb = pd.read_csv('Betriebsdaten_2015_2016a/Data_total_5min_2015_05-2016_03.csv', sep=';', index_col = 0 )
databetrieb.index = pd.to_datetime(databetrieb.index, yearfirst = True, utc = True)
databetrieb = databetrieb.iloc[21300:30820,:]
header = list(databetrieb)

#%%
fluid12 = ["Probe_12_T_in", "Probe_12_T_out", "Probe_12_V_dot"]
fluid28 = ["Probe_28_T_in", "Probe_28_T_out", "Probe_28_V_dot"]
#fluid24 = ["Probe_37_T_in", "Probe_37_T_out", "Probe_37_V_dot"]

# Get Fluid Data from one Probe
fluid = fluid12
dffluid = databetrieb[fluid]

#dftin = [col for col in databetrieb.columns if "T_in" in col]
#dftout = [col for col in databetrieb.columns if "T_out" in col]

# Get Tin / Tout from all Probes or average Temp
dftin = databetrieb.loc[:, databetrieb.columns.str.contains("T_in")]
dftin = dftin.iloc[:,:40]
dftout = databetrieb.loc[:, databetrieb.columns.str.contains("T_out")]
dftout = dftout.iloc[:,:40]
dfvol = databetrieb.loc[:, databetrieb.columns.str.contains("V_dot")]
dfvol = dfvol.iloc[:,:40]


tinmean = dftin.mean(axis=1)
toutmean = dftout.mean(axis=1)
volmean = dfvol.mean(axis=1)
tinoutmean = pd.concat([tinmean, toutmean], axis =1).mean(axis=1)

#%% Only the Probes that are on DTS-West-Channels
dftinw = dftin.loc[:, dftin.columns.str.contains("11|12|01|03|10")]#, "01", "03", "08", "09", "10")]
dftoutw = dftout.loc[:, dftout.columns.str.contains("11|12|01|03|10")]#, "01", "03", "08", "09", "10")]
dfvolw =  dfvol.loc[:, dftout.columns.str.contains("11|12|01|03|10")]#, "01", "03", "08", "09", "10")]
tinmeanw = dftinw.mean(axis=1)
toutmeanw = dftoutw.mean(axis=1)
volmeanw = dfvolw.mean(axis=1)

#print(tinmean)


# Select only probes that are on West-DTS-Channel





#dftin2 = dftin.loc[:, dftin.columns.str.contains("Probe")]

#%% select tin tout vol and concat dataframes (only necessary for animated plot)
"""
"""
dffluid = dfa[fluid]
"""

# merge date index, fluid data and dts data

df1 = pd.concat([date, dfsonmean, dfson], axis = 1)
#df1 = pd.concat([date, dffluid, dfson], axis = 1)

# create index for slider
df1["no"] = np.arange(len(df1)).astype(int)

# select dts-data to plot 
datastart = 5 # Reihe mit Data Start  0-3 sind date & fluid (0 = date, 1-3 = fluid, 4 = dtsmean)
datastop = -1 # Reihe mit Data Stop (letzter Eintrag)

temp1 = df1.iloc[:, datastart :datastop] # entspricht dfson, eigtl überflüssig...


# get min and max for axis
mint = np.nanmin(temp1.values)
maxt = np.nanmax(temp1.values)

tempmin = temp1.min(axis = 0)
tempmax = temp1.max(axis = 0)
tempmean = temp1.mean(axis = 0)
tempstd = temp1.std(axis = 0)



# create depth-numpy based on cols to plot (one entry = one meter)
depth = np.arange(0+offset, len(temp1.columns)+offset, 1)
#depth = np.arange(0, len(temp1.columns)+0.5, 0.5)

# get start and end time
start = df1.iloc[0, -1] # first data entry
end = df1.iloc[-1, -1] # last data entry

start_time = start
end_time = end


#%% make figure
fig = plt.figure(figsize=(13, 8))
plt.tight_layout()

# make subplots

gs = GridSpec(2, 2, width_ratios=[2, 2], height_ratios=[2, 1])



# Temperaturprofil (Hauptplot)
ax1 = fig.add_subplot(gs[0])
#ax1 = plt.subplot2grid((4, 4), (0, 0), rowspan = 3, colspan = 2)
ax1.grid(True, color = '#10366f', alpha = 0.1)
ax1.set_xlabel('DTS-Temperatur [°C]')
ax1.set_ylabel ('DTS-Kabellänge [m]')

"""
# Fluiddaten (unterer Plot)
ax2 = fig.add_subplot(gs[2], sharex = ax1)
#ax2 = plt.subplot2grid((4, 2), (3, 0), rowspan = 1, colspan = 1, sharex = ax1)
ax2.xaxis.grid(True, color = '#10366f', alpha = 0.1)
ax2.set_xlabel('Temperatur [°C]')
ax2.set_ylabel('Durchfluss [l/min]')
ax2.set_ylim(-5,30)
#ax2.yaxis.set_visible(False)
ty = [-100, 350] # y-values for Tin-Tout-Plot
"""


# imshow Temperatur über Tiefe und Zeit als img
titleax3 = 'Temperaturverlauf entlang des DTS-Kabels'

ax3 = fig.add_subplot(gs[1], sharey = ax1)
ax3.set_title(titleax3, fontsize = 10, color = '#1A344A', y = 0.99)
#ax3.set_xlabel('Zeit')
ax3.set_ylabel('DTS-Kabellänge [m]')

# Datum-Ticks auf x-Achse und Farbskala
starti = depth[0]
stopi = depth[-1]


""" # Durch Datetime-Axis ersetzt!
ticks = np.linspace(0, len(dfson)-1, tickno, dtype = int).tolist() #make ticks for x-label
xticker = date_ym.iloc[ticks] # get date-labels
"""
#%%
xax3 = mdates.date2num(date)
xstart = xax3[0]
xstop = xax3[-1]

#%%
ax3.xaxis_date()
date_format = mdates.DateFormatter('%d.%m.%y %H:%M')
ax3.xaxis.set_major_formatter(date_format)

#ax3.tick_params(labelbottom = False)
ax3.tick_params(axis = 'x', labelrotation = 30, labelcolor = 'w')
ax3.grid(color = '#10366f', alpha = 0.1)
caxa = ax3.imshow(dfson.transpose(), interpolation = 'gaussian', extent = [xstart, xstop, stopi, starti],
                 vmin = 5, vmax = 45, cmap = 'nipy_spectral', aspect = 'auto')

#caxa = ax3.imshow(dfson.transpose(), interpolation = 'gaussian', extent = [0, len(dfson), stopi, starti],
#                 vmin = 10, vmax = 20, cmap = 'nipy_spectral', aspect = 'auto')




#ax3.set_xticklabels(xticker, rotation = -30, horizontalalignment = 'left', fontsize = 8.5)
#ax3.set_xticks(ticks)
#ax3.tick_params(axis = 'x', labelbottom = False, labeltop = True)
cbax = fig.add_axes([0.92, 0.42, 0.015, 0.46])
cbar = fig.colorbar(caxa, cax = cbax, orientation = 'vertical', fraction = 0.05, pad = - 0.05)
cbar.set_label('Temp [°C]', rotation = 0, fontsize = 9, labelpad = -20,  y = 1.08)

#cbar = fig.colorbar(cax = cbax, orientation = 'horizontal', fraction = 0.05, pad = - 0.05)



# T-In, T-Out und DTS-Mean als Lineplot gegen die Zeit
titleax4 = 'DTS- und Fluid-Temperaturen \n als Mittelwerte entlang der Sonde'
ax4 = fig.add_subplot(gs[3], sharex = ax3)
ax4.set_title(titleax4, fontsize = 10, color = '#1A344A', y = 0.98)
ax4.grid(color = '#10366f', alpha = 0.1)
ax4.set_ylabel('Temperatur [°C]')
#ax4.set_xticklabels(xticker, rotation = -30,horizontalalignment = 'left', fontsize = 8.5)
#ax4.set_xticks(ticks)
ax4.tick_params(axis = 'x', labelrotation = 30)
ax4.set_ylim(10, 40)

#%%Initial plot

# select the dts data from index no
act_data = df1.loc[df1['no'] == int(20)]
plot_data = act_data.iloc[:, datastart : datastop].transpose()

# select fluid data (two datapoints to make line plot)

tin = pd.concat([act_data.iloc[:,tincol], act_data.iloc[:,tincol]])
tout = pd.concat([act_data.iloc[:,toutcol], act_data.iloc[:,toutcol]])
vol = pd.concat([act_data.iloc[:,volcol], act_data.iloc[:,volcol]])
dtsmean = pd.concat([act_data.iloc[:, dtsmeancol], act_data.iloc[:, dtsmeancol]])
#act_data = df1.loc[df1['no'] == int(start)]
#plot_data = act_data.iloc[:, 7:-1].transpose()

#s, is Temp profile, sa and sb Tin and Tout
label_1 = 'DTS-Temperatur'
#s, = ax1.plot(plot_data, depth, color='#10366f', alpha=1, label = label_1)
#sa, = ax1.plot(tin, ty, color='blue', alpha = 0.2 )
#sb, = ax1.plot(tin, ty, color='red', alpha = 0.2 )
ax1.invert_yaxis()

title_1  =  'Temperatur ' +str(probe) +' [°C] \n ' + str(act_data.iloc[0, 0] )
#title_1  =  'Zeitlich gemittelte DTS-Temperatur \n des ' +str(probe)+'s im Juli und August 2015)' #+' [°C]'#' \n ' 
title_1  =  'Statistik des Temperaturverlaufs des DTS-Kabels' #+' [°C]'#' \n ' 
ax1.set_title(title_1, fontsize = 10, color = '#1A344A', y = 0.99)
#ax1.set_xlim(mint - 0.1 * (maxt - mint) , maxt + 0.1 * (maxt - mint))
ax1.set_ylim([(depth.max() + 0.05 * (depth.max()-depth.min())), (depth.min() - 0.05 * (depth.max() - depth.min()))])

#ax1.set_ylim(950,-50)
ax1.set_xlim(5, 40)


#%% show mean std, min and max in background
# T-Mean-Tmin-Tmax from T1

#label_2 = 'DTS-Temperatur Mittelwert [°C]'
label_2 = 'Mittlere \nDTS-Temperatur' 
labelmin = 'Min - Max'
labelstd = 'Standard-Abweichung'
labelerr = 'Messfehler'

ax1.plot(tempmean, depth, color='#10366f', alpha = 0.8, label = label_2)

ax1.fill_betweenx(depth, tempmin, tempmax,
                 #facecolor="blue", # The fill color
                 color='#7fc7ff',       # The outline color
                 alpha=0.3, label = labelmin)          # Transparency of the fill
ax1.fill_betweenx(depth, tempmean - tempstd, tempmean + tempstd,
                # facecolor="#1CB992", # The fill color
                 color="#c52b2f",       # The outline color
                 alpha=0.3, label = labelstd)          # Transparency of the fill
#ax1.fill_betweenx(depth, Sonde_mean_minus_Fehler, Sonde_mean_plus_Fehler,
#                 color="black",       # The outline color
#                 alpha=0.2, label = labelerr)          # Transparency of the fill

#ax1.legend(loc = 'upper left', bbox_to_anchor=(1.1, 1.), bbox_transform=ax1.transAxes)




#%% make second plot for tin, tout and vol
"""
s2, = ax2.plot(tin, ty, color = 'blue', alpha = 0.8, label = 'Tin [°C]')
s3, = ax2.plot(tout, ty, color = 'red', alpha = 0.8, label = 'Tout [°C]')
s4, = ax2.plot(vol, ty, '--', color = 'c', alpha = 0.8, label = 'vol [m³/h]')
s5, = ax2.plot(dtsmean, ty, '--', color = '#a1b9d4', alpha = 0.8, label = 'DTS-Mean')
"""
#ax2.legend(loc = 'upper left', bbox_to_anchor=(1.1, -0.15), bbox_transform=ax1.transAxes)

#s2, = ax2.axvline(x = tin, ymin = 0, ymax = 1, color='#10366f', alpha=1)
#ax1 = plt.subplot2grid((4, 4), (0, 0), rowspan = 3, colspan = 2)



#%% ax4 Plot Tin-Tout-DTS-Mean über Zeit
#a = dffluid.iloc[:,0]
#print(a)
#s6, = ax4.plot(dffluid.iloc[:,0], label = 'Tin', color = 'blue', marker = '|', markersize = 5)
#s7, = ax4.plot(dffluid.iloc[:,1], label = 'Tout', color = 'red', marker = '|', markersize = 5)
#s8, = ax4.plot(dffluid.iloc[:,2], label = 'Vol', color = 'c', marker = '|', markersize = 5, alpha = 0.5)
#s9, = ax4.plot(dfsonmean.rolling(20, center = True).mean(), label = '\u00d8 DTS')
#s9, = ax4.plot(dfsonmean.rolling(3, center = True).mean(), color = '#10366f', alpha = 0.9 ) #label = '\u00d8 DTS', ) # marker = '|', markersize = 5)

s9, = ax4.plot(dfsonmean, color = '#10366f', alpha = 0.9, label = 'DTS-Temperatur') #label = '\u00d8 DTS', ) # marker = '|', markersize = 5)
#sondenmean
#s9, = ax4.plot(sondenmean, color = '#10366f', alpha = 0.9 ) #label = '\u00d8 DTS', ) # marker = '|', markersize = 5)
#s9, = ax4.plot(sondenmean, color = '#10366f', alpha = 0.9, label = 'DTS-Temperatur') #label = '\u00d8 DTS', ) # marker = '|', markersize = 5)
#s10, = ax4.plot(tinmeanw, linestyle = '-', color = 'crimson', alpha = 0.8, label = 'Fluideintritts-Temperatur') # marker = '|', markersize = 5)
#s11, = ax4.plot(toutmeanw, linestyle = '-', color = 'dodgerblue', alpha = 0.8, label = 'Fluidaustritts-Temperatur',) # marker = '|', markersize = 5)
#s12, = ax4.plot(volmeanw, linestyle = ':', color = 'violet', alpha = 0.8, label = '\u00d8 T-Out',) # marker = '|', markersize = 5)

#s12, = ax4.plot(tinoutmean, linestyle = '-.', color = 'yellowgreen', alpha = 0.9, label = '\u00d8 T-In-T-Out', ) # marker = '|', markersize = 5)
#s13 = ax4.plot(dfsonmean, color = 'b', alpha = 0.5, label = '\u00d8 DTS-Mean-gesamte-Kabel')

#pd.concat([act_data.iloc[:, dtsmeancol], act_data.iloc[:, dtsmeancol]])

#fig.canvas.draw()




#%% one legend for all subplots
lines, labels = ax1.get_legend_handles_labels()
#lines2, labels2 = ax2.get_legend_handles_labels()
lines4, labels4 = ax4.get_legend_handles_labels()
#plt.figlegend(lines + lines2, labels + labels2, bbox_to_anchor=(0.71, 0.29), )
#plt.figlegend(lines + lines2 + lines4, labels + labels2 + labels4, bbox_to_anchor=(0.4, 0.3), ncol = 2, facecolor='white', framealpha=1 )
#plt.figlegend(lines + lines4, labels + labels4, bbox_to_anchor=(0.45, 0.25), ncol = 2, facecolor='white', framealpha=1 )
plt.figlegend(lines , labels , bbox_to_anchor=(0.33, 0.35), ncol = 1, facecolor='white', framealpha=1 )
plt.figlegend( lines4, labels4, bbox_to_anchor=(0.35, 0.22), ncol = 1, facecolor='white', framealpha=1 )


#plt.figlegend( lns, labs, loc='upper left', ncol=2, labelspacing=0. )


#plt.set_tight_layout(True)
plt.show()
#img =  'Abbildungen/Zeitschrift_DTS-Temp '+str(probe)+' 2015_2016_v1_neuer_Legendentext'
#plt.savefig(img, dpi = 250)
