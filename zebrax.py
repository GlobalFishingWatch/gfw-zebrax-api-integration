####################################################################
##  ZebraX tracking device API Call Functions written in Python    #
##  By. Imam Prakoso (imam@globalfishingwatch.org)                 #
##  Dec 2020                                                       #
####################################################################

import pycurl
import certifi
import datetime
import time
import json
from io import BytesIO
import pandas as pd

#API: login
#purpose: to get token string that is used in API call
#parameters: username and password
#testing: 
#get_token test
#auth_token = get_token(<username>,<password>)

def get_token(username,password,verbose=False):
  url = 'https://thingsbox.zebrax.io/api/auth/login'
  data = json.dumps({"username":username,"password":password}) 
  b_obj = BytesIO()
  ch = pycurl.Curl()
  ch.setopt(ch.URL, url)
  ch.setopt(ch.HTTPHEADER, ['Accept: application/json']) 
  ch.setopt(ch.POST,1)
  ch.setopt(ch.SSL_VERIFYPEER,0)
  ch.setopt(ch.POSTFIELDS,data)
  ch.setopt(ch.VERBOSE,verbose)
  ch.setopt(ch.WRITEDATA,b_obj)
  ch.perform()
  ch.close()
  get_body = b_obj.getvalue()
  return get_body.decode('utf8')

#API: devices
#purpose: to get list of devices
#parameters: 
#(1) page: devices list is segmented into pages. page index starts from 0 
#(2) pageSize: how many devices we will get in an API call. Each page can contain maximum 100 devices or size
#testing: 
#auth_token = get_token(<username>, <password>)
#token = json.loads(auth_token)
#token = token['token']
#devices = get_devices(token,0,50,True) #this will get 50 devices from page-0.

def get_devices(token,page,pagesize,verbose=False):
  url = 'https://thingsbox.zebrax.io/api/tenant/devices?page=' + str(page) + '&pageSize=' + str(pagesize);
  b_obj = BytesIO()
  ch = pycurl.Curl()
  ch.setopt(ch.URL,url)
  ch.setopt(ch.HTTPHEADER,['X-Authorization: Bearer ' + token, 'Accept: application/json'])
  ch.setopt(ch.POST,0)
  ch.setopt(ch.SSL_VERIFYPEER,0)
  ch.setopt(ch.VERBOSE,verbose)
  ch.setopt(ch.WRITEDATA,b_obj)
  ch.perform()
  ch.close()
  get_body = b_obj.getvalue()
  return get_body.decode('utf8')
  
#API: get device keys
#purpose: to get all keys of a device. Keys are similar attributes or parameters of the devices.
#parameters: 
#(1) Entity Type: DEVICE
#(2) device ID: device ID that we want to get its attributes.
#testing: 
#auth_token = get_token(<username>, <password>)
#token = json.loads(auth_token)
#token = token['token']
#attributes = get_device_keys(token,'DEVICE','88d1e0d0-33e7-11eb-891e-b1085e72b112'); 

def get_device_keys(token,entitytype,deviceid,verbose=False):
  url = 'https://thingsbox.zebrax.io/api/plugins/telemetry/' + entitytype + '/' + deviceid + '/keys/timeseries'
  b_obj = BytesIO()
  ch = pycurl.Curl()
  ch.setopt(ch.URL,url)
  ch.setopt(ch.HTTPHEADER,['X-Authorization: Bearer ' + token, 'Accept: application/json'])
  ch.setopt(ch.POST,0)
  ch.setopt(ch.SSL_VERIFYPEER,0)
  ch.setopt(ch.VERBOSE,verbose)
  ch.setopt(ch.WRITEDATA,b_obj)
  ch.perform()
  ch.close()
  get_body = b_obj.getvalue()
  return get_body.decode('utf8')

#API: get telemetry data
#purpose: to get data from a device in a specific time range
#parameters: 
#(1) Entity Type: DEVICE
#(2) device ID
#(3) keys, separated by comma. for example: "latitude","longitude","speed","direction","battery_level","gps_interval"
#(4) start timestamp and end timestamp in UNIX timestamp
#testing:
#auth_token = get_token(<username>, <password>)
#token = json.loads(auth_token)
#token = token['token']
#keys = 'longitude,latitude,speed,direction,battery_level,gps_interval'
#data = get_telemetry_data(token,'DEVICE','2e205e60-33e6-11eb-891e-b1085e72b112','2020-12-06 00:00:00','2020-12-06 23:59:59',keys)
#print(data)
 
