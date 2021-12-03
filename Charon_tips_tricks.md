# Charon3 and Charon4 tips and tricks
Currently Charon4 is in use.
I learned how to use the software mainly from the manuals and try / error. 
Therefore my understanding and this document are far from perfect. 
But this document maybe is a good start when working the first time with Charon3.
However my main (unnecessary) advice would be reading the operational and installation manual.
The most important manuals are in ``sciebo\DTS Data\Miscellaneous\Masterthesis_Mathis\Literatur\Manuals``.
They are from the Charon software discs.

**Log In information:** ``sciebo\DTS Data\Log-In_DTS_devices_software.docx``

## Export raw data - Stokes and anti-Stokes
The company does not support the export of the raw data (Stokes and anti-Stokes).
However, on the old PC of Mario in the institute an export using Charon3 is possible.
I did not find the installer for this Charon version.
Requesting one from the company was not successfully, they said it must have been a mistake the the institute even has a version which can export these.
Usually this is only possible with internal versions.

## General Tips
You have to select the items you want to interact with. 
For example if you click on a channel / device you have different options for example in the device tab.
Another example would be selecting a data curve / plot, while selected you can export these data.

If you double-click in a data point in the temperature plot, the temperature at this position over a the whole time is displayed.

## Repeated Workflow
The support information should be generated once per year (stated in manual).
Data on the device should be downloaded and deleted in regular timesteps (to avoid a full data storage of the device).
Data should be exported and saved on a server or somehow backuped regulary (to avoid data loss and free disk space).


## Connection Problems
I have the feeling a Ethernet connection between DTS device and PC is better than USB.
With USB the download crashed sometimes, so I always prefer using the Ethernet connection.

Unplug the Ethernet connection, plug in USB (*wait*) and then Ethernet again sometimes worked.

### No connection via Ethernet - solution
I had problems creating the connection via Ethernet.
My problem was toi set the IP address properly.
I only did that using Charon4.
From the following
* chapter 4.1.1 of ``sciebo\DTS Data\Miscellaneous\Masterthesis_Mathis\Literatur\Manuals\Charon4 - Operation Manual OTS3.pdf``
* [what is ip adress and subnet mask](https://community.fs.com/de/blog/know-ip-address-and-subnet-mask.html)

I concluded this settings ``sciebo`\DTS Data\EONERC\Screenshot\screenshots_during_connection_problems\working_network_settings_of_controller.png``.
Via USB the network settings can be changed.
Unplug the usb and plug in Ethernet, if it is set up properly the connection is established.
**Important:** The secondary Ethernet has to be disabled (*Disable Ethernet Interface*).
I dont know how a secondary Ethernet is implemented correctly, didnt need it.

### Controller switches between yellow (Connection Fault) and normal
In Alsdorf I could solve this by removing the usb connection.
Before the Laptop was connected to the DTS device via USB and Ethernet.
I think Charon4 was confused by that.
In Charon3 this was not a problem

## Temperature Calibration
You can only do this if no measurements (at the device) are running --> Stop Measurements

# Charon4
See [Readme](./README.md#scripts_masterarbeit) for some workflows with Charon4

# Charon3
## Program - Speicherort Daten
Ich denke das Program speichert intern die Daten in ``C:\OTSData\C3\DB``. Falls das stimmt, sind die dort aber in einem anderen Format gespeichert (nicht ``.mex`` oder ``.txt``). Noch nicht getestet, ob man den Ordner einfach in eine andere Installation kopieren kann.

## Work with databases
View > Measurement Explorer; new window opens with all the databases

### merge multiple databases
* click on ```+`` of one database
* right click any and select ``select and merge controll data``, at the bottom
* new window opens where you can select the databases which should be merged
* Warning: You will only have the merged databse after that

### import *.mex
1. click top left charon icon
2. select import
3. select all the ``*.mex`` files aou want to import
     * maybe you want to [merge multiple databases](#merge-multiple-databases) after you imported them

### export data
#### export as *txt
These are the steps you need to do, if you want to export the data as ``.txt`` file. 
1. open measurement explorer: View > Measurement Explorer; new window opens with all the databases
   * eventually you want to [merge multiple databases](#merge-multiple-databases) before proceeding.
2. select the database you want to export something of. click on ``+``, two times
3. select the channel you want to export
4. select the data of the channel you want to export (main window to the right)
5. right click ``open``, make sure the new appeared window is your selected window
6. click on the charon icon on the top left
7. export > measurement data (*.txt)
    * this only exports the selected window. So you should put the channel name and the type of data in the dataname, e.g. ``ch1_temp_datefrom_dateto.txt``
#### export as .mex
This exports a complete database in the ``.mex`` format. This can only be opened with a Charon3 software.
I think this should be rather used for exchanging the data between different PCs.
1. open measurement explorer: View > Measurement Explorer; new window opens with all the databases
   * eventually you want to [merge multiple databases](#merge-multiple-databases) before proceeding.
2. right click the database you want to export and select export

## Displayed data belongs to earlier measurement - black square red dot
Message in plots in the Charon3 software. On the top left appears a black square with a red dot in it, when hovering over it the message appears.

I think the message describes the following effect. When changing the time of a the plot with the bar at the bottom, the time in all plots changes.
All channels are measured after each other, so the different channels measure their data at different timestamps.
When changing the time with the bar at the bottom, you click through all possible timestamps, but some channels dont have data corresponding to this timestamp.
For these channels earlier measured data is plotted. 
Exactly speaking the earlier timestamp with data available for this channel is plotted, but in the plot is written a different timestamp.

