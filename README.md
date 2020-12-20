# GFW - ZebraX API Integration
---

Updated: 2020-12-20

This repo contains files and scripts that are useful for fetching tracking data that is produced by ZebraX tracking devices through API call. `zebrax.py` contains basic functions that implement all features of API call provided by ZebraX.

## ZebraX
---
ZebraX is a company in Indonesia that produces IoT service and hardware. GFW uses tracking device from this company and obtains data that is produced by the them. Those devices are installed on small fishing vessels in Indonesia. They produce location tracking data of small fishing vessels. This data can then be used to improve fishery in the local community.

## zebrax.py
--- 
`zebrax.py` is a library to call ZebraX API that is written in python programming language.

### Authentication
ZebraX API requires token in order to call the API. You can call `get_token` function to get the token with input parameter `username` and `password`. Please contact project coordinator or ZebraX to get the username and password to call the API.

### Device List
This repository initially comes with devices list that is saved in `devices.csv`. This file is used by default to call `zebrax_export_data` function to export all tracks of all devices in a particular timestamp window. Or you can have another list in csv format as the input of devices to `zebrax_export_data` function. This csv has to have at least `id.id` and `name` field. `id.id` is device id where as `name` is device name in ZebraX environment. To refresh `device.csv`, you can call `export_all_devices` function. The devices in ZebraX environment are stored with pagination mechanism. The index of page starts from 0 and is page contains maximum 100 devices. `export_all_devices` need pagination info as input parameter.

### How to export tracking data
`zebrax.py` can be used in any python program by importing it as python library. Export track data can be done by calling `zebrax_export_data` function by providing `username`, `password`, `date_from` and `date_to` as required parameters. `date_from` and `date_to` format is `YYYY-MM-DD HH24:MI_SS`. for example, let's write `main.py`
```Python
### main.py
import zebrax as zx
zx.zebrax_export_data('username','password','2020-12-20 00:00:00','2020-12-20 23:59:59')
```
Another Option, if we have our own device list stored in a particular csv file, let's say `list.csv` the program will look like
```Python
import zebrax as zx
zx.zebrax_export_data('username','password','2020-12-20 00:00:00','2020-12-20 23:59:59','list.csv')
```
`username` and `password` are required as mentioned in Authentication section. Run main.py as a simple python program:
`$> python main.py`
Running this script will produce output file `zebrax_track.csv`. You can then use this output file for pipeline or for producing analysis using GIS.

## System Requirements
---
1. python 3
2. python libraries such as: `pycurl`, `certify`, `datetime`, `time`, `json`, and the most important is `pandas`. If some of libraries are missing, you can install it simply using `pip` command. 