def get_telemetry_data(token,entitytype,deviceid,starttime,endtime,keys,limit=1000,verbose=False):
  start = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
  unixstart = str(round(time.mktime(start.timetuple()))) + '000'
  end = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')
  unixend = str(round(time.mktime(end.timetuple()))) + '000'
  limit = str(limit)
  url = 'https://thingsbox.zebrax.io/api/plugins/telemetry/' + entitytype + '/' + deviceid + '/values/timeseries?limit=' + limit + '&keys=' + keys + '&startTs=' + unixstart + '&endTs=' + unixend
  b_obj = BytesIO()
  ch = pycurl.Curl()
  ch.setopt(ch.URL,url)
  ch.setopt(ch.HTTPHEADER,['X-Authorization: Bearer ' + token, 'Accept: application/json'])
  ch.setopt(ch.POST,0)
  ch.setopt(ch.SSL_VERIFYPEER,0)
  ch.setopt(ch.VERBOSE,verbose)
  ch.setopt(ch.WRITEDATA,b_obj)
  ch.perform()
  ch.close()
  get_body = b_obj.getvalue()
  return get_body.decode('utf8')

def export_all_devices(token, page, number_of_devices=100):
  devices = get_devices(token,page,number_of_devices,False)
  f_dev = open('dev.json','w');
  f_dev.write(devices)
  f_dev.close()
  df_dev = pd.read_json('dev.json');
  df_dev = df_dev['data']
  dfx = pd.DataFrame()
  for colname,data in df_dev.items():
    df_tmp = pd.json_normalize(data)
    dfx = dfx.append(df_tmp)
  dfx.sort_values(by=['name'])
  dfx.to_csv('devices.csv', index=False)
  print("Export Done. Check devices.csv")

def export_device_telemetry(token,deviceid,devicename,starttime,endtime,limit=1000):
  print('Exporting ' + devicename + ' telemetry data')
  keys = 'longitude,latitude,speed,direction,battery_level,gps_interval'
  track = get_telemetry_data(token,'DEVICE',deviceid,starttime,endtime,keys)
  tj = json.loads(track)
  if track == '{}':
    return None
  df_lon = pd.DataFrame(tj['longitude']).sort_values(by=['ts'])
  df_lon.columns = ['ts','lon']
  df_lat = pd.DataFrame(tj['latitude']).sort_values(by=['ts'])
  df_lat.columns = ['ts','lat']
  df_lat = df_lat['lat']
  df_speed = pd.DataFrame(tj['speed']).sort_values(by=['ts'])
  df_speed.columns = ['ts','speed']
  df_speed = df_speed['speed']
  df_course = pd.DataFrame(tj['direction']).sort_values(by=['ts'])
  df_course.columns = ['ts','direction']
  df_course = df_course['direction']
  df_bat = pd.DataFrame(tj['battery_level']).sort_values(by=['ts'])
  df_bat.columns = ['ts','battery_level']
  df_bat = df_bat['battery_level']
  df_gps = pd.DataFrame(tj['gps_interval']).sort_values(by=['ts'])
  df_gps.columns = ['ts','gps_interval']
  df_gps = df_gps['gps_interval']
  series_timestamp = df_lon['ts'].map(lambda x:datetime.datetime.utcfromtimestamp(x/1000).strftime('%Y-%m-%d %H:%M:%S'), na_action='ignore')
  df_timestamp = pd.DataFrame(series_timestamp)
  df_timestamp.columns = ['timestamp']
  df_lon = df_lon['lon']
  frames = [df_timestamp,df_lon,df_lat,df_speed,df_course,df_bat,df_gps]
  df_track = pd.concat(frames, join='outer', axis=1)
  df_track['device_id'] = deviceid
  df_track['device_name'] = devicename
  df_track.assign(timestamp = df_timestamp)
  return df_track

# function: zebrax_export_data  
# purpose: to fetch all telemetry data of all devices listed in a csv file. by default,
# it reads devices.csv as device list by default. This csv at least has information of device id and device name.
# output: zebrax_track.csv

def zebrax_export_data(username,password,date_from,date_to,list_of_device=None):
  auth_token = get_token(username,password)
  token = json.loads(auth_token)
  token = token['token']
  if not list_of_device:
    export_all_devices(token,0,100)
    list_of_device = 'devices.csv'
  df_devices = pd.read_csv(list_of_device)
  df_all_track = pd.DataFrame()
  for index,row in df_devices.iterrows():
    devid = row['id.id']
    devname = row['name']
    df_track = export_device_telemetry(token,devid,devname,date_from,date_to) #'2020-12-19 00:00:00','2020-12-19 23:59:59'
    if df_track is not None:
      df_all_track = df_all_track.append(df_track)
  df_all_track.to_csv('zebrax_track.csv')
  print('Zebrax Export Data DONE')


