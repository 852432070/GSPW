# GSPW
This project provide a sensing platform for IMU on wrist via UDP.

* Show imu data on terminal in real time. (Mode 0)
* Track and record a User and an Activity in a file. (Mode 1)
* Track and inference on neural network. (Mode 2)

usage: python GSPW.py [-h] --mode M [--activity_id A] [--user_id U] [--duration D]

optional arguments:
  -h, --help       show this help message and exit
  --mode M         choose a mode
  --activity_id A  activity id
  --user_id U      user id
  --duration D     duration of the logging mode


  ## GUI version
  All modes in cmd version are achieved in gui version.
  
  usage: python GSPW_gui.py